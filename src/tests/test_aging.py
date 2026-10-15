import pytest
from core.world import WorldState
from core.agents import AgentSystem
from mechanics.aging.aging_strategy import aging_strategy
from mechanics.death.death_strategy import death_strategy

def test_aging_normal_increment():
    world = WorldState(size=1)
    agents = AgentSystem(capacity=10)
    idx = agents.spawn(agent_id=1, x=0, y=0, data={"age": 10, "max_age": 50, "sugar": 10.0, "spicy": 10.0})
    world.occupancy[0, 0] = 1

    ctx = {"world": world, "agents": agents}
    aging_strategy(ctx)

    assert agents.age[idx] == 11
    assert agents.alive_mask[idx] == True
    assert world.occupancy[0, 0] == 1

def test_aging_death_by_old_age():
    world = WorldState(size=1)
    agents = AgentSystem(capacity=10)
    idx = agents.spawn(agent_id=1, x=0, y=0, data={"age": 49, "max_age": 50, "sugar": 10.0, "spicy": 10.0})
    world.occupancy[0, 0] = 1

    ctx = {"world": world, "agents": agents}
    
    # Шаг 1: Старение (возраст станет 50, что >= max_age)
    aging_strategy(ctx)
    assert agents.age[idx] == 50

    # Шаг 2: Смерть
    death_strategy(ctx)
    assert agents.alive_mask[idx] == False
    assert world.occupancy[0, 0] == -1

def test_aging_death_exceeds_max_age():
    world = WorldState(size=1)
    agents = AgentSystem(capacity=10)
    idx = agents.spawn(agent_id=2, x=0, y=0, data={"age": 80, "max_age": 75, "sugar": 10.0, "spicy": 10.0})
    world.occupancy[0, 0] = 2

    ctx = {"world": world, "agents": agents}
    
    aging_strategy(ctx)
    death_strategy(ctx)

    assert agents.alive_mask[idx] == False
    assert world.occupancy[0, 0] == -1
