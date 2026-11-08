import json
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict, List, Any

def save_simulation_archive(
    history: list[dict], 
    metadata: dict, 
    filename: str = "sim_data.zip",
    world = None
):
    """
    Экспорт симуляции: сохраняет JSON метаданные, историю
    и бинарные NumPy файлы (.npy) для быстрой загрузки в Godot.
    """
    output_path = Path(filename)
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("metadata.json", json.dumps(metadata, indent=2))
        
        for step_data in history:
            idx = step_data.get("step", 0)
            zipf.writestr(f"step_{idx:04d}.json", json.dumps(step_data, ensure_ascii=False))
            
        # Если передан world, сохраняем финальные карты в бинарном формате .npy для Godot
        if world is not None:
            import io
            sugar_bytes = io.BytesIO()
            np.save(sugar_bytes, world.sugar_map)
            zipf.writestr("final_sugar_map.npy", sugar_bytes.getvalue())

            spicy_bytes = io.BytesIO()
            np.save(spicy_bytes, world.spicy_map)
            zipf.writestr("final_spicy_map.npy", spicy_bytes.getvalue())

            occupancy_bytes = io.BytesIO()
            np.save(occupancy_bytes, world.occupancy)
            zipf.writestr("final_occupancy.npy", occupancy_bytes.getvalue())
            
    return output_path.resolve()

def export_to_excel(
    metrics_data: dict, 
    simulation_history: List[Dict[str, Any]], 
    filename: str = "sim_data.xlsx"
):
    """
    Создает Excel файл с детальными данными симуляции.
    """
    output_path = Path(filename)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        summary_df = pd.DataFrame({
            "Step": metrics_data["steps"],
            "Agent Count": metrics_data["agent_counts"],
            "Total Sugar": metrics_data["total_sugar"],
            "Total Spicy": metrics_data["total_spicy"],
            "Median Welfare": metrics_data["median_welfare"],
            "Median Age": metrics_data["median_age"],
            "Gini Coefficient": metrics_data["gini_coeffs"],
            "Births": metrics_data["births"],
            "Deaths": metrics_data["deaths"],
            "Avg Sugar Price": metrics_data["avg_sugar_prices"],
        })
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        # ==========================================
        # 2. Trades Log (Детальная история сделок)
        # ==========================================
        all_trades = []
        for step_data in simulation_history:
            raw_trades = step_data.get("raw_trades", [])
            for trade in raw_trades:
                # Добавляем номер шага к каждой сделке
                record = {
                    "Step": step_data["step"],
                    "Seller ID": trade["seller_id"],
                    "Buyer ID": trade["buyer_id"],
                    "Spice Qty": trade["spice_qty"]
                }
                all_trades.append(record)
        
        if all_trades:
            trades_df = pd.DataFrame(all_trades)
            trades_df.to_excel(writer, sheet_name="Trades Log", index=False)
        else:
            # Создаем пустой лист с заголовками, если сделок не было
            pd.DataFrame(columns=["Step", "Seller ID", "Buyer ID", "Spice Qty"]).to_excel(
                writer, sheet_name="Trades Log", index=False
            )

        # ==========================================
        # 3. Agents Final State (Состояние агентов на последнем шаге)
        # ==========================================
        # Можно заменить -1 на конкретный индекс шага, если нужно другое состояние
        last_step_idx = len(simulation_history) - 1
        
        if last_step_idx >= 0 and simulation_history[last_step_idx].get("agents"):
            agents_list = simulation_history[last_step_idx]["agents"]
            
            # Преобразуем список словарей в DataFrame
            # Важно: некоторые поля могут отсутствовать у некоторых агентов, pandas обработает это как NaN
            agents_df = pd.DataFrame(agents_list)
            
            # Упорядочиваем колонки для читаемости
            preferred_cols = ["id", "x", "y", "sugar", "spicy", "age", "max_age", "children_count", "vis"]
            existing_cols = [c for c in preferred_cols if c in agents_df.columns]
            other_cols = [c for c in agents_df.columns if c not in existing_cols]
            
            agents_df = agents_df[existing_cols + other_cols]
            agents_df.to_excel(writer, sheet_name="Agents Final State", index=False)

    return output_path.resolve()