import random as rand
import numpy as np
from registry import register_strategy
from classes import create_agent

@register_strategy("reproduction")
def reproduction_strategy(ctx, params=None):
    """Векторизованная стратегия размножения с использованием AgentSystem и WorldState"""
    if not params:
        return
        
    world = ctx.get("world")
    agents = ctx.get("agents")
    meta = ctx.get("meta")
    config = ctx.get("config")
    
    if world is not None and agents is not None:
        current_id = meta.get("next_agent_id", 1)
        alive = agents.get_alive_indices()
        if len(alive) < 2:
            return
            
        min_res = params.get("minimal_resources", 20)
        prob = params.get("probability", 1.0)
        if isinstance(prob, list):
            prob = prob[0]
            
        max_child = params.get("max_child", 5)
        if isinstance(max_child, list):
            max_child = max_child[0]

        # Фильтруем родителей по ресурсам и лимиту детей
        valid_parents = alive[
            (agents.sugar[alive] >= min_res) & 
            (agents.spicy[alive] >= min_res) & 
            (agents.children_count[alive] < max_child)
        ]
        
        if len(valid_parents) < 2:
            return
            
        # Проходим по валидным родителям и ищем соседей для размножения
        reproduced = set()
        occupancy = world.occupancy
        size = world.size
        
        for idx in valid_parents:
            if idx in reproduced:
                continue
            if rand.random() > prob:
                continue
                
            x, y = int(agents.x[idx]), int(agents.y[idx])
            
            # Ищем свободного соседа в радиусе 1
            found_neighbor = False
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < size and 0 <= ny < size:
                    neighbor_aid = occupancy[ny, nx]
                    if neighbor_aid != -1:
                        n_indices = np.where(agents.id == neighbor_aid)[0]
                        if len(n_indices) > 0:
                            n_idx = n_indices[0]
                            if n_idx not in reproduced and agents.children_count[n_idx] < max_child:
                                if agents.sugar[n_idx] >= min_res and agents.spicy[n_idx] >= min_res:
                                    # Находим свободную клетку рядом для ребенка
                                    empty_spots = []
                                    for edx, edy in [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                                        ex, ey = x + edx, y + edy
                                        if 0 <= ex < size and 0 <= ey < size and occupancy[ey, ex] == -1:
                                            empty_spots.append((ex, ey))
                                    if not empty_spots:
                                        for edx, edy in [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                                            ex, ey = int(agents.x[n_idx]) + edx, int(agents.y[n_idx]) + edy
                                            if 0 <= ex < size and 0 <= ey < size and occupancy[ey, ex] == -1:
                                                empty_spots.append((ex, ey))
                                                
                                    if empty_spots:
                                        ex, ey = rand.choice(empty_spots)
                                        
                                        # Снимаем ресурсы
                                        cost_s_1 = agents.sugar[idx] * 0.2
                                        cost_sp_1 = agents.spicy[idx] * 0.2
                                        cost_s_2 = agents.sugar[n_idx] * 0.2
                                        cost_sp_2 = agents.spicy[n_idx] * 0.2
                                        
                                        agents.sugar[idx] -= cost_s_1
                                        agents.spicy[idx] -= cost_sp_1
                                        agents.sugar[n_idx] -= cost_s_2
                                        agents.spicy[n_idx] -= cost_sp_2
                                        
                                        child_data = {
                                            "sugar": cost_s_1 + cost_s_2,
                                            "spicy": cost_sp_1 + cost_sp_2,
                                            "vis": int((agents.vis[idx] + agents.vis[n_idx]) / 2),
                                            "max_age": int((agents.max_age[idx] + agents.max_age[n_idx]) / 2),
                                            "age": 0
                                        }
                                        
                                        new_idx = agents.spawn(current_id, ex, ey, child_data)
                                        occupancy[ey, ex] = current_id
                                        
                                        agents.children_count[idx] += 1
                                        agents.children_count[n_idx] += 1
                                        
                                        reproduced.add(idx)
                                        reproduced.add(n_idx)
                                        current_id += 1
                                        found_neighbor = True
                                        break
            if found_neighbor:
                continue
                
        meta["next_agent_id"] = current_id
    else:
        # Fallback для старого словаря
        grid = ctx["grid"]
        agents_map = ctx["agents_map"]
        meta = ctx["meta"]
        config = ctx.get("config")
        current_id = meta.get("next_agent_id", 1)
        reproduced_ids = set()
        
        prob_range = params.get("probability", [1.0, 1.0])
        max_child_lifetime = params.get("max_child", 5)
        min_res = params.get("minimal_resources", 20)
        
        for aid in list(agents_map.keys()):
            if aid not in agents_map or aid in reproduced_ids:
                continue
            agent = agents_map[aid]
            if agent.get("children_count", 0) >= max_child_lifetime:
                continue
            if (agent.get("sugar", 0) + agent.get("spicy", 0)) < min_res:
                continue
            if rand.random() > prob_range[0]:
                continue
                
            from utils.get_neighbors import get_neighbors
            from mechanics.reproduce.reproduce import reproduce
            current_cell = grid[agent["y"]][agent["x"]]
            for neighbor_cell in get_neighbors(current_cell, grid):
                nid = neighbor_cell.get("agent_id")
                if nid and nid in agents_map and nid != aid and nid not in reproduced_ids:
                    neighbor = agents_map[nid]
                    new_next_id = reproduce(
                        agent, neighbor, grid, agents_map, 
                        next_id=current_id, min_resource=min_res,
                        percent_own_resources_to_child=params.get("percent_to_child", 0.2),
                        config=config
                    )
                    if new_next_id > current_id:
                        current_id = new_next_id
                        agent["children_count"] = agent.get("children_count", 0) + 1
                        neighbor["children_count"] = neighbor.get("children_count", 0) + 1
                        reproduced_ids.add(aid)
                        reproduced_ids.add(nid)
                        break
        meta["next_agent_id"] = current_id
