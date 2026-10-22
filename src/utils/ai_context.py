# src/utils/ai_context.py
from typing import Dict, Any, List
import numpy as np

def build_ai_context(step_data: Dict[str, Any]) -> str:
    """
    Генерирует компактный контекст для LLM из step_data.
    Расширяемость: новые механики добавляются как отдельные блоки ниже.
    """
    agents = step_data.get("agents", [])
    trades = step_data.get("raw_trades", [])
    sugar_map = np.array(step_data.get("sugar_map", []))
    spicy_map = np.array(step_data.get("spicy_map", []))
    
    if not agents:
        return f"[СИМУЛЯЦИЯ] Шаг {step_data['step']}: Популяция вымерла."

    # --- БЛОК 1: Демография и Ресурсы (Всегда актуален) ---
    pop_count = len(agents)
    avg_sugar = sum(a["sugar"] for a in agents) / pop_count
    avg_spicy = sum(a["spicy"] for a in agents) / pop_count
    
    # Агенты в критическом состоянии (сахар < метаболизма)
    starving = sum(1 for a in agents if a["sugar"] <= a["sugarm"])
    # Богачи (ресурсы > 2x среднего)
    rich_threshold = (avg_sugar + avg_spicy) * 2
    rich_agents = sum(1 for a in agents if (a["sugar"] + a["spicy"]) > rich_threshold)

    context_parts = [
        f"[СИМУЛЯЦИЯ] Шаг {step_data['step']}",
        f"- Популяция: {pop_count} агентов",
        f"- Средние ресурсы: Сахар={avg_sugar:.1f}, Специи={avg_spicy:.1f}",
        f"- Критическое состояние: {starving} агентов (сахар <= метаболизма)",
        f"- Элита (>2x ср. богатства): {rich_agents} агентов",
    ]

    # --- БЛОК 2: Торговая активность (Динамически из raw_trades) ---
    trade_volume = len(trades)
    unique_traders = len(set(t["seller_id"] for t in trades) | set(t["buyer_id"] for t in trades))
    
    if trade_volume > 0:
        total_sugar_traded = sum(t["sugar_qty"] for t in trades)
        total_spice_traded = sum(t["spice_qty"] for t in trades)
        avg_price = total_spice_traded / max(total_sugar_traded, 1)
        
        context_parts.append(f"- Торговля: {trade_volume} сделок, {unique_traders} участников")
        context_parts.append(f"- Оборот: {total_sugar_traded:.0f} Сахара за {total_spice_traded:.0f} Специй (Ср. цена: {avg_price:.2f})")
        
        # Пример сделки для конкретики
        sample = trades[0]
        context_parts.append(f"- Пример: Агент #{sample['seller_id']} продал {sample['sugar_qty']} Сах. агенту #{sample['buyer_id']} за {sample['spice_qty']} Спец.")

    # --- БЛОК 3: Состояние среды (Из карт, без передачи матриц) ---
    if sugar_map.size > 0 and spicy_map.size > 0:
        empty_cells = np.sum((sugar_map == 0) & (spicy_map == 0))
        total_cells = sugar_map.size
        richness_std = np.std(sugar_map + spicy_map) # Неравномерность распределения
        
        context_parts.append(f"- Среда: {empty_cells}/{total_cells} пустых клеток ({empty_cells/total_cells*100:.1f}%)")
        context_parts.append(f"- Неравномерность ресурсов (std): {richness_std:.1f}")

    # === ЗДЕСЬ ДОБАВЛЯТЬ НОВЫЕ ФИЧИ ===
    # Если завтра появится "налог":
    # if "tax_revenue" in step_data:
    #     context_parts.append(f"- Налоговые сборы: {step_data['tax_revenue']}")
    
    return "\n".join(context_parts)