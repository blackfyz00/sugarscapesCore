import importlib

REGISTRY = {}
_LOADED_MECHANICS = set() 

# Маппинг имен механик на их пути модулей, если они отличаются от простого имени
module_mapping = {
    "regeneration_map": "regenerate_res.regenerate_resources_strategy",
    "movement": "movement.move_strategy",
    "eat": "eat.eat_strategy",
    "trading": "trade.trade_strategy",
    "reproduction": "reproduce.reproduce_strategy",
    "aging": "aging.aging_strategy",
    "death": "death.death_strategy"
}

def register_strategy(name):
    def decorator(func):
        REGISTRY[name] = func
        return func
    return decorator

def load_mechanic(mechanic_name: str):
    if mechanic_name in _LOADED_MECHANICS:
        return
    
    submodule = module_mapping.get(mechanic_name, mechanic_name)
    
    try:
        importlib.import_module(f'mechanics.{submodule}')
        _LOADED_MECHANICS.add(mechanic_name)
    except ModuleNotFoundError:
        print(f"⚠️ Модуль для механики '{mechanic_name}' (mechanics.{submodule}) не найден.")
    except Exception as e:
        print(f"❌ Ошибка внутри механики '{mechanic_name}': {e}")
