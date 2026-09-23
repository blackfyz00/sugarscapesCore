import pytest
from classes import create_agent, create_cell
from mechanics.eat.eat import eat

def test_normal_consumption():
    """Агент успешно ест и тратит метаболизм"""
    config = {"agent": {"sugar": 10, "spicy": 10, "sugarm": 2, "spicym": 2}}
    agent = create_agent(id=1, x=0, y=0, config=config)
    
    # Создаем клетку с 5 ресурсами
    cell = create_cell(x=0, y=0, sugar=5, spicy=5)
    cell["agent_id"] = 1
    
    agents_map = {1: agent}
    grid = [[cell]]
    
    eat(cell, agents_map, grid)
    
    # Проверки
    assert cell["sugar"] == 0, "Клетка должна быть пустой"
    assert cell["spicy"] == 0, "Клетка должна быть пустой"
    assert agent["sugar"] == 13, f"Ожидалось 13 (10+5-2), получено {agent['sugar']}"
    assert agent["spicy"] == 13, f"Ожидалось 13 (10+5-2), получено {agent['spicy']}"

def test_empty_cell_no_crash():
    """Функция не падает, если в клетке нет агента"""
    cell = create_cell(x=0, y=0, sugar=5, spicy=5)
    # agent_id по умолчанию None
    grid = [[cell]]
    
    # Должно просто вернуться без ошибок
    eat(cell, {}, grid) 

def test_starvation_scenario():
    """Агент истощается, если ресурсы <= 0 после метаболизма (удаление происходит на шаге death)"""
    config = {"agent": {"sugar": 1, "spicy": 1, "sugarm": 3, "spicym": 3}}
    agent = create_agent(id=1, x=0, y=0, config=config)
    cell = create_cell(x=0, y=0, sugar=0, spicy=0)
    cell["agent_id"] = 1
    
    agents_map = {1: agent}
    grid = [[cell]]
    
    eat(cell, agents_map, grid)
    
    # Проверяем, что ресурсы стали отрицательными / равны нулю, а удаление контролируется отдельно
    assert agent["sugar"] <= 0
    assert agent["spicy"] <= 0
