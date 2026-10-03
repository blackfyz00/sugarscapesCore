import pytest
import numpy as np
from core.world import WorldState
from core.agents import AgentSystem
from mechanics.movement.findperspectivecell import find_perspective_cell_vectorized

def test_successful_move():
    """Агент успешно перемещается на свободную клетку с лучшими ресурсами"""
    world = WorldState(size=2)
    world.occupancy.fill(-1)
    world.sugar_map[0, 0] = 0
    world.sugar_map[0, 1] = 10
    world.spicy_map[0, 0] = 0
    world.spicy_map[0, 1] = 10

    agents = AgentSystem(capacity=10)
    idx = agents.spawn(id=1, x=0, y=0, data={"vis": 1, "sugar": 10.0, "spicy": 10.0})
    world.occupancy[0, 0] = 1

    ctx = {"world": world, "agents": agents}
    find_perspective_cell_vectorized(world, agents)

    assert agents.x[idx] == 1
    assert agents.y[idx] == 0
    assert world.occupancy[0, 0] == -1
    assert world.occupancy[0, 1] == 1

def test_move_from_empty_cell():
    """Если агентов нет, векторизованное движение ничего не делает"""
    world = WorldState(size=2)
    agents = AgentSystem(capacity=10)
    find_perspective_cell_vectorized(world, agents)
    assert True

def test_move_to_occupied_cell():
    """Агент не может переместиться на занятую клетку"""
    world = WorldState(size=2)
    world.occupancy.fill(-1)
    # Клетка (0, 1) имеет больше ресурсов, но там стоит другой агент
    world.sugar_map[0, 1] = 100
    world.spicy_map[0, 1] = 100

    agents = AgentSystem(capacity=10)
    idx1 = agents.spawn(id=1, x=0, y=0, data={"vis": 1, "sugar": 10.0, "spicy": 10.0})
    idx2 = agents.spawn(id=2, x=0, y=1, data={"vis": 1, "sugar": 10.0, "spicy": 10.0})
    world.occupancy[0, 0] = 1
    world.occupancy[0, 1] = 2

    find_perspective_cell_vectorized(world, agents)

    # Агент 1 должен остаться на месте, т.к. единственный сосед занят
    assert agents.x[idx1] == 0
    assert agents.y[idx1] == 0
    assert world.occupancy[0, 0] == 1
