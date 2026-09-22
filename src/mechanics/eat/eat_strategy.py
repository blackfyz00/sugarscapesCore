from registry import register_strategy
from mechanics.eat.eat import eat

@register_strategy("eat")
def eat_strategy(ctx):
    """Потребление ресурсов"""
    grid = ctx["grid"] # Получаем grid из контекста
    agents_map = ctx["agents_map"]
    for row in grid:
        for cell in row:
            eat(cell, agents_map, grid) # Передаем grid в eat
