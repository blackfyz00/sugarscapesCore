from registry import register_strategy
from mechanics.movement.findperspectivecell import find_perspective_cell
from mechanics.movement.move import move

@register_strategy("movement_cobb_douglas")
def movement_strategy(ctx, params=None):
    """Движение агентов"""
    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    if params is None:
        params = {}
    
    for agent in list(agents_map.values()):
        if agent["id"] not in agents_map:
            continue
        current_cell = grid[agent["y"]][agent["x"]]
        best_cell = find_perspective_cell(current_cell, grid, agents_map, **params)
        if best_cell and best_cell != current_cell:
            move(current_cell, best_cell, agents_map)
