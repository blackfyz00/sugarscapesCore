from registry import register_strategy
from mechanics.trade.trade import trade_vectorized

@register_strategy("trading_cobb_douglas")
def trading_strategy(ctx, params=None):
    """
    Стратегия торговли (векторизованная).
    """
    if not ctx.get("enable_trade", True):
        return

    world = ctx.get("world")
    agents = ctx.get("agents")
    step = ctx["step"]

    if world is not None and agents is not None:
        trade_vectorized(world, agents)
    else:
        # Fallback
        grid = ctx["grid"]
        agents_map = ctx["agents_map"]
        from utils.get_neighbors import get_neighbors
        from mechanics.trade.trade import trade
        
        traded_ids = set()
        for agent_id in list(agents_map.keys()):
            if agent_id in traded_ids or agent_id not in agents_map:
                continue
            agent = agents_map[agent_id]
            try:
                current_cell = grid[agent["y"]][agent["x"]]
            except (IndexError, KeyError):
                continue
            for neighbor_cell in get_neighbors(current_cell, grid):
                neighbor_id = neighbor_cell.get("agent_id")
                if neighbor_id and neighbor_id in agents_map and neighbor_id != agent_id and neighbor_id not in traded_ids:
                    if trade(current_cell, neighbor_cell, agents_map, step):
                        traded_ids.add(agent_id)
                        traded_ids.add(neighbor_id)
                        break
