from registry import register_strategy
from mechanics.aging.aging import age_agent

@register_strategy("aging")
def aging_strategy(ctx):
    """Старение агентов"""
    for agent in list(ctx["agents_map"].values()):
        if agent["id"] not in ctx["agents_map"]:
            continue
        age_agent(agent, ctx["agents_map"], ctx["grid"])
