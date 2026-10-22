import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .metrics import calculate_gini

# Настройка шрифтов для кириллицы (раскомментируйте, если видите квадратики)
# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei'] 

def generate_agent_population_chart(steps: list, agent_counts: list) -> bytes:
    plt.figure(figsize=(8, 5))
    plt.plot(steps, agent_counts, label='Популяция агентов', color='blue', linewidth=2)
    plt.xlabel('Шаг')
    plt.ylabel('Количество')
    plt.title('Динамика популяции агентов во времени')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return buf.getvalue()

def generate_resources_chart(steps: list, total_sugar: list, total_spicy: list) -> bytes:
    plt.figure(figsize=(8, 5))
    plt.plot(steps, total_sugar, label='Всего сахара', color='orange', linewidth=2)
    plt.plot(steps, total_spicy, label='Всего пряностей', color='red', linewidth=2)
    plt.xlabel('Шаг')
    plt.ylabel('Количество ресурсов')
    plt.title('Динамика общих ресурсов во времени')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return buf.getvalue()

def generate_welfare_chart(steps: list, avg_welfare: list, gini_coeffs: list = None) -> bytes:
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    color_welfare = 'green'
    ax1.set_xlabel('Шаг')
    ax1.set_ylabel('Среднее благосостояние', color=color_welfare)
    ax1.plot(steps, avg_welfare, label='Ср. благосостояние', color=color_welfare, linewidth=2)
    ax1.tick_params(axis='y', labelcolor=color_welfare)
    
    if gini_coeffs:
        ax2 = ax1.twinx()
        color_gini = 'darkred'
        ax2.set_ylabel('Коэффициент Джини', color=color_gini)
        ax2.plot(steps, gini_coeffs, label='Неравенство (Джини)', color=color_gini, linewidth=2, linestyle='dashed')
        ax2.tick_params(axis='y', labelcolor=color_gini)
        ax2.set_ylim(0, 1)

    plt.title('Благосостояние и неравенство во времени')
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
    plt.grid(True, linestyle='--', alpha=0.3)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return buf.getvalue()

def generate_demographics_chart(steps: list, avg_age: list, births: list = None, deaths: list = None) -> bytes:
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    color_age = 'purple'
    ax1.set_xlabel('Шаг')
    ax1.set_ylabel('Средний возраст', color=color_age)
    ax1.plot(steps, avg_age, label='Ср. возраст', color=color_age, linewidth=2)
    ax1.tick_params(axis='y', labelcolor=color_age)
    
    if births and deaths:
        ax2 = ax1.twinx()
        ax2.set_ylabel('Естественное движение (кол-во)', color='gray')
        ax2.plot(steps, births, label='Рождения', color='lightgreen', linewidth=1.5)
        ax2.plot(steps, deaths, label='Смерти', color='salmon', linewidth=1.5)
        ax2.fill_between(steps, births, deaths, alpha=0.1, color='gray')

    plt.title('Демография: Возраст и естественное движение')
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
    plt.grid(True, linestyle='--', alpha=0.3)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return buf.getvalue()

def generate_wealth_distribution_chart(step_num: int, welfares: list) -> bytes:
    """Гистограмма распределения богатства на конкретном шаге."""
    plt.figure(figsize=(8, 5))
    plt.hist(welfares, bins=20, color='teal', edgecolor='black', alpha=0.7)
    plt.xlabel('Уровень благосостояния')
    plt.ylabel('Число агентов')
    plt.title(f'Распределение богатства на шаге {step_num}')
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return buf.getvalue()

