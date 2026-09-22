import pytest
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from classes import create_agent, create_cell
from trade import trade, calculate_mrs, calculate_welfare

def test_successful_trade():
    """Проверка базовой успешной сделки"""
    # Agent A: много сахара (20), мало спайси (5) → низкий MRS → ПРОДАЕТ сахар
    # Agent B: мало сахара (5), много спайси (20) → высокий MRS → ПОКУПАЕТ сахар
    agent_a = create_agent(id=1, x=0, y=0, sugar=20, spicy=5, sugarm=2, spicym=2)
    agent_b = create_agent(id=2, x=1, y=0, sugar=5, spicy=20, sugarm=2, spicym=2)
    
    cell_a = create_cell(posx=0, posy=0, sugar=0, spicy=0)
    cell_a["agent_id"] = 1
    cell_b = create_cell(posx=1, posy=0, sugar=0, spicy=0)
    cell_b["agent_id"] = 2
    
    agents_map = {1: agent_a, 2: agent_b}
    
    w_a_start = calculate_welfare(agent_a)
    w_b_start = calculate_welfare(agent_b)
    
    result = trade(cell_a, cell_b, agents_map, step=1)
    
    assert result is True
    assert calculate_welfare(agent_a) > w_a_start
    assert calculate_welfare(agent_b) > w_b_start
    
    # Проверяем фактические изменения ресурсов
    # Agent A продает сахар, покупает спайси
    assert agent_a["sugar"] < 20, "Agent A должен потерять сахар"
    assert agent_a["spicy"] > 5, "Agent A должен получить спайси"
    
    # Agent B покупает сахар, продает спайси
    assert agent_b["sugar"] > 5, "Agent B должен получить сахар"
    assert agent_b["spicy"] < 20, "Agent B должен потерять спайси"
    
    assert len(agent_a["history_trades"]) == 1
    assert len(agent_b["history_trades"]) == 1

def test_no_trade_if_same_mrs():
    """Торговля не происходит, если MRS агентов равны"""
    agent_a = create_agent(id=1, x=0, y=0, sugar=10, spicy=10, sugarm=2, spicym=2)
    agent_b = create_agent(id=2, x=1, y=0, sugar=10, spicy=10, sugarm=2, spicym=2)
    
    cell_a = create_cell(posx=0, posy=0, sugar=0, spicy=0)
    cell_a["agent_id"] = 1
    cell_b = create_cell(posx=1, posy=0, sugar=0, spicy=0)
    cell_b["agent_id"] = 2
    
    agents_map = {1: agent_a, 2: agent_b}
    
    result = trade(cell_a, cell_b, agents_map, step=1)
    assert result is False

def test_no_trade_if_buyer_lacks_spicy():
    """Торговля отменяется, если у покупателя нет спайси для оплаты"""
    # Agent A: должен купить сахар (высокий MRS)
    agent_a = create_agent(id=1, x=0, y=0, sugar=5, spicy=0, sugarm=2, spicym=2)
    # Agent B: должен продать сахар (низкий MRS)
    agent_b = create_agent(id=2, x=1, y=0, sugar=20, spicy=5, sugarm=2, spicym=2)
    
    cell_a = create_cell(posx=0, posy=0, sugar=0, spicy=0)
    cell_a["agent_id"] = 1
    cell_b = create_cell(posx=1, posy=0, sugar=0, spicy=0)
    cell_b["agent_id"] = 2
    
    agents_map = {1: agent_a, 2: agent_b}
    
    result = trade(cell_a, cell_b, agents_map, step=1)
    assert result is False, "Покупатель без спайси не может оплатить"

def test_no_trade_if_seller_lacks_sugar():
    """Торговля отменяется, если у продавца нет сахара"""
    agent_a = create_agent(id=1, x=0, y=0, sugar=20, spicy=5, sugarm=2, spicym=2)
    agent_b = create_agent(id=2, x=1, y=0, sugar=0, spicy=20, sugarm=2, spicym=2)
    
    cell_a = create_cell(posx=0, posy=0, sugar=0, spicy=0)
    cell_a["agent_id"] = 1
    cell_b = create_cell(posx=1, posy=0, sugar=0, spicy=0)
    cell_b["agent_id"] = 2
    
    agents_map = {1: agent_a, 2: agent_b}
    
    result = trade(cell_a, cell_b, agents_map, step=1)
    assert result is False, "Продавец без сахара не может продать"

def test_trade_history_recording():
    """Проверка корректности записи в историю сделок"""
    agent_a = create_agent(id=1, x=0, y=0, sugar=20, spicy=5, sugarm=2, spicym=2)
    agent_b = create_agent(id=2, x=1, y=0, sugar=5, spicy=20, sugarm=2, spicym=2)
    
    cell_a = create_cell(posx=0, posy=0, sugar=0, spicy=0)
    cell_a["agent_id"] = 1
    cell_b = create_cell(posx=1, posy=0, sugar=0, spicy=0)
    cell_b["agent_id"] = 2
    
    agents_map = {1: agent_a, 2: agent_b}
    
    trade(cell_a, cell_b, agents_map, step=5)
    
    record_a = agent_a["history_trades"][0]
    assert record_a["step"] == 5
    assert record_a["partner_id"] == 2
    assert "role" in record_a
    assert "sugar_change" in record_a
    assert "spicy_change" in record_a
    
    # Проверяем противоположные знаки изменений
    record_b = agent_b["history_trades"][0]
    assert record_a["sugar_change"] == -record_b["sugar_change"]
    assert record_a["spicy_change"] == -record_b["spicy_change"]

def test_no_trade_with_empty_cell():
    """Торговля не происходит, если в одной из клеток нет агента"""
    agent_a = create_agent(id=1, x=0, y=0, sugar=10, spicy=10, sugarm=2, spicym=2)
    
    cell_a = create_cell(posx=0, posy=0, sugar=0, spicy=0)
    cell_a["agent_id"] = 1
    cell_b = create_cell(posx=1, posy=0, sugar=0, spicy=0)
    
    agents_map = {1: agent_a}
    
    result = trade(cell_a, cell_b, agents_map, step=1)
    assert result is False

def test_no_trade_when_agent_meets_itself():
    """Торговля не происходит, если агент встречается сам с собой"""
    agent_a = create_agent(id=1, x=0, y=0, sugar=10, spicy=10, sugarm=2, spicym=2)
    
    cell_a = create_cell(posx=0, posy=0, sugar=0, spicy=0)
    cell_a["agent_id"] = 1
    cell_b = create_cell(posx=1, posy=0, sugar=0, spicy=0)
    cell_b["agent_id"] = 1  # Тот же агент!
    
    agents_map = {1: agent_a}
    
    result = trade(cell_a, cell_b, agents_map, step=1)
    assert result is False