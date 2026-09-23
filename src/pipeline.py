# pipeline.py
from functools import partial
from registry import register_strategy, REGISTRY, load_mechanic, MODULE_MAPPING
import copy 

@register_strategy("reset_flags")
def reset_flags_strategy(ctx, params=None):
    """Сброс флагов торговли"""
    for agent in ctx["agents_map"].values():
        agent["is_trading"] = False

@register_strategy("collect_data")
def collect_data_strategy(ctx, params=None):
    """Сбор данных о состоянии симуляции"""
    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    step = ctx["step"]
    
    current_sugar_map = [[cell["sugar"] for cell in row] for row in grid]
    current_spicy_map = [[cell["spicy"] for cell in row] for row in grid]
    
    step_data = {
        "step": step,
        "sugar_map": current_sugar_map,
        "spicy_map": current_spicy_map,
        "agents": copy.deepcopy(list(agents_map.values()))
    }
    ctx["simulation_history"].append(step_data)

def build_pipeline(config: dict) -> list:
    """Собирает пайплайн, автоматически добавляя системные шаги"""
    
    system_steps = ["reset_flags", "collect_data"]
    
    user_steps = config.get("pipeline_steps", [])
    
    full_pipeline_names = system_steps[:1] + user_steps + system_steps[1:]
    
    pipeline = []
    for step_name in full_pipeline_names:
        if step_name not in REGISTRY:
            load_mechanic(step_name)
            
        if step_name in REGISTRY:
            func = REGISTRY[step_name]
            params = config.get(step_name, {}) 
            pipeline.append(partial(func, params=params))
            
    return pipeline
