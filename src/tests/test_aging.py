import pytest
from mechanics.aging.aging import age_agent
from mechanics.death.death import check_and_remove_agent
from classes import create_agent, create_cell

def test_aging_normal_increment():
    cell = create_cell(0, 0, 10, 10)
    cell["agent_id"] = 1
    grid = [[cell]]

    config = {"agent": {"age": 10, "max_age": 50, "sugar": 10, "spicy": 10}}
    agent = create_agent(id=1, x=0, y=0, config=config)
    agents_map = {1: agent}

    died = age_agent(agent, agents_map, grid)

    assert not died
    assert agent["age"] == 11
    assert 1 in agents_map
    assert grid[0][0]["agent_id"] == 1

def test_aging_death_by_old_age():
    cell = create_cell(0, 0, 10, 10)
    cell["agent_id"] = 1
    grid = [[cell]]

    config = {"agent": {"age": 49, "max_age": 50, "sugar": 10, "spicy": 10}}
    agent = create_agent(id=1, x=0, y=0, config=config)
    agents_map = {1: agent}

    # Шаг 1: Старение
    died = age_agent(agent, agents_map, grid)
    assert died
    assert agent["age"] == 50

    # Шаг 2: Удаление (отдельная механика)
    removed = check_and_remove_agent(1, agents_map, grid)
    assert removed
    assert 1 not in agents_map
    assert grid[0][0]["agent_id"] is None

def test_aging_death_exceeds_max_age():
    cell = create_cell(0, 0, 10, 10)
    cell["agent_id"] = 2
    grid = [[cell]]

    config = {"agent": {"age": 80, "max_age": 75, "sugar": 10, "spicy": 10}}
    agent = create_agent(id=2, x=0, y=0, config=config)
    agents_map = {2: agent}

    # Шаг 1: Старение
    died = age_agent(agent, agents_map, grid)
    assert died

    # Шаг 2: Удаление
    removed = check_and_remove_agent(2, agents_map, grid)
    assert removed
    assert 2 not in agents_map
    assert grid[0][0]["agent_id"] is None
