import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from classes import create_agent, create_cell
from eat import eat

def test_normal_consumption():
    """Агент успешно ест и тратит метаболизм"""
    # Создаем агента с 10 сахара и метаболизмом 2
    agent = create_agent(id=1, x=0, y=0, sugar=10, spicy=10, sugarm=2, spicym=2)
    
    # Создаем клетку с 5 ресурсами
    cell = create_cell(posx=0, posy=0, sugar=5, spicy=5)
    cell["agent_id"] = 1
    
    agents_map = {1: agent}
    
    eat(cell, agents_map)
    
    # Проверки
    assert cell["sugar"] == 0, "Клетка должна быть пустой"
    assert cell["spicy"] == 0, "Клетка должна быть пустой"
    assert agent["sugar"] == 13, f"Ожидалось 13 (10+5-2), получено {agent['sugar']}"
    assert agent["spicy"] == 13, f"Ожидалось 13 (10+5-2), получено {agent['spicy']}"

def test_empty_cell_no_crash():
    """Функция не падает, если в клетке нет агента"""
    cell = create_cell(posx=0, posy=0, sugar=5, spicy=5)
    # agent_id по умолчанию None
    
    # Должно просто вернуться без ошибок
    eat(cell, {}) 

def test_starvation_scenario():
    """Агент умирает и удаляется из карты, если ресурсы <= 0 после метаболизма"""
    agent = create_agent(id=1, x=0, y=0, sugar=1, spicy=1, sugarm=3, spicym=3)
    cell = create_cell(posx=0, posy=0, sugar=0, spicy=0)
    cell["agent_id"] = 1
    
    agents_map = {1: agent}
    
    eat(cell, agents_map)
    
    # Проверяем, что агент был удален из словаря
    assert 1 not in agents_map, "Голодный агент должен быть удален из agents_map"
  