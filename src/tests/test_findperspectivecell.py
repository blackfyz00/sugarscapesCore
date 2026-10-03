import pytest
import numpy as np
from core.world import WorldState
from core.agents import AgentSystem
from mechanics.movement.findperspectivecell import find_perspective_cell_vectorized

def test_find_perspective_cell_success():
    """Поиск выбирает свободную клетку в пределах видимости с наилучшим благосостоянием"""
    world = WorldState(size=6)
    # Заполняем нулями
    world.sugar_map.fill(0)
    world.spicy_map.fill(0)
    world.occupancy.fill(-1)

    # Ставим агента в (1, 1), vis = 2
    agents = AgentSystem(capacity=10)
    agent_data = {"sugar": 10.0, "spicy": 10.0, "sugarm": 1.0, "spicym": 1.0, "vis": 2}
    idx1 = agents.spawn(agent_id=1, x=1, y=1, data=agent_data)
    world.occupancy[1, 1] = 1

    # Занятая клетка в зоне видимости (0, 1)
    world.occupancy[1, 0] = 2
    agents.spawn(agent_id=2, x=0, y=1, data={"sugar": 50.0, "spicy": 50.0})

    # Клетка в зоне видимости с хорошими ресурсами (2, 1)
    world.sugar_map[1, 2] = 10
    world.spicy_map[1, 2] = 10

    # Клетка в зоне видимости с меньшими ресурсами (1, 2)
    world.sugar_map[2, 1] = 1
    world.spicy_map[2, 1] = 1

    # Клетка вне зоны видимости (5, 5)
    world.sugar_map[5, 5] = 100
    world.spicy_map[5, 5] = 100

    find_perspective_cell_vectorized(world, agents)

    # Агент должен переместиться в (2, 1) — клетку с наилучшим благосостоянием в пределах vis=2
    assert agents.x[idx1] == 2
    assert agents.y[idx1] == 1
    assert world.occupancy[1, 1] == -1
    assert world.occupancy[1, 2] == 1

def test_find_perspective_cell_no_agent():
    """Если живых агентов нет, функция отрабатывает без ошибок"""
    world = WorldState(size=2)
    agents = AgentSystem(capacity=2)
    # Никого не спавним
    find_perspective_cell_vectorized(world, agents)
    assert True

def test_find_perspective_cell_no_visible_cells():
    """Если все клетки в зоне видимости заняты, агент остается на месте"""
    world = WorldState(size=2)
    world.occupancy.fill(-1)

    agents = AgentSystem(capacity=10)
    idx1 = agents.spawn(agent_id=1, x=0, y=0, data={"vis": 1, "sugar": 10.0, "spicy": 10.0})
    world.occupancy[0, 0] = 1

    # Единственный сосед (1, 0) занят
    idx2 = agents.spawn(agent_id=2, x=1, y=0, data={"vis": 1, "sugar": 10.0, "spicy": 10.0})
    world.occupancy[0, 1] = 2

    find_perspective_cell_vectorized(world, agents)

    assert agents.x[idx1] == 0
    assert agents.y[idx1] == 0
    assert world.occupancy[0, 0] == 1
