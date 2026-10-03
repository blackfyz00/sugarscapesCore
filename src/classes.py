import random as rand
import copy
from typing import Any
from module_mapping import MODULE_MAPPING

def create_agent(id: int, x: int, y: int, config: dict) -> dict[str, Any]:
    """Создает агента, безопасно копируя структуру из конфига и учитывая требования модулей"""
    
    agent_cfg = config.get("agent", {})
    pipeline = config.get("pipeline_steps")
    
    # Собираем все требуемые поля и дефолты из активных модулей пайплайна
    required_fields = set()
    defaults = {}
    
    if pipeline:
        for step in pipeline:
            module_info = MODULE_MAPPING.get(step, {})
            required_fields.update(module_info.get("required_fields", []))
            defaults.update(module_info.get("defaults", {}))
    else:
        # Если пайплайн не указан (как в тестах), берем ВСЕ поля из конфига
        # И дополнительно добавляем дефолты для всех известных модулей, 
        # чтобы механики не падали с KeyError
        required_fields = set(agent_cfg.keys())
        for info in MODULE_MAPPING.values():
            defaults.update(info.get("defaults", {}))

    # Объединяем: приоритет у конфига, потом у дефолтов
    final_fields = {**defaults, **agent_cfg}
    
    base = {
        "id": id,
        "x": x,
        "y": y,
    }
    
    dynamic = {}
    for key in required_fields.union(set(final_fields.keys())):
        val = final_fields.get(key)
        if val is None:
            continue
            
        # 1. Обработка диапазонов [min, max]
        if isinstance(val, list) and len(val) == 2 and all(isinstance(i, (int, float)) for i in val):
            dynamic[key] = rand.randint(val[0], val[1]) if isinstance(val[0], int) else rand.uniform(val[0], val[1])
        
        # 2. Безопасное копирование сложных структур (списков/словарей)
        elif isinstance(val, (list, dict)):
            dynamic[key] = copy.deepcopy(val)
            
        else:
            dynamic[key] = val 
            
    # print(f"Agent {id} created with keys: {list(dynamic.keys())}") 
    
    return {**dynamic, **base} 

def create_cell(x: int, y: int, sugar: int, spicy: int) -> dict:
    return {
        "x": x,
        "y": y,
        "sugar": sugar,
        "spicy": spicy,
        "agent_id": None
    }