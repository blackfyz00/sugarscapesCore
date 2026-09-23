from registry import register_strategy
from mechanics.aging.aging import age_agent

@register_strategy("aging")
def aging_strategy(ctx, params=None):
    """Вызывает механику старения для всех живых агентов"""
    if params is None:
        params = {}
    for agent in list(ctx["agents_map"].values()):
        if agent["id"] not in ctx["agents_map"]:
            continue
            
        age_agent(agent, ctx["agents_map"], ctx["grid"], **params)
