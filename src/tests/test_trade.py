import pytest
import numpy as np
from core.world import WorldState
from core.agents import AgentSystem
from mechanics.trade.trade_cobb_strategy import trading_strategy
from utils.welfare_cobb import calculate_welfare_cobb_douglas

def test_successful_trade():
    """Проверка базовой успешной сделки в векторизованной архитектуре"""
    world = WorldState(size=2)
    world.occupancy.fill(-1)

    agents = AgentSystem(capacity=10)
    # Агент A: много сахара, мало специй
    idx_a = agents.spawn(id=1, x=0, y=0, data={"sugar": 20.0, "spicy": 5.0, "sugarm": 2.0, "spicym": 2.0})
    # Агент B: мало сахара, много специй (сосед в (1,0))
    idx_b = agents.spawn(id=2, x=1, y=0, data={"sugar": 5.0, "spicy": 20.0, "sugarm": 2.0, "spicym": 2.0})
    
    world.occupancy[0, 0] = 1
    world.occupancy[0, 1] = 2

    w_a_start = calculate_welfare_cobb_douglas(agents.sugar[idx_a], agents.spicy[idx_a], agents.sugarm[idx_a], agents.spicym[idx_a])
    w_b_start = calculate_welfare_cobb_douglas(agents.sugar[idx_b], agents.spicy[idx_b], agents.sugarm[idx_b], agents.spicym[idx_b])

    ctx = {
        "enable_trade": True,
        "world": world,
        "agents": agents,
        "step": 1
    }

    trading_strategy(ctx)

    w_a_end = calculate_welfare_cobb_douglas(agents.sugar[idx_a], agents.spicy[idx_a], agents.sugarm[idx_a], agents.spicym[idx_a])
    w_b_end = calculate_welfare_cobb_douglas(agents.sugar[idx_b], agents.spicy[idx_b], agents.sugarm[idx_b], agents.spicym[idx_b])

    assert w_a_end > w_a_start
    assert w_b_end > w_b_start

def test_no_trade_if_same_mrs():
    """Торговля не происходит, если MRS агентов равны"""
    world = WorldState(size=2)
    world.occupancy.fill(-1)

    agents = AgentSystem(capacity=10)
    idx_a = agents.spawn(id=1, x=0, y=0, data={"sugar": 10.0, "spicy": 10.0, "sugarm": 2.0, "spicym": 2.0})
    idx_b = agents.spawn(id=2, x=1, y=0, data={"sugar": 10.0, "spicy": 10.0, "sugarm": 2.0, "spicym": 2.0})
    
    world.occupancy[0, 0] = 1
    world.occupancy[0, 1] = 2

    s_a_start = agents.sugar[idx_a]
    s_b_start = agents.sugar[idx_b]

    ctx = {
        "enable_trade": True,
        "world": world,
        "agents": agents,
        "step": 1
    }

    trading_strategy(ctx)

    # Ничего не должно измениться
    assert agents.sugar[idx_a] == s_a_start
    assert agents.sugar[idx_b] == s_b_start
