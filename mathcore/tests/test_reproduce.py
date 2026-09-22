import pytest
from reproduce import reproduce, get_empty_neighbors
from classes import create_agent, create_cell

def test_get_empty_neighbors():
    grid = [
        [create_cell(0, 0, 10, 10), create_cell(1, 0, 10, 10)],
        [create_cell(0, 1, 10, 10), create_cell(1, 1, 10, 10)]
    ]
    cell = grid[0][0]
    empty = get_empty_neighbors(cell, grid)
    assert len(empty) == 2
    assert grid[0][1] in empty
    assert grid[1][0] in empty

    # Occupy one
    grid[0][1]["agent_id"] = 99
    empty = get_empty_neighbors(cell, grid)
    assert len(empty) == 1
    assert grid[1][0] in empty

def test_reproduce_success():
    grid = [
        [create_cell(0, 0, 10, 10), create_cell(1, 0, 10, 10)],
        [create_cell(0, 1, 10, 10), create_cell(1, 1, 10, 10)]
    ]
    
    agent_a = create_agent(id=1, x=0, y=0, sugar=40, spicy=40)
    agent_b = create_agent(id=2, x=1, y=0, sugar=40, spicy=40)
    
    grid[0][0]["agent_id"] = 1
    grid[0][1]["agent_id"] = 2
    
    agents_map = {1: agent_a, 2: agent_b}
    
    next_id = reproduce(agent_a, agent_b, grid, agents_map, next_id=3)
    
    assert next_id == 4
    assert 3 in agents_map
    # Check parent resources deducted
    assert agent_a["sugar"] == 30
    assert agent_a["spicy"] == 30
    assert agent_b["sugar"] == 30
    assert agent_b["spicy"] == 30
    
    # Check child stats
    child = agents_map[3]
    assert child["sugar"] == 20
    assert child["spicy"] == 20
    # Child should be placed in an empty neighbor cell (e.g. at (0, 1) or (1, 1))
    child_cell = grid[child["y"]][child["x"]]
    assert child_cell["agent_id"] == 3

def test_reproduce_insufficient_resources():
    grid = [
        [create_cell(0, 0, 10, 10), create_cell(1, 0, 10, 10)],
        [create_cell(0, 1, 10, 10), create_cell(1, 1, 10, 10)]
    ]
    
    agent_a = create_agent(id=1, x=0, y=0, sugar=10, spicy=40) # Insufficient sugar
    agent_b = create_agent(id=2, x=1, y=0, sugar=40, spicy=40)
    
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
    
    agent_a = create_agent(id=1, x=0, y=0, sugar=40, spicy=40)
    agent_b = create_agent(id=2, x=1, y=0, sugar=40, spicy=40)
    agent_c = create_agent(id=3, x=0, y=1, sugar=10, spicy=10)
    agent_d = create_agent(id=4, x=1, y=1, sugar=10, spicy=10)
    
    grid[0][0]["agent_id"] = 1
    grid[0][1]["agent_id"] = 2
    grid[1][0]["agent_id"] = 3
    grid[1][1]["agent_id"] = 4
    
    agents_map = {1: agent_a, 2: agent_b, 3: agent_c, 4: agent_d}
    
    next_id = reproduce(agent_a, agent_b, grid, agents_map, next_id=5)
    
    # No empty neighbors anywhere around parents
    assert next_id == 5
    assert len(agents_map) == 4
