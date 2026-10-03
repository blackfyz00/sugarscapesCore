from registry import register_strategy

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
        
        # Сбор ресурсов с карт мира в позициях агентов
        harvested_sugar = world.sugar_map[ys, xs].astype(float) * procent
        harvested_spicy = world.spicy_map[ys, xs].astype(float) * procent
        
        # Обнуляем ресурсы на клетках
        world.sugar_map[ys, xs] = 0
        world.spicy_map[ys, xs] = 0
        
        # Применяем к агентам: + собранное, - метаболизм
        agents.sugar[alive] += harvested_sugar - agents.sugarm[alive]
        agents.spicy[alive] += harvested_spicy - agents.spicym[alive]
    else:
        # Fallback для старой логики со словарями
        import random
        grid = ctx["grid"]
        agents_map = ctx["agents_map"]
        agents_list = list(agents_map.values())
        random.shuffle(agents_list)
        for agent in agents_list:
            if agent["id"] not in agents_map:
                continue
            cx, cy = agent["x"], agent["y"]
            cell = grid[cy][cx]
            from mechanics.eat.eat import eat
            eat(cell, agents_map, grid, **params)
