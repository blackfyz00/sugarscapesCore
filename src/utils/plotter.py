import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .metrics import calculate_gini

def generate_agent_population_chart(steps: list, agent_counts: list) -> bytes:
    plt.figure(figsize=(8, 5))
    plt.plot(steps, agent_counts, label='Agent Population', color='blue', linewidth=2)
    plt.xlabel('Step')
    plt.ylabel('Count')
    plt.title('Agent Population Over Time')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return buf.getvalue()

def generate_resources_chart(steps: list, total_sugar: list, total_spicy: list) -> bytes:
    plt.figure(figsize=(8, 5))
    plt.plot(steps, total_sugar, label='Total Sugar', color='orange', linewidth=2)
    plt.plot(steps, total_spicy, label='Total Spicy', color='red', linewidth=2)
    plt.xlabel('Step')
    plt.ylabel('Resource Amount')
    plt.title('Total Resources Over Time')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return buf.getvalue()

def generate_welfare_chart(steps: list, avg_welfare: list, gini_coeffs: list = None) -> bytes:
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    # Основное ось: Среднее благосостояние
    color_welfare = 'green'
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Average Welfare', color=color_welfare)
    ax1.plot(steps, avg_welfare, label='Avg Welfare', color=color_welfare, linewidth=2)
    ax1.tick_params(axis='y', labelcolor=color_welfare)
    
    # Вторая ось: Коэффициент Джини (если передан)
    if gini_coeffs:
        ax2 = ax1.twinx()
        color_gini = 'darkred'
        ax2.set_ylabel('Gini Coefficient', color=color_gini)
        ax2.plot(steps, gini_coeffs, label='Inequality (Gini)', color=color_gini, linewidth=2, linestyle='dashed')
        ax2.tick_params(axis='y', labelcolor=color_gini)
        ax2.set_ylim(0, 1)

    plt.title('Welfare & Inequality Over Time')
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
    plt.grid(True, linestyle='--', alpha=0.3)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return buf.getvalue()

def generate_demographics_chart(steps: list, avg_age: list, births: list = None, deaths: list = None) -> bytes:
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    color_age = 'purple'
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Average Age', color=color_age)
    ax1.plot(steps, avg_age, label='Avg Age', color=color_age, linewidth=2)
    ax1.tick_params(axis='y', labelcolor=color_age)
    
    if births and deaths:
        ax2 = ax1.twinx()
        ax2.set_ylabel('Vital Rates (Count)', color='gray')
        ax2.plot(steps, births, label='Births', color='lightgreen', linewidth=1.5)
        ax2.plot(steps, deaths, label='Deaths', color='salmon', linewidth=1.5)
        ax2.fill_between(steps, births, deaths, alpha=0.1, color='gray')

    plt.title('Demographics: Age & Vital Rates')
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
    plt.xlabel('Welfare Level')
    plt.ylabel('Number of Agents')
    plt.title(f'Wealth Distribution at Step {step_num}')
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    
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
    final_welfares: list = None
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

    # Добавляем снимок распределения богатства на последнем шаге
    if final_welfares:
        last_step = steps[-1] if steps else 0
        charts["graphs/final_wealth_dist.png"] = generate_wealth_distribution_chart(last_step, final_welfares)

    return charts

def render_charts_from_data(metrics_data: dict, final_welfares: list) -> dict[str, bytes]:
    """Принимает готовые словари и возвращает байты картинок."""
    return generate_charts(
        steps=metrics_data["steps"],
        agent_counts=metrics_data["agent_counts"],
        total_sugar=metrics_data["total_sugar"],
        total_spicy=metrics_data["total_spicy"],
        avg_welfare=metrics_data["avg_welfare"],
        avg_age=metrics_data["avg_age"],
        gini_coeffs=metrics_data["gini_coeffs"],
        births=metrics_data["births"],
        deaths=metrics_data["deaths"],
        final_welfares=final_welfares
    )