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
    """Загружает конфиг ТОЛЬКО по явному пути."""
    if not config_path:
        print("❌ Критическая ошибка: Аргумент --config обязателен при запуске из EXE.", file=sys.stderr)
        sys.exit(1)
    
    path = Path(config_path)
    if not path.exists():
        print(f"❌ Ошибка: Конфиг не найден по указанному пути: {path.resolve()}", file=sys.stderr)
        sys.exit(1)
        
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

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

            # --- БЕЗОПАСНАЯ ДИАГНОСТИКА ПОЗИЦИЙ ---
            # Получаем первых 3 живых индекса
            alive_indices = list(agents.get_alive_indices())[:3]
            
            pos_before = {}
            for idx in alive_indices:
                # Пробуем разные способы доступа к агенту, чтобы не упасть
                ag = None
                if hasattr(agents, 'get_agent'):
                    ag = agents.get_agent(idx)
                elif hasattr(agents, 'agents') and idx in agents.agents:
                    ag = agents.agents[idx]
                elif hasattr(agents, '_data'): # Если данные лежат в словаре _data
                     ag = agents._data.get(idx)
                
                if ag:
                    # Предполагаем, что у агента есть атрибуты x, y
                    px = getattr(ag, 'x', None)
                    py = getattr(ag, 'y', None)
                    if px is not None and py is not None:
                        pos_before[idx] = (px, py)
            # ---------------------------------------

            # ВЫПОЛНЯЕМ ПАЙПЛАЙН
            for strategy in pipeline:
                try:
                    strategy(context)
                except Exception as e:
                    print(f"❌ Ошибка в стратегии {type(strategy)} на шаге {step}: {e}", file=sys.stderr)
                    raise e # Перебрасываем, чтобы остановить симуляцию

            next_agent_id = meta["next_agent_id"]

            # --- СРАВНЕНИЕ ПОСЛЕ ШАГА ---
            if step <= 5 or step % 20 == 0:
                moved_any = False
                log_lines = [f"Step {step}: "]
                
                for idx in alive_indices:
                    if idx not in pos_before: continue
                    
                    ag_after = None
                    if hasattr(agents, 'get_agent'):
                        ag_after = agents.get_agent(idx)
                    elif hasattr(agents, 'agents') and idx in agents.agents:
                        ag_after = agents.agents[idx]
                    
                    if ag_after:
                        old_pos = pos_before[idx]
                        new_pos = (getattr(ag_after, 'x', -999), getattr(ag_after, 'y', -999))
                        
                        status = "MOVED ✅" if old_pos != new_pos else "STUCK ❌"
                        if old_pos != new_pos:
                            moved_any = True
                        
                        log_lines.append(f"Ag{idx}: {old_pos}->{new_pos} ({status}); ")
                
                print("".join(log_lines))
                
                if not moved_any and step == 1:
                     print("⚠️ WARNING: Никто не двинулся на первом шаге!", file=sys.stderr)

            if step % 10 == 0:
                alive_count = len(agents.get_alive_indices())
                print(f"⏳ Шаг {step}. Живых агентов: {alive_count}")

        print("📊 Обработка данных...")
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
