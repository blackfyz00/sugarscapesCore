import math
from utils.welfare_cobb import calculate_welfare_cobb_douglas as calc_welfare_util

def calculate_welfare(agent: dict) -> float:
    """Рассчитывает полезность агента (Cobb-Douglas)."""
    return calc_welfare_util(
        agent["sugar"], 
        agent["spicy"], 
        agent["sugarm"], 
        agent["spicym"]
    )
    
def calculate_mrs(agent: dict) -> float:
    """
    Предельная норма замещения (MRS).
    Показывает, сколько специй агент готов отдать за единицу сахара.
    """
    # Защита от деления на ноль и отрицательных ресурсов
    if agent["sugar"] <= 0 or agent["sugarm"] <= 0 or agent["spicy"] <= 0 or agent["spicym"] <= 0: 
        return 0.0 
        
    # MRS = (MU_sugar / MU_spicy) ~ (spicy/spicym) / (sugar/sugarm)
    return (agent["spicy"] / agent["spicym"]) / (agent["sugar"] / agent["sugarm"])
    
def trade(cell_a: dict, cell_b: dict, agents_map: dict, step: int) -> bool:
    """
    Совершает сделку между двумя агентами, если она выгодна обоим (Парето-улучшение).
    """
    id_a, id_b = cell_a.get("agent_id"), cell_b.get("agent_id")
    
    # Базовые проверки
    if id_a is None or id_b is None or id_a == id_b:
        return False
    
    if id_a not in agents_map or id_b not in agents_map:
        return False
        
    a, b = agents_map[id_a], agents_map[id_b]
    
    # Агенты с нулевыми или отрицательными ресурсами не торгуют
    if a["sugar"] <= 0 or a["spicy"] <= 0 or b["sugar"] <= 0 or b["spicy"] <= 0:
        return False

    mrs_a = calculate_mrs(a)
    mrs_b = calculate_mrs(b)
    
    # Если MRS равны или некорректны,_trade_ нет смысла
    if mrs_a == 0 or mrs_b == 0 or math.isclose(mrs_a, mrs_b, rel_tol=1e-9):
        return False
    
    # Определяем покупателя и продавца
    # Высокий MRS означает, что агент высоко ценит сахар (готов много отдать за него) -> Он ПОКУПАТЕЛЬ сахара
    if mrs_a > mrs_b:
        buyer, seller = a, b
    else:
        buyer, seller = b, a
    
    # Расчет цены (геометрическое среднее MRS)
    price = math.sqrt(mrs_a * mrs_b)
    
    # Определение объема обмена
    # Чтобы избежать слишком крупных сделок, ограничим базовый объем 1 единицей
    # Корректируем вторую валюту относительно цены
    if price >= 1:
        amount_sugar = 1
        amount_spicy = max(1, round(price))
    else:
        amount_sugar = max(1, round(1 / price))
        amount_spicy = 1
        
    # Проверка наличия ресурсов у участников
    # Продавец продает сахар, Покупатель платит специями
    if seller["sugar"] < amount_sugar or buyer["spicy"] < amount_spicy:
        return False
    
    # Расчет новых состояний
    new_buyer_sugar = buyer["sugar"] + amount_sugar
    new_buyer_spicy = buyer["spicy"] - amount_spicy
    new_seller_sugar = seller["sugar"] - amount_sugar
    new_seller_spicy = seller["spicy"] + amount_spicy
    
    # Финальная защита от ухода в минус (на всякий случай)
    if new_buyer_spicy < 0 or new_seller_sugar < 0:
        return False
    
    # Проверка Парето-эффективности (сделка должна улучшать жизнь обоим)
    w_buyer_old = calculate_welfare(buyer)
    w_seller_old = calculate_welfare(seller)
    
    # Временные словари для расчета новой полезности
    buyer_new_state = {**buyer, "sugar": new_buyer_sugar, "spicy": new_buyer_spicy}
    seller_new_state = {**seller, "sugar": new_seller_sugar, "spicy": new_seller_spicy}
    
    w_buyer_new = calculate_welfare(buyer_new_state)
    w_seller_new = calculate_welfare(seller_new_state)
    
    # Если хотя бы одному стало хуже или так же — отмена
    if w_buyer_new <= w_buyer_old or w_seller_new <= w_seller_old:
        return False
    
    # --- Применение изменений ---
    
    # Обновляем ресурсы
    buyer["sugar"] = new_buyer_sugar
    buyer["spicy"] = new_buyer_spicy
    seller["sugar"] = new_seller_sugar
    seller["spicy"] = new_seller_spicy
    
    # Помечаем как участвовавших в торговле (для стратегии)
    buyer["is_trading"] = True
    seller["is_trading"] = True
    
    # Запись в историю сделок
    trade_record_buyer = {
        "step": step,
        "partner_id": seller["id"],
        "role": "buyer",
        "sugar_change": amount_sugar,
        "spicy_change": -amount_spicy
    }
    
    trade_record_seller = {
        "step": step,
        "partner_id": buyer["id"],
        "role": "seller",
        "sugar_change": -amount_sugar,
        "spicy_change": amount_spicy
    }
    
    # Безопасное добавление в историю
    if "history_trades" not in buyer:
        buyer["history_trades"] = []
    if "history_trades" not in seller:
        seller["history_trades"] = []
        
    buyer["history_trades"].append(trade_record_buyer)
    seller["history_trades"].append(trade_record_seller)
    
    return True
