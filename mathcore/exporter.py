import json
import zipfile
from pathlib import Path

def export_simulation_to_zip(simulation_history: list, grid_size: int, output_filename: str = "sim_data.zip"):
    """
    Экспортирует историю симуляции в ZIP-архив (План Б из arch.md).
    Содержит metadata.json и покадровые файлы step_XXXX.json.
    """
    output_path = Path(output_filename)
    print(f"📦 Создание ZIP-архива симуляции: {output_path}...")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Записываем метаданные
        metadata = {
            "total_steps": len(simulation_history),
            "grid_width": grid_size,
            "grid_height": grid_size
        }
        zipf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))

        # 2. Записываем каждый шаг в отдельный JSON-файл внутри архива
        for step_data in simulation_history:
            step_num = step_data["step"]
            filename = f"step_{step_num:04d}.json"
            step_json_str = json.dumps(step_data, ensure_ascii=False)
            zipf.writestr(filename, step_json_str)

    print(f"✅ Экспорт в ZIP завершен! Файл: {output_path.resolve()}")
