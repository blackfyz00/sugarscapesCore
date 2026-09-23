from registry import register_strategy
from utils.get_neighbors import get_neighbors
from mechanics.trade.trade import trade

@register_strategy("trading_cobb_douglas")
def trading_strategy(ctx, params=None):
    """
    Стратегия торговли: каждый агент может совершить максимум одну сделку за шаг.
    """
    # Проверка глобального флага включения торговли
    if not ctx.get("enable_trade", True):
        return

    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    step = ctx["step"]
    
    # Множество ID агентов, которые уже совершили сделку в этом шаге
    traded_ids = set()
    
    # Получаем статический список ID, чтобы безопасно итерироваться
    current_agent_ids = list(agents_map.keys())
    
    for agent_id in current_agent_ids:
        # Если агент уже торговал или был удален, пропускаем
        if agent_id in traded_ids or agent_id not in agents_map:
            continue
            
        agent = agents_map[agent_id]
        
        # Находим клетку агента
        try:
            current_cell = grid[agent["y"]][agent["x"]]
        except (IndexError, KeyError):
            continue
            
        neighbors = get_neighbors(current_cell, grid)
        
        for neighbor_cell in neighbors:
            neighbor_id = neighbor_cell.get("agent_id")
            
            # Проверяем соседа: он должен существовать, быть живым, не быть самим собой и еще не торговать
            if (neighbor_id is not None and 
                neighbor_id in agents_map and 
                neighbor_id != agent_id and 
                neighbor_id not in traded_ids):
                
                # Пытаемся совершить сделку
                success = trade(current_cell, neighbor_cell, agents_map, step)
                
                if success:
                    # Если сделка прошла, помечаем обоих как "занятых"
                    traded_ids.add(agent_id)
                    traded_ids.add(neighbor_id)
                    break # Прерываем цикл по соседям, переходим к следующему агенту
