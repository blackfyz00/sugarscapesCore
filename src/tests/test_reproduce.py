import pytest
from mechanics.reproduce.reproduce import reproduce, get_empty_neighbors
from classes import create_agent, create_cell

def test_get_empty_neighbors():
    grid = [
        [create_cell(0, 0, 10, 10), create_cell(1, 0, 10, 10)],
        [create_cell(0, 1, 10, 10), create_cell(1, 1, 10, 10)]
    ]
    cell = grid[0][0]
    empty = get_empty_neighbors(cell, grid)
    
    # ИСПРАВЛЕНО: Ожидаем 3 соседа (правый, нижний и диагональный右下)
    assert len(empty) == 3
    assert grid[0][1] in empty
    assert grid[1][0] in empty
    assert grid[1][1] in empty # Диагональ тоже считается соседом

    # Occupy one
    grid[0][1]["agent_id"] = 99
    empty = get_empty_neighbors(cell, grid)
    # Теперь осталось 2 свободных соседа
    assert len(empty) == 2
    assert grid[1][0] in empty
    assert grid[1][1] in empty

def test_reproduce_success():
    grid = [
        [create_cell(0, 0, 10, 10), create_cell(1, 0, 10, 10)],
        [create_cell(0, 1, 10, 10), create_cell(1, 1, 10, 10)]
    ]
    
    config = {"agent": {"sugar": 40, "spicy": 40, "vis": 2}}
    agent_a = create_agent(id=1, x=0, y=0, config=config)
    agent_b = create_agent(id=2, x=1, y=0, config=config)
    
    grid[0][0]["agent_id"] = 1
    grid[0][1]["agent_id"] = 2
    
    agents_map = {1: agent_a, 2: agent_b}
    
    next_id = reproduce(agent_a, agent_b, grid, agents_map, next_id=3)
    
    assert next_id == 4
    assert 3 in agents_map
    # Check parent resources deducted (40 * 0.2 = 8)
    assert agent_a["sugar"] == 32
    assert agent_a["spicy"] == 32
    assert agent_b["sugar"] == 32
    assert agent_b["spicy"] == 32
    
    # Check child stats (8 + 8 = 16)
    child = agents_map[3]
    assert child["sugar"] == 16
    assert child["spicy"] == 16
    child_cell = grid[child["y"]][child["x"]]
    assert child_cell["agent_id"] == 3

def test_reproduce_insufficient_resources():
    grid = [
        [create_cell(0, 0, 10, 10), create_cell(1, 0, 10, 10)],
        [create_cell(0, 1, 10, 10), create_cell(1, 1, 10, 10)]
    ]
    
    agent_a = create_agent(id=1, x=0, y=0, config={"agent": {"sugar": 10, "spicy": 40, "vis": 2}})
    agent_b = create_agent(id=2, x=1, y=0, config={"agent": {"sugar": 40, "spicy": 40, "vis": 2}})
    
    grid[0][0]["agent_id"] = 1
    grid[0][1]["agent_id"] = 2
    
    agents_map = {1: agent_a, 2: agent_b}
    
    next_id = reproduce(agent_a, agent_b, grid, agents_map, next_id=3)
    
    assert next_id == 3
    assert len(agents_map) == 2

def test_reproduce_no_empty_cell():
    grid = [
        [create_cell(0, 0, 10, 10), create_cell(1, 0, 10, 10)],
        [create_cell(0, 1, 10, 10), create_cell(1, 1, 10, 10)]
    ]
    
    config = {"agent": {"sugar": 40, "spicy": 40, "vis": 2}}
    agent_a = create_agent(id=1, x=0, y=0, config=config)
    agent_b = create_agent(id=2, x=1, y=0, config=config)
    agent_c = create_agent(id=3, x=0, y=1, config={"agent": {"sugar": 10, "spicy": 10, "vis": 2}})
    agent_d = create_agent(id=4, x=1, y=1, config={"agent": {"sugar": 10, "spicy": 10, "vis": 2}})
    
    grid[0][0]["agent_id"] = 1
    grid[0][1]["agent_id"] = 2
    grid[1][0]["agent_id"] = 3
    grid[1][1]["agent_id"] = 4
    
    agents_map = {1: agent_a, 2: agent_b, 3: agent_c, 4: agent_d}
    
    next_id = reproduce(agent_a, agent_b, grid, agents_map, next_id=5)
    
    assert next_id == 5
    assert len(agents_map) == 4
