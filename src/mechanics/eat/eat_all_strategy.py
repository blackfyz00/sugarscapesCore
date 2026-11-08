from registry import register_strategy
import numpy as np

@register_strategy("eat_all")
def eat_strategy(ctx, params=None):
    """Векторизованное потребление ресурсов агентами из WorldState и AgentSystem"""
    world = ctx.get("world")
    agents = ctx.get("agents") # Это экземпляр AgentSystem
    
    if params is None:
        params = {}
    procent = params.get("procent", 1.0)

    if world is not None and agents is not None:
        alive = agents.get_alive_indices()
        if len(alive) == 0:
            return
        
        xs = agents.x[alive]
        ys = agents.y[alive]
        
        harvested_sugar_float = world.sugar_map[ys, xs].astype(np.float64) * procent
        harvested_spicy_float = world.spicy_map[ys, xs].astype(np.float64) * procent
        
        world.sugar_map[ys, xs] = 0
        world.spicy_map[ys, xs] = 0
        
        net_change_sugar = harvested_sugar_float - agents.sugarm[alive].astype(np.float64)
        net_change_spicy = harvested_spicy_float - agents.spicym[alive].astype(np.float64)
        
        target_dtype = agents.sugar.dtype
        
        new_sugar_vals = agents.sugar[alive].astype(np.float64) + net_change_sugar
        
        # Защита от отрицательных значений, если тип беззнаковый (uint*)
        if np.issubdtype(target_dtype, np.unsignedinteger):
            new_sugar_vals = np.maximum(new_sugar_vals, 0)
            
        # Округление до целого и приведение к нужному типу
        agents.sugar[alive] = np.round(new_sugar_vals).astype(target_dtype)
        
        # Аналогично для специй
        new_spicy_vals = agents.spicy[alive].astype(np.float64) + net_change_spicy
        
        if np.issubdtype(target_dtype, np.unsignedinteger):
            new_spicy_vals = np.maximum(new_spicy_vals, 0)
            
        agents.spicy[alive] = np.round(new_spicy_vals).astype(target_dtype)
