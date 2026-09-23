import pytest
from classes import create_agent, create_cell
from mechanics.movement.findperspectivecell import find_perspective_cell

def test_find_perspective_cell_success():
    """Поиск выбирает свободную клетку в пределах видимости с наилучшим благосостоянием"""
    config = {"agent": {"sugar": 10, "spicy": 10, "sugarm": 1, "spicym": 1, "vis": 2}}
    agent = create_agent(id=1, x=1, y=1, config=config)
    
    cell_current = create_cell(x=1, y=1, sugar=0, spicy=0)
    cell_current["agent_id"] = 1
    
    # Клетка вне зоны видимости (vis=2)
    cell_far = create_cell(x=5, y=5, sugar=100, spicy=100)
    
    # Клетка в зоне видимости с хорошими ресурсами
    cell_good = create_cell(x=2, y=1, sugar=10, spicy=10)
    
    # Клетка в зоне видимости с меньшими ресурсами
    cell_poor = create_cell(x=1, y=2, sugar=1, spicy=1)
    
    # Занятая клетка в зоне видимости
    cell_occupied = create_cell(x=0, y=1, sugar=50, spicy=50)
    cell_occupied["agent_id"] = 2
    
    map_matrix = [
        [create_cell(x=0, y=0, sugar=0, spicy=0), cell_occupied, create_cell(x=2, y=0, sugar=0, spicy=0), create_cell(x=3, y=0, sugar=0, spicy=0), create_cell(x=4, y=0, sugar=0, spicy=0), create_cell(x=5, y=0, sugar=0, spicy=0)],
        [create_cell(x=0, y=1, sugar=0, spicy=0), cell_current, cell_good, create_cell(x=3, y=1, sugar=0, spicy=0), create_cell(x=4, y=1, sugar=0, spicy=0), create_cell(x=5, y=1, sugar=0, spicy=0)],
        [create_cell(x=0, y=2, sugar=0, spicy=0), cell_poor, create_cell(x=2, y=2, sugar=0, spicy=0), create_cell(x=3, y=2, sugar=0, spicy=0), create_cell(x=4, y=2, sugar=0, spicy=0), create_cell(x=5, y=2, sugar=0, spicy=0)],
        [create_cell(x=0, y=3, sugar=0, spicy=0), create_cell(x=1, y=3, sugar=0, spicy=0), create_cell(x=2, y=3, sugar=0, spicy=0), create_cell(x=3, y=3, sugar=0, spicy=0), create_cell(x=4, y=3, sugar=0, spicy=0), create_cell(x=5, y=3, sugar=0, spicy=0)],
        [create_cell(x=0, y=4, sugar=0, spicy=0), create_cell(x=1, y=4, sugar=0, spicy=0), create_cell(x=2, y=4, sugar=0, spicy=0), create_cell(x=3, y=4, sugar=0, spicy=0), create_cell(x=4, y=4, sugar=0, spicy=0), create_cell(x=5, y=4, sugar=0, spicy=0)],
        [create_cell(x=0, y=5, sugar=0, spicy=0), create_cell(x=1, y=5, sugar=0, spicy=0), create_cell(x=2, y=5, sugar=0, spicy=0), create_cell(x=3, y=5, sugar=0, spicy=0), create_cell(x=4, y=5, sugar=0, spicy=0), cell_far],
    ]

    agents_map = {1: agent, 2: create_agent(id=2, x=0, y=1, config={"agent": {}})}

    best_cell = find_perspective_cell(cell_current, map_matrix, agents_map)

    assert best_cell is not None, "Должна быть найдена перспективная клетка"
    assert best_cell["x"] == 2 and best_cell["y"] == 1, "Должна быть выбрана клетка cell_good"

def test_find_perspective_cell_no_agent():
    """Если в клетке нет агента, поиск возвращает None"""
    cell_current = create_cell(x=0, y=0, sugar=0, spicy=0)
    map_matrix = [[cell_current]]
    
    result = find_perspective_cell(cell_current, map_matrix, {})
    assert result is None

def test_find_perspective_cell_no_visible_cells():
    """Если все клетки в зоне видимости заняты или отсутствуют, возвращает None"""
    # ИСПРАВЛЕНО: Добавлены ресурсы и метаболизм в конфиг
    config = {"agent": {"vis": 1, "sugar": 10, "spicy": 10, "sugarm": 1, "spicym": 1}}
    agent = create_agent(id=1, x=0, y=0, config=config)
    cell_current = create_cell(x=0, y=0, sugar=0, spicy=0)
    cell_current["agent_id"] = 1
    
    neighbor_1 = create_cell(x=1, y=0, sugar=10, spicy=10)
    neighbor_1["agent_id"] = 2
    
    map_matrix = [
        [cell_current, neighbor_1]
    ]
    agents_map = {1: agent, 2: create_agent(id=2, x=1, y=0, config={"agent": {}})}
    
    result = find_perspective_cell(cell_current, map_matrix, agents_map)
    assert result is None