# --- НОВАЯ ФУНКЦИЯ ДЛЯ ГРАФИКА ЦЕН ---
def generate_price_history_chart(steps: list, avg_sugar_prices: list, avg_spice_prices: list) -> bytes:
    """График динамики средних обменных курсов ресурсов."""
    plt.figure(figsize=(8, 5))
    
    # Фильтруем нули (шаги без сделок), чтобы график был чистым
    valid_indices = [i for i, p in enumerate(avg_sugar_prices) if p > 0]
    
    if not valid_indices:
        plt.text(0.5, 0.5, "Нет данных о торгах\n(или цены равны 0)", ha='center', va='center', fontsize=12, color='gray')
        plt.title("Динамика цен обмена")
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        return buf.getvalue()

    filtered_steps = [steps[i] for i in valid_indices]
    filtered_sugar_p = [avg_sugar_prices[i] for i in valid_indices]
    filtered_spice_p = [avg_spice_prices[i] for i in valid_indices]

    plt.plot(filtered_steps, filtered_sugar_p, label='Цена Сахара (в Специях)', color='orange', linewidth=2)
    plt.plot(filtered_steps, filtered_spice_p, label='Цена Специй (в Сахаре)', color='red', linewidth=2, linestyle='--')
    
    plt.xlabel('Шаг')
    plt.ylabel('Относительная цена')
    plt.title('Динамика средних обменных курсов')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return buf.getvalue()


def generate_charts(
    steps: list, 
    agent_counts: list, 
    total_sugar: list, 
    total_spicy: list, 
    avg_welfare: list = None, 
    avg_age: list = None,
    gini_coeffs: list = None,
    births: list = None,
    deaths: list = None,
    final_welfares: list = None,
    avg_sugar_prices: list = None,  # ДОБАВЛЕНО
    avg_spice_prices: list = None   # ДОБАВЛЕНО
) -> dict[str, bytes]:
    """
    Генерирует расширенный набор графиков симуляции.
    """
    charts = {}
    if not steps:
        return charts

    charts["graphs/agent_population.png"] = generate_agent_population_chart(steps, agent_counts)
    charts["graphs/resources_over_time.png"] = generate_resources_chart(steps, total_sugar, total_spicy)
    
    if avg_welfare is not None:
        charts["graphs/average_welfare.png"] = generate_welfare_chart(steps, avg_welfare, gini_coeffs)
        
    if avg_age is not None:
        charts["graphs/demographics.png"] = generate_demographics_chart(steps, avg_age, births, deaths)

    # Добавляем график цен, если данные есть
    if avg_sugar_prices is not None and avg_spice_prices is not None:
        charts["graphs/exchange_rates.png"] = generate_price_history_chart(steps, avg_sugar_prices, avg_spice_prices)

    # Добавляем снимок распределения богатства на последнем шаге
    if final_welfares:
        last_step = steps[-1] if steps else 0
        charts["graphs/final_wealth_dist.png"] = generate_wealth_distribution_chart(last_step, final_welfares)

    return charts

def render_charts_from_data(metrics_data: dict, final_welfares: list) -> dict[str, bytes]:
    """Принимает готовые словари и возвращает байты картинок."""
    
    welfare_key = "median_welfare" if "median_welfare" in metrics_data else "avg_welfare"
    age_key = "median_age" if "median_age" in metrics_data else "avg_age"

    return generate_charts(
        steps=metrics_data["steps"],
        agent_counts=metrics_data["agent_counts"],
        total_sugar=metrics_data["total_sugar"],
        total_spicy=metrics_data["total_spicy"],
        
        # Передаем данные под правильными именами параметров функции
        avg_welfare=metrics_data[welfare_key], 
        avg_age=metrics_data[age_key],
        
        gini_coeffs=metrics_data["gini_coeffs"],
        births=metrics_data["births"],
        deaths=metrics_data["deaths"],
        final_welfares=final_welfares,
        avg_sugar_prices=metrics_data.get("avg_sugar_prices"),
        avg_spice_prices=metrics_data.get("avg_spice_prices")
    )

import json
from pathlib import Path

def generate_html_dashboard(
    metrics_data: dict, 
    final_welfares: list, 
    output_path: str = "report.html"
) -> str:
    """
    Генерирует автономный HTML-дашборд, читая шаблон из templates/dashboard.html
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
    # Путь относительно текущего файла (src/utils/plotter.py -> src/templates/dashboard.html)
    template_dir = Path(__file__).parent.parent / "templates"
    template_path = template_dir / "dashboard.html"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 3. Подстановка данных
    # Мы используем уникальные маркеры, чтобы не конфликтовать с JS/CSS
    # В файле dashboard.html вместо {data_json_str} должно быть написано {{DATA_JSON}}
    html_content = html_content.replace("{{DATA_JSON}}", data_json_str)

    # 4. Запись результата
    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path_obj, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return str(path_obj.resolve())