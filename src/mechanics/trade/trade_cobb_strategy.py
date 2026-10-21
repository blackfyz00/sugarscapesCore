# src/mechanics/trade/trade_cobb_strategy.py
from registry import register_strategy
from mechanics.trade.trade import trade_vectorized

@register_strategy("trading_cobb_douglas")
def trading_strategy(ctx, params=None):
    if not ctx.get("enable_trade", True):
        ctx["active_trades_raw"] = [] # Явно обнуляем, если торговли нет
        return

    world = ctx.get("world")
    agents = ctx.get("agents")

    if world is not None and agents is not None:
        # Получаем список сделок
        trades_list = trade_vectorized(world, agents)
        
        # Сохраняем для метрик
        ctx["active_trades_raw"] = trades_list
        
        # Для совместимости со старым кодом (если он читает active_trades как dict),
        # можно сформировать словарь быстро, но лучше использовать новый ключ.
        # Если старый код критичен, оставьте формирование active_trades ниже,
        # но для метрик используйте active_trades_raw.
        
        if trades_list:
             # Быстрая индексация для UI, если нужно показать кому кто продал
             # Но для метрик это не обязательно делать здесь
             pass
    else:
        ctx["active_trades_raw"] = []
