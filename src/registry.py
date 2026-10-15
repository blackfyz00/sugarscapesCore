# registry.py
import importlib

REGISTRY = {}
_LOADED_MECHANICS = set()

# Импортируем наш новый реестр
from module_mapping import MODULE_MAPPING

def register_strategy(name):
    def decorator(func):
        REGISTRY[name] = func
        return func
    return decorator

def load_mechanic(mechanic_name: str):
    if mechanic_name in _LOADED_MECHANICS:
        return
    
    # Берем информацию из нового реестра
    module_info = MODULE_MAPPING.get(mechanic_name)
    if not module_info:
        print(f"⚠️ Механика '{mechanic_name}' не найдена в MODULE_REGISTRY")
        return

    submodule_path = module_info["strategy"]
    
    try:
        # Импортируем модуль стратегии
        importlib.import_module(f'mechanics.{submodule_path}')
        _LOADED_MECHANICS.add(mechanic_name)
    except ModuleNotFoundError:
        print(f"⚠️ Модуль для механики '{mechanic_name}' (mechanics.{submodule_path}) не найден.")
    except Exception as e:
        print(f"❌ Ошибка внутри механики '{mechanic_name}': {e}")