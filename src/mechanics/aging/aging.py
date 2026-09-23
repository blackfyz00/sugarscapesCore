def age_agent(agent: dict, agents_map: dict, grid: list[list[dict]], **kwargs) -> bool:
    """Увеличивает возраст"""
    agent["age"] += 1
    
    if agent["age"] >= agent["max_age"]:
        return True
        
    return False
