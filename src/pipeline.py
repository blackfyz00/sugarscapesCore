from registry import register_strategy, REGISTRY, load_mechanic

@register_strategy("reset_flags")
def reset_flags_strategy(ctx):
    """Сброс флагов торговли"""
    for agent in ctx["agents_map"].values():
        agent["is_trading"] = False

@register_strategy("collect_data")
def collect_data_strategy(ctx):
    """Сбор данных о состоянии симуляции"""
    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    step = ctx["step"]
    
    current_sugar_map = [[cell["sugar"] for cell in row] for row in grid]
    
    step_data = {
        "step": step,
        "sugar_map": current_sugar_map,
        "agents": [
            {
                "id": ag["id"],
                "x": ag["x"],
                "y": ag["y"],
                "wealth": ag["sugar"] + ag["spicy"],
                "is_trading": ag["is_trading"]
            }
            for ag in agents_map.values()
        ]
    }
    
    ctx["simulation_history"].append(step_data)

# === Фабрика пайплайна ===
def build_pipeline(config: dict) -> list:
    """Создать пайплайн на основе конфигурации из реестра стратегий"""
    default_mechanics = [
        "reset_flags",
        "regeneration_map",
        "movement",
        "eat",
        "trading",   
        "reproduction",
        "aging",
        "death",
        "collect_data"
    ]
    
    mechanics = config.get("pipeline_steps")
    if not mechanics:
        mechanics = default_mechanics
        
    pipeline = []
    for step_name in mechanics:
        # Автоматически пытаемся загрузить механику, если она еще не зарегистрирована
        if step_name not in REGISTRY:
            load_mechanic(step_name)

        if step_name in REGISTRY:
            pipeline.append(REGISTRY[step_name])
        else:
            print(f"⚠️ Предупреждение: стратегия '{step_name}' не найдена в REGISTRY и пропущена.")
    print(REGISTRY) 
    return pipeline
