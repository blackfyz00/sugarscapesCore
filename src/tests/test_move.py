import pytest
from classes import create_agent, create_cell
from mechanics.movement.move import move

def test_successful_move():
    """Агент успешно перемещается из одной клетки в другую"""
    agent = create_agent(id=1, x=0, y=0, config={"agent": {}})
    cell_from = create_cell(x=0, y=0, sugar=0, spicy=0)
    cell_from["agent_id"] = 1
    
    cell_to = create_cell(x=1, y=0, sugar=5, spicy=5)
    
    agents_map = {1: agent}
    
    success = move(cell_from, cell_to, agents_map)
    
    assert success is True, "Перемещение должно быть успешным"
    assert cell_from["agent_id"] is None, "Исходная клетка должна освободиться"
    assert cell_to["agent_id"] == 1, "Целевая клетка должна содержать агента"
    assert agent["x"] == 1
    assert agent["y"] == 0

def test_move_from_empty_cell():
    """Нельзя переместить агента, если в исходной клетке нет агента"""
    cell_from = create_cell(x=0, y=0, sugar=0, spicy=0)
    cell_to = create_cell(x=1, y=0, sugar=5, spicy=5)
    agents_map = {}
    
    success = move(cell_from, cell_to, agents_map)
    
    assert success is False, "Перемещение из пустой клетки должно вернуть False"

def test_move_to_occupied_cell():
    """Нельзя переместиться в занятую клетку"""
    agent1 = create_agent(id=1, x=0, y=0, config={"agent": {}})
    agent2 = create_agent(id=2, x=1, y=0, config={"agent": {}})
    
    cell_from = create_cell(x=0, y=0, sugar=0, spicy=0)
    cell_from["agent_id"] = 1
    
    cell_to = create_cell(x=1, y=0, sugar=5, spicy=5)
    cell_to["agent_id"] = 2
    
    agents_map = {1: agent1, 2: agent2}
    
    success = move(cell_from, cell_to, agents_map)
    
    assert success is False, "Перемещение в занятую клетку должно быть запрещено"
    assert cell_from["agent_id"] == 1, "Агент должен остаться на месте"
    assert cell_to["agent_id"] == 2, "Целевой агент должен остаться на месте"
