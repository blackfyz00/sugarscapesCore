from registry import register_strategy

@register_strategy("regeneration_map")
def regeneration_map_strategy(ctx, params=None):
    """Стратегия регенерации ресурсов с поддержкой параметров из контракта"""
    grid = ctx["grid"]
    if params is None:
        params = {}
    
    reg_sugar = params.get("regeneration_sugar", 1)
    reg_spicy = params.get("regeneration_spicy", 1)
    max_val = params.get("max_val", 4)

    for row in grid:
        for cell in row:
            if cell["sugar"] < max_val:
                cell["sugar"] += reg_sugar
            if "spicy" in cell and cell["spicy"] < max_val:
                cell["spicy"] += reg_spicy
