from registry import register_strategy
import numpy as np

@register_strategy("regeneration_map")
def regenerate_resources_strategy(ctx, params=None):
    """Стратегия регенерации ресурсов"""
    if params is None:
        params = {}
    
    reg_sugar = params.get("regeneration_sugar", 1)
    reg_spicy = params.get("regeneration_spicy", 1)
    max_val = params.get("max_val", 4)

    world = ctx.get("world")
    
    if world is not None:
        # Векторизованная регенерация через WorldState
        world.regenerate(reg_sugar, reg_spicy, max_val)
        
        # ВАЖНО: Не перезаписываем ctx["grid"] здесь, если он используется другими механиками в том же шаге.
        # Обновление grid для совместимости лучше делать в collect_data или перед legacy-fallback механиками.
        # Если нужно срочно обновить для последующих legacy-шагов:
        if "grid" in ctx:
            # Оптимизация: обновляем значения inplace, если размер совпадает, чтобы сохранить ссылки
            grid = ctx["grid"]
            if len(grid) == world.size and len(grid[0]) == world.size:
                for y in range(world.size):
                    for x in range(world.size):
                        cell = grid[y][x]
                        cell["sugar"] = int(world.sugar_map[y, x])
                        cell["spicy"] = int(world.spicy_map[y, x])
            else:
                ctx["grid"] = world.to_dict_list()
                
    else:
        # Fallback для legacy грида
        grid = ctx.get("grid")
        if not grid:
            return
            
        for row in grid:
            for cell in row:
                # Используем min, чтобы не превысить max_val при rate > 1
                if cell["sugar"] < max_val:
                    cell["sugar"] = min(max_val, cell["sugar"] + reg_sugar)
                
                if "spicy" in cell and cell["spicy"] < max_val:
                    cell["spicy"] = min(max_val, cell["spicy"] + reg_spicy)
