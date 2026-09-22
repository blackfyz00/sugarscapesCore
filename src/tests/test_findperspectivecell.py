import pytest
from classes import create_agent, create_cell
from mechanics.movement.findperspectivecell import find_perspective_cell

def test_find_perspective_cell_success():
    """Поиск выбирает свободную клетку в пределах видимости с наилучшим благосостоянием"""
    agent = create_agent(id=1, x=1, y=1, sugar=10, spicy=10, sugarm=1, spicym=1, vis=2)
    
    cell_current = create_cell(posx=1, posy=1, sugar=0, spicy=0)
    cell_current["agent_id"] = 1
    
    # Клетка вне зоны видимости (vis=2)
    cell_far = create_cell(posx=5, posy=5, sugar=100, spicy=100)
    
    # Клетка в зоне видимости с хорошими ресурсами
    cell_good = create_cell(posx=2, posy=1, sugar=10, spicy=10)
    
    # Клетка в зоне видимости с меньшими ресурсами
    cell_poor = create_cell(posx=1, posy=2, sugar=1, spicy=1)
    
    # Занятая клетка в зоне видимости
    cell_occupied = create_cell(posx=0, posy=1, sugar=50, spicy=50)
    cell_occupied["agent_id"] = 2
    
    # Добавим cell_far отдельно в карту большего размера, либо разместим в матрице
    map_matrix = [
        [create_cell(posx=0, posy=0, sugar=0, spicy=0), cell_occupied, create_cell(posx=2, posy=0, sugar=0, spicy=0), create_cell(posx=3, posy=0, sugar=0, spicy=0), create_cell(posx=4, posy=0, sugar=0, spicy=0), create_cell(posx=5, posy=0, sugar=0, spicy=0)],
        [create_cell(posx=0, posy=1, sugar=0, spicy=0), cell_current, cell_good, create_cell(posx=3, posy=1, sugar=0, spicy=0), create_cell(posx=4, posy=1, sugar=0, spicy=0), create_cell(posx=5, posy=1, sugar=0, spicy=0)],
        [create_cell(posx=0, posy=2, sugar=0, spicy=0), cell_poor, create_cell(posx=2, posy=2, sugar=0, spicy=0), create_cell(posx=3, posy=2, sugar=0, spicy=0), create_cell(posx=4, posy=2, sugar=0, spicy=0), create_cell(posx=5, posy=2, sugar=0, spicy=0)],
        [create_cell(posx=0, posy=3, sugar=0, spicy=0), create_cell(posx=1, posy=3, sugar=0, spicy=0), create_cell(posx=2, posy=3, sugar=0, spicy=0), create_cell(posx=3, posy=3, sugar=0, spicy=0), create_cell(posx=4, posy=3, sugar=0, spicy=0), create_cell(posx=5, posy=3, sugar=0, spicy=0)],
        [create_cell(posx=0, posy=4, sugar=0, spicy=0), create_cell(posx=1, posy=4, sugar=0, spicy=0), create_cell(posx=2, posy=4, sugar=0, spicy=0), create_cell(posx=3, posy=4, sugar=0, spicy=0), create_cell(posx=4, posy=4, sugar=0, spicy=0), create_cell(posx=5, posy=4, sugar=0, spicy=0)],
        [create_cell(posx=0, posy=5, sugar=0, spicy=0), create_cell(posx=1, posy=5, sugar=0, spicy=0), create_cell(posx=2, posy=5, sugar=0, spicy=0), create_cell(posx=3, posy=5, sugar=0, spicy=0), create_cell(posx=4, posy=5, sugar=0, spicy=0), cell_far],
    ]

    agents_map = {1: agent, 2: create_agent(id=2, x=0, y=1)}

    best_cell = find_perspective_cell(cell_current, map_matrix, agents_map)

    assert best_cell is not None, "Должна быть найдена перспективная клетка"
    # cell_good имеет больше ресурсов, чем cell_poor, и находится в радиусе видимости (расстояние 1)
    # cell_far имеет супер много ресурсов, но она вне зоны видимости (vis=2)
    assert best_cell["posx"] == 2 and best_cell["posy"] == 1, "Должна быть выбрана клетка cell_good"

def test_find_perspective_cell_no_agent():
    """Если в клетке нет агента, поиск возвращает None"""
    cell_current = create_cell(posx=0, posy=0, sugar=0, spicy=0)
    # agent_id = None
    map_matrix = [[cell_current]]
    
    result = find_perspective_cell(cell_current, map_matrix, {})
    assert result is None

def test_find_perspective_cell_no_visible_cells():
    """Если все клетки в зоне видимости заняты или отсутствуют, возвращает None"""
    agent = create_agent(id=1, x=0, y=0, vis=1)
    cell_current = create_cell(posx=0, posy=0, sugar=0, spicy=0)
    cell_current["agent_id"] = 1
    
    neighbor_1 = create_cell(posx=1, posy=0, sugar=10, spicy=10)
    neighbor_1["agent_id"] = 2
    
    map_matrix = [
        [cell_current, neighbor_1]
    ]
    agents_map = {1: agent, 2: create_agent(id=2, x=1, y=0)}
    
    result = find_perspective_cell(cell_current, map_matrix, agents_map)
    assert result is None
