# src/pipeline.py
import copy
import numpy as np  # ВАЖНО: необходим для проверки типов NumPy при сериализации
from functools import partial
from registry import register_strategy, REGISTRY, load_mechanic, MODULE_MAPPING

@register_strategy("reset_flags")
def reset_flags_strategy(ctx, params=None):
    """Сброс флагов торговли через AgentSystem"""
    agents = ctx.get("agents")
    if agents is not None:
        agents.is_trading.fill(False)
    else:
        for agent in ctx["agents_map"].values():
            agent["is_trading"] = False


@register_strategy("collect_data")
def collect_data_strategy(ctx, params=None):
    """Сбор данных о состоянии симуляции (поддерживает WorldState и AgentSystem)"""
    world = ctx.get("world")
    agents = ctx.get("agents")
    step = ctx["step"]
    
    if world is not None and agents is not None:
        current_sugar_map = world.sugar_map.tolist()
        current_spicy_map = world.spicy_map.tolist()
        
        # Очищаем типы NumPy перед сериализацией в JSON
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
    
    active_trades = ctx.pop("active_trades", None)
    if active_trades:
        for agent in agent_list:
            agent_id = agent.get("id")
            if agent_id in active_trades:
                trade_info = active_trades[agent_id]
                
                # Обработка нового формата словаря с деталями сделки
                if isinstance(trade_info, dict):
                    partner_id = trade_info.get("partner_id")
                    trade_text = trade_info.get("text", "")
                else:
                    # Fallback для старого формата (просто ID партнера)
                    partner_id = trade_info
                    trade_text = f"Сделка с #{partner_id}"

                if partner_id is not None:
                    agent["trade_partner_id"] = int(partner_id)
                    agent["trade_text"] = trade_text

    step_data = {
        "step": int(step),
        "sugar_map": current_sugar_map,
        "spicy_map": current_spicy_map,
        "agents": copy.deepcopy(agent_list)
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
