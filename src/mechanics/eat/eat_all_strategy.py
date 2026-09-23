import random
from registry import register_strategy
from mechanics.eat.eat import eat
@register_strategy("eat_all")
def eat_strategy(ctx, params=None):
    """Потребление ресурсов агентами в случайном порядке"""
    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    if params is None:
        params = {}
    agents_list = list(agents_map.values())
    random.shuffle(agents_list)
    for agent in agents_list:
        if agent["id"] not in agents_map:
            continue
        cx, cy = agent["x"], agent["y"]
        cell = grid[cy][cx]  
        eat(cell, agents_map, grid, **params)
