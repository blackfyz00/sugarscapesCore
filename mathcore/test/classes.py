import random as rand

def create_agent(id: int, x: int, y: int, **kwargs) -> dict:
    defaults = {
        "id": id,
        "x": x, 
        "y": y,          
        "vis": 3,
        "sugar": 25, "spicy": 25,
        "sugarm": 2, "spicym": 2,
        # "morality": 0.5,         
        "infected": False,       
        "is_trading": False      
    }
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
