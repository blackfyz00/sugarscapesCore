import argparse
import json
import sys
import random as rand
from pathlib import Path

script_dir = Path(__file__).parent.resolve()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
    
# Импорты из вашего проекта
from utils.create_map import create_map
from pipeline import build_pipeline
from core.world import WorldState
from core.agents import AgentSystem
from utils.metrics import aggregate_metrics
from utils.plotter import render_charts_from_data
from utils.exporter import save_simulation_archive

if sys.platform == "win32":
    # Принудительно переключаем stdout/stderr на UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    # Устанавливаем переменную окружения для Python
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def parse_args():
    parser = argparse.ArgumentParser(description="Sugarscapes Simulation Core")
    parser.add_argument(
        "--config", 
        type=str, 
        default=None,
        help="Absolute or relative path to config.json"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="sim_data.zip",
        help="Output path for the simulation archive (zip)"
    )
    return parser.parse_args()


def load_config(config_path: str | None) -> dict:
    """Загружает конфиг по явному пути или использует fallback-логику."""
    if config_path:
        path = Path(config_path)
        if not path.exists():
            print(f"❌ Ошибка: Конфиг не найден по пути: {path.resolve()}", file=sys.stderr)
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Fallback для обратной совместимости
    fallback_paths = ["./config.json", "src/config.json"]
    for fp in fallback_paths:
        p = Path(fp)
        if p.exists():
            print(f"ℹ️ Используем конфиг по умолчанию: {p.resolve()}")
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
                
    print("❌ Ошибка: config.json не найден ни по --config, ни в стандартных путях.", file=sys.stderr)
    sys.exit(1)


def main():
    args = parse_args()
    
    try:
        config = load_config(args.config)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON конфига: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неизвестная ошибка при загрузке конфига: {e}", file=sys.stderr)
        sys.exit(1)

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
    agents = AgentSystem(capacity=max(5000, num_agents * 20))
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

    pipeline = build_pipeline(config)
    meta = {"next_agent_id": next_agent_id}
    simulation_history = []

    print(f"🏁 Старт: {num_agents} агентов, {steps} шагов (Seed: {seed})")
    print(f"⚙️ Шагов в пайплайне: {len(pipeline)}")

    try:
        for step in range(1, steps + 1):
            context = {
                "step": step,
                "world": world,
                "agents": agents,
                "simulation_history": simulation_history,
                "meta": meta,
                "config": config,
            }

            for strategy in pipeline:
                strategy(context)

            next_agent_id = meta["next_agent_id"]

            if step % 10 == 0:
                alive_count = len(agents.get_alive_indices())
                print(f"⏳ Шаг {step}. Живых агентов: {alive_count}")

        print("📊 Обработка данных и генерация графиков...")
        metrics_data, final_welfares = aggregate_metrics(simulation_history)
        charts = render_charts_from_data(metrics_data, final_welfares)

        metadata = {
            "total_steps": len(simulation_history),
            "grid_width": grid_size,
            "grid_height": grid_size,
            "seed": seed
        }

        output_path = save_simulation_archive(
            history=simulation_history,
            charts=charts,
            metadata=metadata,
            filename=args.output,
            world=world
        )
        
        print(f"✅ Симуляция успешно завершена. Архив сохранен: {Path(output_path).resolve()}")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Критическая ошибка во время симуляции: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
