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
    
def trade(cell_a: dict, cell_b: dict, agents_map: dict) -> bool:
    id_a, id_b = cell_a.get("agent_id"), cell_b.get("agent_id")
    if id_a is None or id_b is None: return False
    a = agents_map[id_a]
    b = agents_map[id_b]
    a["is_trading"] = False
    b["is_trading"] = False
    mrs_a = calculate_mrs(a)
    mrs_b = calculate_mrs(b)
    
    if math.isclose(mrs_a, mrs_b): return False
    price = math.sqrt(mrs_a * mrs_b)
    if mrs_a > mrs_b:
        spice_seller = b  
        spice_buyer = a   
    else:
        spice_seller = a  
        spice_buyer = b   
    if price >= 1:
        sugar_ex = 1
        spice_ex = int(price)
    else:
        sugar_ex = int(1 / price)
        spice_ex = 1
    if sugar_ex == 0 or spice_ex == 0: return False
    if spice_seller["spicy"] < spice_ex or spice_buyer["sugar"] < sugar_ex:
        return False
        
    ss_sugar_new = spice_seller["sugar"] + sugar_ex
    ss_spicy_new = spice_seller["spicy"] - spice_ex
    sb_sugar_new = spice_buyer["sugar"] - sugar_ex
    sb_spicy_new = spice_buyer["spicy"] + spice_ex
    w_ss_old = calculate_welfare(spice_seller)
    w_sb_old = calculate_welfare(spice_buyer)
    w_ss_new = calculate_welfare({"sugar": ss_sugar_new, "spicy": ss_spicy_new, 
                                  "sugarm": spice_seller["sugarm"], "spicym": spice_seller["spicym"]})
    w_sb_new = calculate_welfare({"sugar": sb_sugar_new, "spicy": sb_spicy_new, 
                                  "sugarm": spice_buyer["sugarm"], "spicym": spice_buyer["spicym"]})
    both_better = (w_ss_new > w_ss_old) and (w_sb_new > w_sb_old)
    if not both_better: return False
    
    mrs_ss_new = calculate_mrs({"sugar": ss_sugar_new, "spicy": ss_spicy_new, 
                                "sugarm": spice_seller["sugarm"], "spicym": spice_seller["spicym"]})
    mrs_sb_new = calculate_mrs({"sugar": sb_sugar_new, "spicy": sb_spicy_new, 
                                "sugarm": spice_buyer["sugarm"], "spicym": spice_buyer["spicym"]})
    mrs_valid = mrs_sb_new >= mrs_ss_new
    if not mrs_valid: return False
    spice_seller["sugar"] += sugar_ex
    spice_seller["spicy"] -= spice_ex
    spice_buyer["sugar"] -= sugar_ex
    spice_buyer["spicy"] += spice_ex
    spice_seller["is_trading"] = True
    spice_buyer["is_trading"] = True
    return True