import json
import random as rand
from utils.create_map import create_map
from utils.exporter import export_simulation_to_zip
from pipeline import build_pipeline
from utils.init_agents import initialize_agents

def main():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        with open("src/config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

    seed = config.get("seed")
    if seed is not None:
        rand.seed(seed)

    print("🌍 Инициализация мира...")
    grid_size = config.get("grid_size", 100)
    num_agents = config.get("num_agents", 60)
    steps = config.get("steps", 100)
    
    grid = create_map(grid_size)
    
    # Инициализируем агентов с учетом конфига и пайплайна
    agents_map, next_agent_id = initialize_agents(grid, config)

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
        # Контекст для текущего шага
        context = {
            "step": step,
            "grid": grid,
            "agents_map": agents_map,
            "simulation_history": simulation_history,
            "meta": meta,
            # Передаем конфиг для условной логики внутри стратегий
            "enable_trade": config.get("enable_trade", True),
            "enable_reproduction": config.get("enable_reproduction", True),
        }

        # Выполняем пайплайн
        for strategy in pipeline:
            strategy(context)
        
        # Обновляем next_agent_id из meta
        next_agent_id = meta["next_agent_id"]
        
        if step % 10 == 0:
            print(f"⏳ Шаг {step}. Живых агентов: {len(agents_map)}")

    export_simulation_to_zip(simulation_history, grid_size, output_filename="simulation.zip")


if __name__ == "__main__":
    main()
