# src/mechanics/trade/trade_cobb_strategy.py
from registry import register_strategy
from mechanics.trade.trade import trade_vectorized

@register_strategy("trading_cobb_douglas")
def trading_strategy(ctx, params=None):
    if not ctx.get("enable_trade", True):
        return

    world = ctx.get("world")
    agents = ctx.get("agents")

    if world is not None and agents is not None:
        trade_details = trade_vectorized(world, agents)
        if trade_details:
            ctx["active_trades"] = trade_details
    else:
        # Fallback для старой логики (если нужен)
        pass
