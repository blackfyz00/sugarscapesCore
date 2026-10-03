import json
import random as rand
from utils.create_map import create_map
from utils.init_agents import initialize_agents
from pipeline import build_pipeline
from core.world import WorldState
from core.agents import AgentSystem

# Импортируем новые модули
from utils.metrics import aggregate_metrics
from utils.plotter import render_charts_from_data
from utils.exporter import save_simulation_archive

def main():
    try:
        with open("./config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        with open("src/config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

    seed = config.get("seed")
    if seed is not None:
        rand.seed(seed)

    print("🌍 Инициализация мира...")
    num_agents = config.get("num_agents", 60)
    grid_size = config.get("grid_size", 100)
    map_file = config.get("map_file", None)
    world = create_map(grid_size, map_file)
    
    steps = config.get("steps", 100)
    
    # Инициализируем агентов через AgentSystem
    agents = AgentSystem(capacity=num_agents * 5)
    from classes import create_agent
    
    next_agent_id = 1
    for _ in range(num_agents):
        placed = False
        while not placed:
            x = rand.randint(0, grid_size - 1)
            y = rand.randint(0, grid_size - 1)
            if world.occupancy[y, x] == -1:
                agent_dict = create_agent(id=next_agent_id, x=x, y=y, config=config)
                agents.spawn(next_agent_id, x, y, agent_dict)
                world.occupancy[y, x] = next_agent_id
                next_agent_id += 1
                placed = True

    # Создаем пайплайн
    pipeline = build_pipeline(config)
    
    # Мета-данные для пайплайна
    meta = {
        "next_agent_id": next_agent_id
    }
    
    simulation_history = []
    
    print(f"🏁 Старт: {num_agents} агентов, {steps} шагов (Seed: {seed})")
    print(f"⚙️ Шагов в пайплайне: {len(pipeline)}")

    for step in range(1, steps + 1):
        context = {
            "step": step,
            "world": world,  # Ссылка на WorldState (NumPy)
            "agents": agents,  # Ссылка на AgentSystem (SoA NumPy)
            "simulation_history": simulation_history,
            "meta": meta,
            "config": config, 
        }

        # Выполняем пайплайн полностью на векторизованных структурах без словарей в горячем цикле
        for strategy in pipeline:
            strategy(context)

        # Обновляем ID
        next_agent_id = meta["next_agent_id"]
        
        if step % 10 == 0:
            alive_count = len(agents.get_alive_indices())
            print(f"⏳ Шаг {step}. Живых агентов: {alive_count}")

    # --- БЛОК АНАЛИТИКИ И ЭКСПОРТА ---
    print("📊 Обработка данных и генерация графиков...")
    
    # 1. Агрегируем метрики из истории
    metrics_data, final_welfares = aggregate_metrics(simulation_history)
    
    # 2. Рисуем графики по полученным данным
    charts = render_charts_from_data(metrics_data, final_welfares)
    
    # 3. Формируем метаданные
    metadata = {
        "total_steps": len(simulation_history),
        "grid_width": grid_size,
        "grid_height": grid_size,
        "seed": seed
    }
    
    # 4. Сохраняем всё в архив с бинарными .npy картами для Godot
    output_path = save_simulation_archive(
        history=simulation_history, 
        charts=charts, 
        metadata=metadata, 
        filename="sim_data.zip",
        world=world
    )
    
if __name__ == "__main__":
    main()
