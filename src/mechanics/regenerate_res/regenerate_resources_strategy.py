from registry import register_strategy
from mechanics.regenerate_res.regenerate_resources import regenerate_resources

@register_strategy("regeneration_map")
def regeneration_strategy(ctx):
    """Регенерация ресурсов"""
    regenerate_resources(ctx["grid"])
