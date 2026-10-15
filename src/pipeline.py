# src/pipeline.py
import copy
import numpy as np  
from functools import partial
from registry import register_strategy, REGISTRY, load_mechanic, MODULE_MAPPING

@register_strategy("reset_flags")
def reset_flags_strategy(ctx, params=None):
    agents = ctx.get("agents")
    if agents is not None:
        agents.is_trading.fill(False)
    # Сбрасываем буфер торгов на каждом шаге, чтобы не накапливать мусор
    ctx["active_trades_raw"] = [] 

@register_strategy("collect_data")
def collect_data_strategy(ctx, params=None):
    world = ctx.get("world")
    agents = ctx.get("agents")
    step = ctx["step"]
    
    if world is not None and agents is not None:
        current_sugar_map = world.sugar_map.tolist()
        current_spicy_map = world.spicy_map.tolist()
        
        agents_dict_map = agents.to_dict_map()
        agent_list = []
        for aid, agent in agents_dict_map.items():
            clean_agent = {}
            for k, v in agent.items():
                if isinstance(v, np.integer):
                    clean_agent[k] = int(v)
                elif isinstance(v, np.floating):
                    clean_agent[k] = float(v)
                else:
                    clean_agent[k] = v
            agent_list.append(clean_agent)
            
    else:
        grid = ctx["grid"]
        agents_map = ctx["agents_map"]
        current_sugar_map = [[cell["sugar"] for cell in row] for row in grid]
        current_spicy_map = [[cell["spicy"] for cell in row] for row in grid]
        agent_list = list(agents_map.values())
    
    # --- Сбор торговых данных ---
    raw_trades = ctx.pop("active_trades_raw", [])
    
    # Обогащение агентов данными о партнере
    partner_map = {}
    for t in raw_trades:
        partner_map[t["seller_id"]] = t["buyer_id"]
        partner_map[t["buyer_id"]] = t["seller_id"]
        
    for agent in agent_list:
        aid = agent.get("id")
        if aid in partner_map:
            agent["trade_partner_id"] = partner_map[aid]

    step_data = {
        "step": int(step),
        "sugar_map": current_sugar_map,
        "spicy_map": current_spicy_map,
        "agents": agent_list,      # ✅ ВОЗВРАЩАЕМ АГЕНТОВ СЮДА ОБЯЗАТЕЛЬНО
        "raw_trades": raw_trades   # ✅ И ТОРГИ ДЛЯ МЕТРИК
    }
    ctx["simulation_history"].append(step_data)


def build_pipeline(config: dict) -> list:
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
