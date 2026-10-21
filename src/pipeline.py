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
    
    raw_trades = ctx.pop("active_trades_raw", [])
    
    # --- ФОРМИРОВАНИЕ ТЕКСТОВОГО ОПИСАНИЯ СДЕЛКИ ---
    trade_info_map = {} # id -> text
    
    for t in raw_trades:
        seller_id = t["seller_id"]
        buyer_id = t["buyer_id"]
        sugar_qty = t["sugar_qty"]
        spice_qty = t["spice_qty"]
        
        # Для ПРОДАВЦА: Он продал сахар, купил специи
        # Текст: "Продал X сахара за Y специй"
        seller_text = f"📦 Продал {int(sugar_qty)} Сах. за {int(spice_qty)} Спец."
        
        # Для ПОКУПАТЕЛЯ: Он купил сахар, заплатил специями
        # Текст: "Купил X сахара за Y специй"
        buyer_text = f"💰 Купил {int(sugar_qty)} Сах. за {int(spice_qty)} Спец."
        
        trade_info_map[seller_id] = seller_text
        trade_info_map[buyer_id] = buyer_text
        
    # Обогащаем список агентов
    for agent in agent_list:
        aid = agent.get("id")
        if aid in trade_info_map:
            agent["trade_text"] = trade_info_map[aid]
            # Также сохраним partner_id для связи линий, если нужно
            # Найдем партнера по списку trades
            for t in raw_trades:
                if t["seller_id"] == aid:
                    agent["trade_partner_id"] = t["buyer_id"]
                elif t["buyer_id"] == aid:
                    agent["trade_partner_id"] = t["seller_id"]

    step_data = {
        "step": int(step),
        "sugar_map": current_sugar_map,
        "spicy_map": current_spicy_map,
        "agents": agent_list,      
        "raw_trades": raw_trades   
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
