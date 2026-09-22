import random as rand
from classes import create_agent
from get_neighbors import get_neighbors
from typing import Any

def get_empty_neighbors(cell: dict, grid: list[list[dict]]) -> list:
    """Возвращает СПИСОК всех пустых соседей."""
    return [n for n in get_neighbors(cell, grid) if n["agent_id"] is None]

def reproduce(agent_a: dict[str, Any], agent_b: dict[str, Any], grid: list[list[dict]], agents_map: dict, next_id: int,
                min_resource: int = 20, percent_own_resources_to_child: float = 0.2,
                ) -> int:
                    
    if (agent_a["sugar"] < min_resource or agent_a["spicy"] < min_resource or
        agent_b["sugar"] < min_resource or agent_b["spicy"] < min_resource):
        return next_id

    # 2. Поиск свободного места
    cell_a = grid[agent_a["y"]][agent_a["x"]]
    cell_b = grid[agent_b["y"]][agent_b["x"]]
    
    # Используем новую функцию, возвращающую список
    candidates = get_empty_neighbors(cell_a, grid)
    candidates.extend(get_empty_neighbors(cell_b, grid))
    
    # Убираем дубликаты (если родители стоят рядом, у них могут быть общие соседи)
    unique_candidates = list({id(c): c for c in candidates}.values())
    
    if not unique_candidates:
        return next_id

    empty_cell = rand.choice(unique_candidates)

    # 3. Транзакция ресурсов
    cost_sugar_a = int(agent_a["sugar"] * percent_own_resources_to_child)
    cost_spicy_a = int(agent_a["spicy"] * percent_own_resources_to_child)
    cost_sugar_b = int(agent_b["sugar"] * percent_own_resources_to_child)
    cost_spicy_b = int(agent_b["spicy"] * percent_own_resources_to_child)

    agent_a["sugar"] -= cost_sugar_a
    agent_a["spicy"] -= cost_spicy_a
    agent_b["sugar"] -= cost_sugar_b
    agent_b["spicy"] -= cost_spicy_b

    child_sugar = cost_sugar_a + cost_sugar_b
    child_spicy = cost_spicy_a + cost_spicy_b

    # 4. Создание ребенка
    child = create_agent(
        id=next_id,
        x=empty_cell["posx"],
        y=empty_cell["posy"],
        sugar=child_sugar,
        spicy=child_spicy,
        vis = round((agent_a["vis"] + agent_b["vis"]) / 2)
    )

    agents_map[next_id] = child
    empty_cell["agent_id"] = next_id

    return next_id + 1
