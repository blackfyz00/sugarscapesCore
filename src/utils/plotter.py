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
    Генерирует автономный HTML-дашборд с использованием Plotly.js и Tailwind CSS.
    Не изменяет существующие функции генерации PNG.
    """
    
    # 1. Подготовка данных для JS
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
    
    # ВАЖНО: ensure_ascii=False сохраняет кириллицу в читаемом виде
    data_json_str = json.dumps(dashboard_data, ensure_ascii=False)

    # 2. HTML Шаблон
    html_template = f"""<!DOCTYPE html>
<html lang="ru" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sugarscape Analytics Dashboard</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        slate: {{ 950: '#020617' }}
                    }}
                }}
            }}
        }}
    </script>
    
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    
    <style>
        body {{ overflow-x: hidden; }}
        .chart-container {{ width: 100%; height: 400px; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300 font-sans antialiased">

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <header class="flex justify-between items-center mb-8 pb-4 border-b border-slate-200 dark:border-slate-800">
            <div>
                <h1 class="text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-emerald-500 bg-clip-text text-transparent">
                    Sugarscape Core
                </h1>
                <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Интерактивный аналитический отчет</p>
            </div>
            <button id="theme-toggle" class="p-2 rounded-lg bg-white dark:bg-slate-800 shadow-md hover:shadow-lg transition-all focus:outline-none ring-2 ring-blue-500/20">
                <span id="theme-icon">🌙</span>
            </button>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
                <p class="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">Финальная популяция</p>
                <p id="kpi-agents" class="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-2">--</p>
            </div>
            <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
                <p class="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">Медиана благосостояния</p>
                <p id="kpi-welfare" class="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-2">--</p>
            </div>
            <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
                <p class="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">Коэффициент Джини</p>
                <p id="kpi-gini" class="text-2xl font-bold text-red-600 dark:text-red-400 mt-2">--</p>
            </div>
             <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
                <p class="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">Всего шагов</p>
                <p id="kpi-steps" class="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-2">--</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 col-span-1 lg:col-span-2">
                <h3 class="text-lg font-semibold mb-4">Динамика популяции и демографии</h3>
                <div id="chart-population" class="chart-container"></div>
            </div>

            <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
                <h3 class="text-lg font-semibold mb-4">Общие ресурсы (Сахар/Специи)</h3>
                <div id="chart-resources" class="chart-container"></div>
            </div>

            <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
                <h3 class="text-lg font-semibold mb-4">Благосостояние и Неравенство</h3>
                <div id="chart-welfare" class="chart-container"></div>
            </div>

            <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
                <h3 class="text-lg font-semibold mb-4">Рыночные цены (Exchange Rates)</h3>
                <div id="chart-prices" class="chart-container"></div>
            </div>

            <div class="bg-white dark:bg-slate-900 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
                <h3 class="text-lg font-semibold mb-4">Распределение богатства (Final Step)</h3>
                <div id="chart-distribution" class="chart-container"></div>
            </div>
        </div>
        
        <footer class="mt-12 text-center text-xs text-slate-400 dark:text-slate-600">
            Generated by Simulation Core • Powered by Plotly & Tailwind
        </footer>
    </div>

    <script>
        const rawData = {data_json_str};

        const toggleBtn = document.getElementById('theme-toggle');
        const iconSpan = document.getElementById('theme-icon');
        const htmlEl = document.documentElement;
        let isDark = true;

        function updateChartsTheme() {{
            // Используем "плоские" ключи для надежного обновления вложенных осей Plotly
            const layoutUpdates = {{
                paper_bgcolor: isDark ? 'rgba(0,0,0,0)' : 'rgba(255,255,255,0)',
                plot_bgcolor: isDark ? 'rgba(0,0,0,0)' : 'rgba(255,255,255,0)',
                'font.color': isDark ? '#e2e8f0' : '#1e293b',
                'xaxis.gridcolor': isDark ? '#334155' : '#cbd5e1',
                'yaxis.gridcolor': isDark ? '#334155' : '#cbd5e1',
                'yaxis2.gridcolor': isDark ? '#334155' : '#cbd5e1'
            }};
            
            ['chart-population', 'chart-resources', 'chart-welfare', 'chart-prices', 'chart-distribution'].forEach(id => {{
                if(document.getElementById(id)) {{
                    Plotly.relayout(id, layoutUpdates);
                }}
            }});
        }}

        toggleBtn.addEventListener('click', () => {{
            isDark = !isDark;
            if(isDark) {{
                htmlEl.classList.add('dark');
                iconSpan.textContent = '🌙';
            }} else {{
                htmlEl.classList.remove('dark');
                iconSpan.textContent = '☀️';
            }}
            updateChartsTheme();
        }});

        function getBaseLayout(title) {{
            return {{
                title: {{ text: title, font: {{ size: 16 }} }},
                margin: {{ l: 50, r: 20, t: 40, b: 40 }},
                showlegend: true,
                legend: {{ orientation: 'h', y: -0.2 }},
                autosize: true,
                responsive: true
            }};
        }}

        function renderPopulationChart() {{
            const traceAgents = {{
                x: rawData.steps, y: rawData.agents, type: 'scatter', mode: 'lines+markers',
                name: 'Популяция', line: {{ color: '#3b82f6', width: 2 }}, marker: {{ size: 4 }}
            }};
            
            const traceBirths = {{
                x: rawData.steps, y: rawData.births, type: 'bar', name: 'Рождения',
                marker: {{ color: 'rgba(16, 185, 129, 0.6)' }}, visible: false
            }};
            
            const traceDeaths = {{
                x: rawData.steps, y: rawData.deaths.map(d => -d), type: 'bar', name: 'Смерти',
                marker: {{ color: 'rgba(239, 68, 68, 0.6)' }}, visible: false
            }};

            const layout = getBaseLayout('Динамика популяции');
            layout.yaxis = {{ title: 'Количество агентов' }};
            layout.yaxis2 = {{ title: 'Естественное движение', overlaying: 'y', side: 'right', rangemode: 'tozero' }};
            
            Plotly.newPlot('chart-population', [traceAgents, traceBirths, traceDeaths], layout);
        }}

        function renderResourcesChart() {{
            const traceSugar = {{ x: rawData.steps, y: rawData.sugar, type: 'scatter', mode: 'lines', name: 'Сахар', line: {{ color: '#f59e0b', width: 2 }} }};
            const traceSpicy = {{ x: rawData.steps, y: rawData.spicy, type: 'scatter', mode: 'lines', name: 'Специи', line: {{ color: '#ef4444', width: 2 }} }};
            Plotly.newPlot('chart-resources', [traceSugar, traceSpicy], getBaseLayout('Запасы ресурсов'));
        }}

        function renderWelfareChart() {{
            const traceWelfare = {{ x: rawData.steps, y: rawData.welfare, type: 'scatter', mode: 'lines', name: 'Медиана благосостояния', line: {{ color: '#10b981', width: 2 }} }};
            const traceGini = {{ x: rawData.steps, y: rawData.gini, type: 'scatter', mode: 'lines', name: 'Коэфф. Джини', line: {{ color: '#8b5cf6', dash: 'dashdot', width: 2 }}, yaxis: 'y2' }};

            const layout = getBaseLayout('Благосостояние и Неравенство');
            // ЗАЩИТА: Если массив пустой, Math.max вернет -Infinity и сломает график
            const maxWelfare = rawData.welfare.length > 0 ? Math.max(...rawData.welfare) : 100;
            layout.yaxis = {{ title: 'Уровень жизни', range: [0, maxWelfare * 1.1] }};
            layout.yaxis2 = {{ title: 'Неравенство (0-1)', overlaying: 'y', side: 'right', range: [0, 1] }};
            
            Plotly.newPlot('chart-welfare', [traceWelfare, traceGini], layout);
        }}

        function renderPricesChart() {{
            const validIndices = rawData.price_sugar.map((v, i) => v > 0 ? i : null).filter(i => i !== null);
            if(validIndices.length === 0) {{
                document.getElementById('chart-prices').innerHTML = '<div class="flex items-center justify-center h-full text-slate-400">Нет данных о торгах</div>';
                return;
            }}

            const filteredSteps = validIndices.map(i => rawData.steps[i]);
            const filteredSugarP = validIndices.map(i => rawData.price_sugar[i]);
            const filteredSpiceP = validIndices.map(i => rawData.price_spice[i]);

            const traceSugarPrice = {{ x: filteredSteps, y: filteredSugarP, type: 'scatter', mode: 'lines+markers', name: 'Цена Сахара (в Специях)', line: {{ color: '#f59e0b', width: 2 }}, marker: {{ size: 6 }} }};
            const traceSpicePrice = {{ x: filteredSteps, y: filteredSpiceP, type: 'scatter', mode: 'lines+markers', name: 'Цена Специй (в Сахаре)', line: {{ color: '#ef4444', width: 2, dash: 'dot' }}, marker: {{ size: 6 }} }};

            Plotly.newPlot('chart-prices', [traceSugarPrice, traceSpicePrice], getBaseLayout('Обменные курсы'));
        }}

        function renderDistributionChart() {{
            if(!rawData.final_wealth_dist || rawData.final_wealth_dist.length === 0) {{
                 document.getElementById('chart-distribution').innerHTML = '<div class="flex items-center justify-center h-full text-slate-400">Нет данных</div>';
                return;
            }}

            const traceHist = {{ x: rawData.final_wealth_dist, type: 'histogram', histnorm: 'probability density', marker: {{ color: '#3b82f6', opacity: 0.7 }}, nbinsx: 30 }};
            const layout = getBaseLayout('Гистограмма распределения благосостояния');
            layout.xaxis.title = 'Уровень благосостояния';
            layout.yaxis.title = 'Плотность вероятности';
            layout.showlegend = false;

            Plotly.newPlot('chart-distribution', [traceHist], layout);
        }}

        window.onload = () => {{
            // ЗАЩИТА: Безопасное обновление KPI без падения на .toFixed()
            if(rawData.agents && rawData.agents.length > 0) {{
                document.getElementById('kpi-agents').textContent = rawData.agents[rawData.agents.length - 1] || 0;
                const lastWelfare = rawData.welfare.length > 0 ? rawData.welfare[rawData.welfare.length - 1] : 0;
                const lastGini = rawData.gini.length > 0 ? rawData.gini[rawData.gini.length - 1] : 0;
                
                document.getElementById('kpi-welfare').textContent = lastWelfare.toFixed(2);
                document.getElementById('kpi-gini').textContent = lastGini.toFixed(3);
                document.getElementById('kpi-steps').textContent = rawData.steps.length;
            }}

            renderPopulationChart();
            renderResourcesChart();
            renderWelfareChart();
            renderPricesChart();
            renderDistributionChart();
            
            updateChartsTheme();
        }};
    </script>
</body>
</html>"""

    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path_obj, "w", encoding="utf-8") as f:
        f.write(html_template)
        
    return str(path_obj.resolve())