import math

def calculate_welfare(agent: dict) -> float:
    """Cobb-Douglas Welfare Function"""
    m_total = agent["sugarm"] + agent["spicym"]
    if m_total == 0: return 0
    s = max(0, agent["sugar"])
    p = max(0, agent["spicy"])
    return (s ** (agent["sugarm"] / m_total)) * (p ** (agent["spicym"] / m_total))
    
def calculate_mrs(agent: dict) -> float:
    """Marginal Rate of Substitution"""
    if agent["sugar"] <= 0 or agent["sugarm"] <= 0: 
        return float('inf')
    return (agent["spicy"] / agent["spicym"]) / (agent["sugar"] / agent["sugarm"])
    
def trade(cell_a: dict, cell_b: dict, agents_map: dict, step: int) -> bool:
    id_a, id_b = cell_a.get("agent_id"), cell_b.get("agent_id")
    if id_a is None or id_b is None or id_a == id_b:
        return False
    
    a, b = agents_map[id_a], agents_map[id_b]
    mrs_a, mrs_b = calculate_mrs(a), calculate_mrs(b)
        
    if (math.isinf(mrs_a) or math.isinf(mrs_b) or 
            math.isclose(mrs_a, mrs_b) or
            mrs_a == 0 or mrs_b == 0): 
            return False
    
    # High MRS = values sugar more = BUY sugar
    if mrs_a > mrs_b:
        buyer, seller = a, b
    else:
        buyer, seller = b, a
    
    price = math.sqrt(mrs_a * mrs_b)
    
    if price >= 1:
        sugar_ex = 1
        spice_ex = max(1, int(price))
    else:
        sugar_ex = max(1, int(1 / price))
        spice_ex = 1
    
    # Check resources
    if seller["sugar"] < sugar_ex or buyer["spicy"] < spice_ex:
        return False
    
    # Calculate new states
    buyer_sugar_new = buyer["sugar"] + sugar_ex
    buyer_spicy_new = buyer["spicy"] - spice_ex
    seller_sugar_new = seller["sugar"] - sugar_ex
    seller_spicy_new = seller["spicy"] + spice_ex
    
    if buyer_spicy_new < 0 or seller_sugar_new < 0:
        return False
    
    # Pareto check
    w_buyer_old = calculate_welfare(buyer)
    w_seller_old = calculate_welfare(seller)
    
    state_buyer_new = {**buyer, "sugar": buyer_sugar_new, "spicy": buyer_spicy_new}
    state_seller_new = {**seller, "sugar": seller_sugar_new, "spicy": seller_spicy_new}
    
    if (calculate_welfare(state_buyer_new) <= w_buyer_old or 
        calculate_welfare(state_seller_new) <= w_seller_old):
        return False
    
    # Apply changes
    buyer.update({"sugar": buyer_sugar_new, "spicy": buyer_spicy_new, "is_trading": True})
    seller.update({"sugar": seller_sugar_new, "spicy": seller_spicy_new, "is_trading": True})
    
    # Record trades
    buyer["history_trades"].append({
        "step": step,
        "partner_id": seller["id"],
        "role": "buyer",
        "sugar_change": sugar_ex,
        "spicy_change": -spice_ex
    })
    
    seller["history_trades"].append({
        "step": step,
        "partner_id": buyer["id"],
        "role": "seller",
        "sugar_change": -sugar_ex,
        "spicy_change": spice_ex
    })
    
    return True
