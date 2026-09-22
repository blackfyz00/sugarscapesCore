import random as rand # Добавил импорт, если он нужен для других функций, которые могут быть добавлены
from trade import trade
from move import move
from eat import eat
from findperspectivecell import find_perspective_cell 
from reproduce import reproduce
from get_neighbors import get_neighbors
from regenerate_resources import regenerate_resources
from aging import age_agent
from death import check_and_remove_agent # Импортируем новую функцию

REGISTRY = {}

def register_strategy(name):
    """Декоратор для регистрации стратегии"""
    def decorator(func):
        REGISTRY[name] = func
        return func
    return decorator

@register_strategy("reset_flags")
def reset_flags_strategy(ctx):
    """Сброс флагов торговли"""
    for agent in ctx["agents_map"].values():
        agent["is_trading"] = False

@register_strategy("regeneration_map")
def regeneration_strategy(ctx):
    """Регенерация ресурсов"""
    regenerate_resources(ctx["grid"])

@register_strategy("movement")
def movement_strategy(ctx):
    """Движение агентов"""
    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    
    for agent in list(agents_map.values()):
        if agent["id"] not in agents_map:
            continue
        current_cell = grid[agent["y"]][agent["x"]]
        best_cell = find_perspective_cell(current_cell, grid, agents_map)
        if best_cell:
            move(current_cell, best_cell, agents_map)

@register_strategy("eating")
def eating_strategy(ctx):
    """Потребление ресурсов"""
    grid = ctx["grid"] # Получаем grid из контекста
    agents_map = ctx["agents_map"]
    for row in grid:
        for cell in row:
            eat(cell, agents_map, grid) # Передаем grid в eat

@register_strategy("trading")
def trading_strategy(ctx):
    """Торговля между агентами"""
    if not ctx.get("enable_trade", True): # Проверяем флаг из конфига
        return

    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    step = ctx["step"]
    
    current_agents_list = list(agents_map.values())
    for agent in current_agents_list:
        if agent["id"] not in agents_map:
            continue
            
        current_cell = grid[agent["y"]][agent["x"]]
        neighbors = get_neighbors(current_cell, grid)
        
        for neighbor_cell in neighbors:
            trade(current_cell, neighbor_cell, agents_map, step)

@register_strategy("reproduction")
def reproduction_strategy(ctx):
    """Размножение агентов"""
    if not ctx.get("enable_reproduction", True): # Проверяем флаг из конфига
        return

    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    
    meta = ctx.get("meta", {})
    
    current_agents_list = list(agents_map.values())
    for agent in current_agents_list:
        if agent["id"] not in agents_map:
            continue
            
        current_cell = grid[agent["y"]][agent["x"]]
        neighbors = get_neighbors(current_cell, grid)
        
        for neighbor_cell in neighbors:
            neighbor_agent_id = neighbor_cell.get("agent_id")
            if (neighbor_agent_id and 
                neighbor_agent_id in agents_map and 
                neighbor_agent_id != agent["id"]):
                
                neighbor_agent = agents_map[neighbor_agent_id]
                meta["next_agent_id"] = reproduce(
                    agent, 
                    neighbor_agent, 
                    grid, 
                    agents_map, 
                    meta["next_agent_id"]
                )

@register_strategy("aging")
def aging_strategy(ctx):
    """Старение агентов"""
    for agent in list(ctx["agents_map"].values()):
        if agent["id"] not in ctx["agents_map"]:
            continue
        age_agent(agent, ctx["agents_map"], ctx["grid"])

@register_strategy("death")
def death_strategy(ctx):
    """Удаление мертвых агентов"""
    agents_map = ctx["agents_map"]
    grid = ctx["grid"]
    
    # Итерируемся по копии ключей, так как agents_map будет изменяться
    for agent_id in list(agents_map.keys()):
        check_and_remove_agent(agent_id, agents_map, grid)


@register_strategy("collect_data")
def collect_data_strategy(ctx):
    """Сбор данных о состоянии симуляции"""
    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    step = ctx["step"]
    
    current_sugar_map = [[cell["sugar"] for cell in row] for row in grid]
    
    step_data = {
        "step": step,
        "sugar_map": current_sugar_map,
        "agents": [
            {
                "id": ag["id"],
                "x": ag["x"],
                "y": ag["y"],
                "wealth": ag["sugar"] + ag["spicy"],
                "is_trading": ag["is_trading"]
            }
            for ag in agents_map.values()
        ]
    }
    
    ctx["simulation_history"].append(step_data)

# === Фабрика пайплайна ===
def build_pipeline(config: dict) -> list:
    """Создать пайплайн на основе конфигурации из реестра стратегий"""
    default_mechanics = [
        "reset_flags",
        "regeneration_map",
        "movement",
        "eating",
        "trading",   
        "reproduction",
        "aging",
        "death",
        "collect_data"
    ]
    
    mechanics = config.get("pipeline_steps")
    if not mechanics:
        mechanics = default_mechanics
        
    pipeline = []
    for step_name in mechanics:
        if step_name in REGISTRY:
            pipeline.append(REGISTRY[step_name])
        else:
            print(f"⚠️ Предупреждение: стратегия '{step_name}' не найдена в REGISTRY и пропущена.")
            
    return pipeline
