# src/pipeline.py
import copy
import numpy as np  
from functools import partial
from registry import register_strategy, REGISTRY, load_mechanic, MODULE_MAPPING
from utils.ai_context import build_ai_context

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
        agent_list.sort(key=lambda x: x['id'])
    else:
        grid = ctx["grid"]
        agents_map = ctx["agents_map"]
        current_sugar_map = [[cell["sugar"] for cell in row] for row in grid]
        current_spicy_map = [[cell["spicy"] for cell in row] for row in grid]
        agent_list = list(agents_map.values())
    
    raw_trades = ctx.pop("active_trades_raw", [])
    
    trade_info_map = {} 
    partner_map = {}
    
    for t in raw_trades:
        seller_id = int(t["seller_id"])
        buyer_id = int(t["buyer_id"])
        
        # spice_qty уже int в новой версии trade_vectorized
        spice_cost = t["spice_qty"] 
        
        # Текст для продавца: он отдал 1 сахар, получил spice_cost специй
        trade_info_map[seller_id] = f"📦 Продажа: -1 Сах ➕ {spice_cost} Спец"
        
        # Текст для покупателя: он отдал spice_cost специй, получил 1 сахар
        trade_info_map[buyer_id] = f"💰 Покупка: +1 Сах ➖ {spice_cost} Спец"
        
        # Сохраняем партнеров сразу
        partner_map[seller_id] = buyer_id
        partner_map[buyer_id] = seller_id
    
    # 2. Обогащаем список агентов за один проход O(N)
    for agent in agent_list:
        aid = int(agent.get("id"))
        if aid in trade_info_map:
            agent["trade_text"] = trade_info_map[aid]
            agent["trade_partner_id"] = partner_map[aid]

    step_data = {
        "step": int(step),
        "sugar_map": current_sugar_map,
        "spicy_map": current_spicy_map,
        "agents": agent_list,      
        "raw_trades": raw_trades   
    }
    ai_summary = build_ai_context(step_data)
    step_data["ai_summary"] = ai_summary
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
