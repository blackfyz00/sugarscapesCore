import random as rand
from registry import register_strategy
from utils.get_neighbors import get_neighbors
from mechanics.reproduce.reproduce import reproduce

@register_strategy("reproduction")
def reproduction_strategy(ctx, params=None):
    """Стратегия размножения с учетом пожизненного лимита потомства"""
    if not params:
        return
        
    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    meta = ctx["meta"]
    config = ctx.get("config")
    
    current_id = meta.get("next_agent_id", 1)
    reproduced_ids = set()
    agent_ids = list(agents_map.keys())
    
    # Читаем параметры
    prob_range = params.get("probability", [1.0, 1.0])
    max_child_lifetime = params.get("max_child", 5) # Теперь это лимит на ВСЮ жизнь
    
    for aid in agent_ids:
        if aid not in agents_map or aid in reproduced_ids:
            continue
            
        agent = agents_map[aid]
        
        # 1. Проверка пожизненного лимита детей
        current_children = agent.get("children_count", 0)
        if isinstance(max_child_lifetime, list):
             limit = rand.randint(max_child_lifetime[0], max_child_lifetime[1])
        else:
             limit = int(max_child_lifetime)
             
        if current_children >= limit:
            continue # Агент уже достиг предела потомства
            
        # Проверка ресурсов родителя
        min_res = params.get("minimal_resources", 20)
        if (agent.get("sugar", 0) + agent.get("spicy", 0)) < min_res:
            continue
            
        # 2. Проверка вероятности размножения в ЭТОМ шаге
        if isinstance(prob_range, list) and len(prob_range) == 2:
            chance = rand.uniform(prob_range[0], prob_range[1])
        else:
            chance = float(prob_range)
            
        if rand.random() > chance:
            continue  
            
        current_cell = grid[agent["y"]][agent["x"]]
        neighbors = get_neighbors(current_cell, grid)
        
        for neighbor_cell in neighbors:
            nid = neighbor_cell.get("agent_id")
            
            if nid and nid in agents_map and nid != aid and nid not in reproduced_ids:
                neighbor = agents_map[nid]
                
                # Проверяем ресурсы и лимит соседа тоже
                if (neighbor.get("sugar", 0) + neighbor.get("spicy", 0)) < min_res:
                    continue
                
                # ВАЖНО: Передаем текущий ID для создания ребенка
                new_next_id = reproduce(
                    agent, 
                    neighbor, 
                    grid, 
                    agents_map, 
                    next_id=current_id,
                    min_resource=min_res,
                    percent_own_resources_to_child=params.get("percent_to_child", 0.2),
                    config=config
                )
                
                if new_next_id > current_id:
                    # Успешное рождение!
                    current_id = new_next_id
                    
                    # Обновляем счетчики детей у обоих родителей
                    agent["children_count"] = agent.get("children_count", 0) + 1
                    neighbor["children_count"] = neighbor.get("children_count", 0) + 1
                    
                    reproduced_ids.add(aid)
                    reproduced_ids.add(nid)
                    
                    # Если у основного агента кончился лимит или ресурсы, прерываем поиск
                    if agent["children_count"] >= limit or (agent.get("sugar", 0) + agent.get("spicy", 0)) < min_res:
                        break
                    
    meta["next_agent_id"] = current_id
