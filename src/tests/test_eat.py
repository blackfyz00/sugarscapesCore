import pytest
import numpy as np
from core.world import WorldState
from core.agents import AgentSystem
from mechanics.eat.eat_all_strategy import eat_strategy

def test_normal_consumption():
    """Агент успешно ест ресурсы с карты и платит метаболизм"""
    world = WorldState(size=1)
    world.sugar_map[0, 0] = 5
    world.spicy_map[0, 0] = 5
    world.occupancy[0, 0] = 1

    agents = AgentSystem(capacity=10)
    idx = agents.spawn(id=1, x=0, y=0, data={"sugar": 10.0, "spicy": 10.0, "sugarm": 2.0, "spicym": 2.0})

    ctx = {"world": world, "agents": agents}
    eat_strategy(ctx)

    # Проверки: ресурсы на клетке собраны и обнулены
    assert world.sugar_map[0, 0] == 0
    assert world.spicy_map[0, 0] == 0
    # Ресурсы агента: 10 (старт) + 5 (собрано) - 2 (метаболизм) = 13
    assert agents.sugar[idx] == 13.0
    assert agents.spicy[idx] == 13.0

def test_empty_cell_no_crash():
    """Функция не падает, если на клетке нет ресурсов или агента"""
    world = WorldState(size=1)
    world.sugar_map[0, 0] = 0
    world.spicy_map[0, 0] = 0
    world.occupancy[0, 0] = -1

    agents = AgentSystem(capacity=10)
    # Нет живых агентов
    ctx = {"world": world, "agents": agents}
    eat_strategy(ctx)
    assert True

def test_starvation_scenario():
    """Агент получает отрицательные или нулевые ресурсы, если метаболизм превышает запас"""
    world = WorldState(size=1)
    world.sugar_map[0, 0] = 0
    world.spicy_map[0, 0] = 0
    world.occupancy[0, 0] = 1

    agents = AgentSystem(capacity=10)
    idx = agents.spawn(id=1, x=0, y=0, data={"sugar": 1.0, "spicy": 1.0, "sugarm": 3.0, "spicym": 3.0})

    ctx = {"world": world, "agents": agents}
    eat_strategy(ctx)

    assert agents.sugar[idx] <= 0
    assert agents.spicy[idx] <= 0
