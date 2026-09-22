import random as rand

def create_agent(id: int, x: int, y: int, config: dict = None, **kwargs) -> dict:
    if config is None:
        config = {}
        
    defaults = {
        "id": id,
        "x": x, 
        "y": y,          
        "vis": 3,
        "sugar": 25, 
        "spicy": 25,
        "sugarm": 12, 
        "spicym": 8,
        "history_trades": [],
        "is_trading": False,
    }
    
    # Если включено старение, добавляем поля возраста и max_age
    if config.get("enable_aging", True):
        defaults["age"] = 0
        defaults["max_age"] = rand.randint(60, 100)

    defaults.update(kwargs)
    return defaults

def create_cell(posx: int, posy: int, sugar: int, spicy: int) -> dict:
    return {
        "posx": posx,
        "posy": posy,
        "sugar": sugar,
        "spicy": spicy,
        "agent_id": None
    }
