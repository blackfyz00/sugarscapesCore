from registry import register_strategy
from utils.get_neighbors import get_neighbors
from mechanics.trade.trade import trade

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
