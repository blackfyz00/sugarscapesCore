import shutil
import json
from pathlib import Path

def generate_html_dashboard(
    metrics_data: dict, 
    final_welfares: list, 
    output_path: str = "sim_data.html",
    excel_filename: str = None  
) -> str:
    """
    Генерирует автономный HTML-дашборд, читая шаблон из templates/sim_data.html
    """
    
    # 1. Подготовка данных для JS (как было раньше)
    steps = metrics_data.get("steps", [])
    agent_counts = metrics_data.get("agent_counts", [])
    total_sugar = metrics_data.get("total_sugar", [])
    total_spicy = metrics_data.get("total_spicy", [])
    
    welfare_key = "median_welfare" if "median_welfare" in metrics_data else "avg_welfare"
    age_key = "median_age" if "median_age" in metrics_data else "avg_age"
    
    welfares = metrics_data.get(welfare_key, [])
    ages = metrics_data.get(age_key, [])
    gini_coeffs = metrics_data.get("gini_coeffs", [])
    births = metrics_data.get("births", [])
    deaths = metrics_data.get("deaths", [])
    sugar_prices = metrics_data.get("avg_sugar_prices", [])
    spice_prices = metrics_data.get("avg_spice_prices", [])

    dashboard_data = {
        "steps": steps,
        "agents": agent_counts,
        "sugar": total_sugar,
        "spicy": total_spicy,
        "welfare": welfares,
        "age": ages,
        "gini": gini_coeffs,
        "births": births,
        "deaths": deaths,
        "price_sugar": sugar_prices,
        "price_spice": spice_prices,
        "final_wealth_dist": final_welfares
    }
    
    data_json_str = json.dumps(dashboard_data, ensure_ascii=False)

    # 2. Чтение шаблона
    template_dir = Path(__file__).parent.parent / "templates"
    template_path = template_dir / "dashboard.html"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 3. Подстановка данных
    html_content = html_content.replace("{{DATA_JSON}}", data_json_str)
    target_excel_name = excel_filename if excel_filename else "sim_data.xlsx"
    html_content = html_content.replace("{{EXCEL_FILENAME}}", target_excel_name)

    # 4. Копирование Excel-файла рядом с HTML (для работы ссылки file://)
    source_excel_path = Path(target_excel_name) # Предполагаем, что main.py создал его в текущей директории или указал путь
    
    # Если файл существует, копируем его в ту же папку, где будет лежать HTML
    if source_excel_path.exists():
        dest_dir = Path(output_path).parent
        dest_excel_path = dest_dir / target_excel_name
        
        # Копируем только если источники разные, чтобы избежать ошибки SameFileError
        if source_excel_path.resolve() != dest_excel_path.resolve():
            shutil.copy2(source_excel_path, dest_excel_path)
            print(f"📂 Copied Excel to: {dest_excel_path}")

    # 5. Запись результата
    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path_obj, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return str(path_obj.resolve())