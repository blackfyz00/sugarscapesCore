from registry import register_strategy
from mechanics.death.death import check_and_remove_agent

@register_strategy("death")
def death_strategy(ctx, params=None):
    """Удаление мертвых агентов"""
    agents_map = ctx["agents_map"]
    grid = ctx["grid"]
    
    # Итерируемся по копии ключей, так как agents_map будет изменяться
    for agent_id in list(agents_map.keys()):
        check_and_remove_agent(agent_id, agents_map, grid)
