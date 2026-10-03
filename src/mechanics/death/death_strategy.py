from registry import register_strategy
import numpy as np

@register_strategy("death")
def death_strategy(ctx, params=None):
    """Векторизованная проверка и удаление мертвых агентов (голод или старость)"""
    world = ctx.get("world")
    agents = ctx.get("agents")
    
    if world is not None and agents is not None:
        alive = agents.get_alive_indices()
        if len(alive) == 0:
            return
            
        is_starved = (agents.sugar[alive] <= 0) | (agents.spicy[alive] <= 0)
        is_old = agents.age[alive] >= agents.max_age[alive]
        
        dead_mask_local = is_starved | is_old
        dead_indices = alive[dead_mask_local]
        
        if len(dead_indices) > 0:
            # Очищаем occupancy на сетке мира
            for idx in dead_indices:
                x, y = agents.x[idx], agents.y[idx]
                if world.occupancy[y, x] == agents.id[idx]:
                    world.occupancy[y, x] = -1
            
            # Убиваем в AgentSystem
            agents.kill(dead_indices)
    else:
        # Fallback
        agents_map = ctx["agents_map"]
        grid = ctx["grid"]
        from mechanics.death.death import check_and_remove_agent
        for agent_id in list(agents_map.keys()):
            check_and_remove_agent(agent_id, agents_map, grid)
