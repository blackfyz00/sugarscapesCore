# src/mechanics/trade/trade.py
import numpy as np

def trade_vectorized(world, agents) -> dict:
    """
    Векторизованная торговля с защитой от NaN и проверкой ресурсов.
    """
    trade_details = {}
    alive = agents.get_alive_indices()
    if len(alive) < 2:
        return trade_details
        
    id_to_idx = {int(agents.id[i]): i for i in alive}
    
    xs = agents.x[alive]
    ys = agents.y[alive]
    ids = agents.id[alive]
    occupancy = world.occupancy
    size = world.size
    
    # Используем все 8 направлений для честности, как в размножении
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    traded_set = set()
    
    for i, idx in enumerate(alive):
        aid = int(ids[i])
        if aid in traded_set:
            continue
            
        x, y = int(xs[i]), int(ys[i])
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                neighbor_aid = occupancy[ny, nx]
                
                # Проверка: клетка занята, это не мы, и партнер еще не торговал
                if neighbor_aid != -1 and neighbor_aid != aid and neighbor_aid not in traded_set:
                    n_idx = id_to_idx.get(neighbor_aid)
                    if n_idx is None:
                        continue
                        
                    s_a, sp_a = agents.sugar[idx], agents.spicy[idx]
                    s_b, sp_b = agents.sugar[n_idx], agents.spicy[n_idx]
                    
                    # Строгая проверка на положительность ресурсов
                    if s_a <= 0 or sp_a <= 0 or s_b <= 0 or sp_b <= 0:
                        continue
                        
                    # Расчет MRS (Marginal Rate of Substitution)
                    # Защита от деления на ноль уже обеспечена проверкой выше, 
                    # но добавим защиту от NaN/Inf на всякий случай
                    try:
                        mrs_a = (sp_a * agents.sugarm[idx]) / (s_a * agents.spicym[idx])
                        mrs_b = (sp_b * agents.sugarm[n_idx]) / (s_b * agents.spicym[n_idx])
                        
                        if not (np.isfinite(mrs_a) and np.isfinite(mrs_b)):
                            continue
                    except:
                        continue
                    
                    if np.isclose(mrs_a, mrs_b, rtol=1e-5):
                        continue
                        
                    # Определяем покупателя и продавца
                    if mrs_a > mrs_b:
                        buyer_idx, seller_idx = idx, n_idx
                        buyer_id, seller_id = aid, neighbor_aid
                    else:
                        buyer_idx, seller_idx = n_idx, idx
                        buyer_id, seller_id = neighbor_aid, aid
                        
                    # Цена сделки (геометрическое среднее MRS)
                    price = np.sqrt(abs(mrs_a * mrs_b))
                    amount_sugar = 1
                    amount_spicy = max(1, int(np.round(price)))
                    
                    # Проверка возможности сделки
                    if agents.sugar[seller_idx] >= amount_sugar and agents.spicy[buyer_idx] >= amount_spicy:
                        # Обновляем ресурсы
                        agents.sugar[seller_idx] -= amount_sugar
                        agents.spicy[seller_idx] += amount_spicy
                        agents.sugar[buyer_idx] += amount_sugar
                        agents.spicy[buyer_idx] -= amount_spicy
                        
                        agents.is_trading[idx] = True
                        agents.is_trading[n_idx] = True
                        traded_set.add(aid)
                        traded_set.add(neighbor_aid)
                        
                        trade_text = f"Купил {amount_sugar} сах. за {amount_spicy} спец."
                        
                        trade_details[aid] = {
                            "partner_id": neighbor_aid,
                            "text": trade_text
                        }
                        trade_details[neighbor_aid] = {
                            "partner_id": aid,
                            "text": trade_text
                        }
                        break 
    return trade_details
