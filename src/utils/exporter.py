import json
import zipfile
from pathlib import Path

def save_simulation_archive(
    history: list[dict], 
    charts: dict[str, bytes], 
    metadata: dict, 
    filename: str = "sim_data.zip"
):
    """
    Чистая функция экспорта. Не знает ни об агентах, ни о графиках.
    Просто кладет байты в архив.
    """
    output_path = Path(filename)
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("metadata.json", json.dumps(metadata, indent=2))
        
        for step_data in history:
            idx = step_data.get("step", 0)
            zipf.writestr(f"step_{idx:04d}.json", json.dumps(step_data, ensure_ascii=False))
            
        for path, data in charts.items():
            zipf.writestr(path, data)
            
    return output_path.resolve()
