# src/utils/metrics.py
import numpy as np
from .welfare_cobb import calculate_welfare_cobb_douglas

def calculate_gini(values: list) -> float:
    if not values or sum(values) == 0:
        return 0.0
    sorted_values = sorted(values)
    n = len(sorted_values)
    index = np.arange(1, n + 1)
    return float((np.sum((2 * index - n - 1) * sorted_values)) / (n * np.sum(sorted_values)))

def extract_step_metrics(step_data: dict, prev_agent_ids: set) -> tuple[dict, set]:
    """
    Извлекает метрики из одного шага.
    Данные о торгах берутся напрямую из step_data["raw_trades"].
    """
    agents = step_data.get("agents", {})
    agent_list = list(agents.values()) if isinstance(agents, dict) else agents
    
    current_ids = {a["id"] for a in agent_list if "id" in a}
    
    welfares = [
        calculate_welfare_cobb_douglas(
            sugar=a.get("sugar", 0.0),
            spicy=a.get("spicy", 0.0),
            sugarm=a.get("sugarm", 0.0),
            spicym=a.get("spicym", 0.0)
        ) 
        for a in agent_list
    ]
    ages = [a.get("age", 0) for a in agent_list]
    
    sugar_map = step_data.get("sugar_map", [])
    spicy_map = step_data.get("spicy_map", [])
    
    s_sum = sum(sum(row) for row in sugar_map) if sugar_map else 0
    sp_sum = sum(sum(row) for row in spicy_map) if spicy_map else 0

    # --- РАСЧЕТ ЦЕН ИЗ СТРУКТУРИРОВАННЫХ ДАННЫХ ---
    avg_sugar_price = 0.0
    avg_spice_price = 0.0
    
    raw_trades = step_data.get("raw_trades", [])
    
    if raw_trades:
        prices = []
        for t in raw_trades:
            sugar_amt = t.get("sugar_qty", 0)
            spice_amt = t.get("spice_qty", 0)
            
            if sugar_amt > 0:
                # Цена сахара в специях
                p = spice_amt / sugar_amt
                prices.append(p)
        
        if prices:
            avg_sugar_price = sum(prices) / len(prices)
            if avg_sugar_price > 0:
                avg_spice_price = 1.0 / avg_sugar_price

    metrics = {
        "step": step_data.get("step", 0),
        "count": len(agent_list),
        "sugar": s_sum,
        "spicy": sp_sum,
        "avg_welfare": sum(welfares) / len(welfares) if welfares else 0,
        "avg_age": sum(ages) / len(ages) if ages else 0,
        "gini": calculate_gini(welfares),
        "births": len(current_ids - prev_agent_ids),
        "deaths": len(prev_agent_ids - current_ids),
        "avg_sugar_price": avg_sugar_price,
        "avg_spice_price": avg_spice_price
    }
    
    return metrics, current_ids

def aggregate_metrics(history: list[dict]) -> tuple[dict, list]:
    """
    Принимает полную историю шагов.
    Теперь history содержит поле "raw_trades" в каждом элементе.
    """
    result = {
        "steps": [], "agent_counts": [], "total_sugar": [], "total_spicy": [],
        "avg_welfare": [], "avg_age": [], "gini_coeffs": [], 
        "births": [], "deaths": [],
        "avg_sugar_prices": [],
        "avg_spice_prices": []
    }
    
    prev_ids = set()
    final_welfares = []

    for i, step_data in enumerate(history):
        # Вызываем без дополнительного аргумента trades, так как они теперь внутри step_data
        m, prev_ids = extract_step_metrics(step_data, prev_ids)
        
        result["steps"].append(m["step"])
        result["agent_counts"].append(m["count"])
        result["total_sugar"].append(m["sugar"])
        result["total_spicy"].append(m["spicy"])
        result["avg_welfare"].append(m["avg_welfare"])
        result["avg_age"].append(m["avg_age"])
        result["gini_coeffs"].append(m["gini"])
        result["births"].append(m["births"])
        result["deaths"].append(m["deaths"])
        result["avg_sugar_prices"].append(m["avg_sugar_price"])
        result["avg_spice_prices"].append(m["avg_spice_price"])
        
        if i == len(history) - 1:
            agents = step_data.get("agents", {})
            agent_list = list(agents.values()) if isinstance(agents, dict) else agents
            final_welfares = [
                calculate_welfare_cobb_douglas(
                    sugar=a.get("sugar", 0.0),
                    spicy=a.get("spicy", 0.0),
                    sugarm=a.get("sugarm", 0.0),
                    spicym=a.get("spicym", 0.0)
                ) 
                for a in agent_list
            ]

    return result, final_welfares