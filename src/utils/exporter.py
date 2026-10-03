import json
import zipfile
from pathlib import Path
import numpy as np

def save_simulation_archive(
    history: list[dict], 
    charts: dict[str, bytes], 
    metadata: dict, 
    filename: str = "sim_data.zip",
    world = None
):
    """
    Экспорт симуляции: сохраняет JSON метаданные, историю, графики 
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
            
        for path, data in charts.items():
            zipf.writestr(path, data)
            
    return output_path.resolve()
