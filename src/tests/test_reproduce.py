import pytest
import numpy as np
from core.world import WorldState
from core.agents import AgentSystem
from mechanics.reproduce.reproduce_strategy import reproduction_strategy

def test_reproduce_success():
    world = WorldState(size=2)
    world.occupancy.fill(-1)
    
    agents = AgentSystem(capacity=10)
    idx_a = agents.spawn(id=1, x=0, y=0, data={"sugar": 40.0, "spicy": 40.0, "vis": 2})
    idx_b = agents.spawn(id=2, x=1, y=0, data={"sugar": 40.0, "spicy": 40.0, "vis": 2})
    world.occupancy[0, 0] = 1
    world.occupancy[0, 1] = 2
    
    ctx = {
        "world": world,
        "agents": agents,
        "meta": {"next_agent_id": 3},
        "config": {}
    }
    params = {"minimal_resources": 20, "probability": 1.0, "max_child": 5}
    
    reproduction_strategy(ctx, params)
    
    # Проверяем, что у родителей вычлись ресурсы (40 * 0.2 = 8)
    assert agents.sugar[idx_a] == 32.0
    assert agents.spicy[idx_a] == 32.0
    assert agents.sugar[idx_b] == 32.0
    assert agents.spicy[idx_b] == 32.0
    
    # Проверяем появление третьего агента (ребенка)
    alive = agents.get_alive_indices()
    assert len(alive) == 3
    child_idx = [i for i in alive if i not in (idx_a, idx_b)][0]
    
    assert agents.sugar[child_idx] == 16.0  # 8 + 8
    assert agents.spicy[child_idx] == 16.0
    assert ctx["meta"]["next_agent_id"] == 4

def test_reproduce_insufficient_resources():
    world = WorldState(size=2)
    world.occupancy.fill(-1)
    
    agents = AgentSystem(capacity=10)
    agents.spawn(id=1, x=0, y=0, data={"sugar": 10.0, "spicy": 40.0, "vis": 2})
    agents.spawn(id=2, x=1, y=0, data={"sugar": 40.0, "spicy": 40.0, "vis": 2})
    world.occupancy[0, 0] = 1
    world.occupancy[0, 1] = 2
    
    ctx = {
        "world": world,
        "agents": agents,
        "meta": {"next_agent_id": 3},
        "config": {}
    }
    params = {"minimal_resources": 20, "probability": 1.0, "max_child": 5}
    
    reproduction_strategy(ctx, params)
    
    # Ребенок не должен появиться из-за нехватки ресурсов у первого агента
    assert len(agents.get_alive_indices()) == 2
    assert ctx["meta"]["next_agent_id"] == 3

def test_reproduce_no_empty_cell():
    world = WorldState(size=2)
    world.occupancy.fill(-1)
    
    agents = AgentSystem(capacity=10)
    agents.spawn(id=1, x=0, y=0, data={"sugar": 40.0, "spicy": 40.0, "vis": 2})
    agents.spawn(id=2, x=1, y=0, data={"sugar": 40.0, "spicy": 40.0, "vis": 2})
    agents.spawn(id=3, x=0, y=1, data={"sugar": 10.0, "spicy": 10.0, "vis": 2})
    agents.spawn(id=4, x=1, y=1, data={"sugar": 10.0, "spicy": 10.0, "vis": 2})
    
    world.occupancy[0, 0] = 1
    world.occupancy[0, 1] = 2
    world.occupancy[1, 0] = 3
    world.occupancy[1, 1] = 4
    
    ctx = {
        "world": world,
        "agents": agents,
        "meta": {"next_agent_id": 5},
        "config": {}
    }
    params = {"minimal_resources": 20, "probability": 1.0, "max_child": 5}
    
    reproduction_strategy(ctx, params)
    
    # Все клетки заняты, размножение невозможно
    assert len(agents.get_alive_indices()) == 4
    assert ctx["meta"]["next_agent_id"] == 5
