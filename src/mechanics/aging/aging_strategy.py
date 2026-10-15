from registry import register_strategy

@register_strategy("aging")
def aging_strategy(ctx, params=None):
    """Векторизованное старение агентов"""
    agents = ctx.get("agents")
    if agents is not None:
        alive = agents.get_alive_indices()
        if len(alive) > 0:
            agents.age[alive] += 1
    else:
        # Fallback
        from mechanics.aging.aging import age_agent
        for agent in list(ctx["agents_map"].values()):
            if agent["id"] not in ctx["agents_map"]:
                continue
            age_agent(agent, ctx["agents_map"], ctx["grid"], **params)
