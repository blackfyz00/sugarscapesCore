from registry import register_strategy
from utils.get_neighbors import get_neighbors
from mechanics.reproduce.reproduce import reproduce

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
