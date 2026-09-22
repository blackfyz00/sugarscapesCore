import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aging import age_agent
from classes import create_agent, create_cell

def test_aging_normal_increment():
    cell = create_cell(0, 0, 10, 10)
    cell["agent_id"] = 1
    grid = [[cell]]
    
    agent = create_agent(id=1, x=0, y=0, age=10, max_age=50)
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
    
    agent = create_agent(id=1, x=0, y=0, age=49, max_age=50)
    agents_map = {1: agent}
    
    died = age_agent(agent, agents_map, grid)
    
    assert died
    assert agent["age"] == 50
    assert 1 not in agents_map
    assert grid[0][0]["agent_id"] is None

def test_aging_death_exceeds_max_age():
    cell = create_cell(0, 0, 10, 10)
    cell["agent_id"] = 2
    grid = [[cell]]
    
    agent = create_agent(id=2, x=0, y=0, age=80, max_age=75)
    agents_map = {2: agent}
    
    died = age_agent(agent, agents_map, grid)
    
    assert died
    assert 2 not in agents_map
    assert grid[0][0]["agent_id"] is None
