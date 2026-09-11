import json
import random as rand
from classes import create_agent
from create_map import create_map
from trade import trade
from move import move
from eat import eat
from findperspectivecell import find_perspective_cell 

def regenerate_resources(grid, max_val=4):
    for row in grid:
        for cell in row:
            if cell["sugar"] < max_val:
                cell["sugar"] += 1
            if cell["spicy"] < max_val:
                cell["spicy"] += 1

def get_neighbors(cell, grid):
    x, y = cell["posx"], cell["posy"]
    neighbors = []
    # Проверяем 4 направления (верх, низ, лево, право)
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
            neighbors.append(grid[ny][nx])
    return neighbors

def main():
    print("🌍 Инициализация мира...")
    grid_size = 15  # Увеличим для интереса, как в твоем JSON
    num_agents = 2 
    steps = 100
    
    grid = create_map(grid_size)
    agents_map = {}
    
    # Создаем агентов
    for i in range(1, num_agents + 1):
        placed = False
        while not placed:
            x = rand.randint(0, grid_size - 1)
            y = rand.randint(0, grid_size - 1)
            if grid[y][x]["agent_id"] is None:
                agent = create_agent(
                    id=i, 
                    x=x, 
                    y=y, 
                    sugar=rand.randint(5, 25), 
                    spicy=rand.randint(5, 25),
                    sugarm=rand.randint(1, 4),
                    spicym=rand.randint(1, 4)
                )
                agents_map[i] = agent
                grid[y][x]["agent_id"] = i
                placed = True

    simulation_history = []
    print(f"🏁 Старт: {num_agents} агентов, {steps} шагов")

    for step in range(1, steps + 1):
        # 1. Регенерация
        regenerate_resources(grid)

        # 2. Движение
        for agent in list(agents_map.values()):
            current_cell = grid[agent["y"]][agent["x"]]
            best_cell = find_perspective_cell(current_cell, grid, agents_map)
            if best_cell:
                move(current_cell, best_cell, agents_map)
                
        # 3. Еда
        for row in grid:
            for cell in row:
                eat(cell, agents_map)

        # 4. Торговля
        for agent in list(agents_map.values()):
            current_cell = grid[agent["y"]][agent["x"]]
            neighbors = get_neighbors(current_cell, grid)
            for neighbor_cell in neighbors:
                trade(current_cell, neighbor_cell, agents_map)

        # 5. Проверка на смерть (Убираем умерших из agents_map и сетки)
        dead_ids = [aid for aid, ag in agents_map.items() if ag["sugar"] <= 0 or ag["spicy"] <= 0]
        for aid in dead_ids:
            dead_agent = agents_map[aid]
            grid[dead_agent["y"]][dead_agent["x"]]["agent_id"] = None
            del agents_map[aid]

        # 6. Сбор данных
        # Сохраняем карту ресурсов (берем только сахар для экономии места, или оба)
        current_sugar_map = [[cell["sugar"] for cell in row] for row in grid]
        
        step_data = {
            "step": step,
            "sugar_map": current_sugar_map,
            "agents": [
                {
                    "id": ag["id"],
                    "x": ag["x"],
                    "y": ag["y"],
                    "wealth": ag["sugar"] + ag["spicy"],
                    "is_trading": ag["is_trading"]
                }
                for ag in agents_map.values()
            ]
        }
            
        simulation_history.append(step_data)
        if step % 10 == 0:
            print(f"⏳ Шаг {step}. Живых агентов: {len(agents_map)}")

    # Экспорт
    output_file = "sim_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(simulation_history, f)
        
    print(f"\n✅ Готово! Файл: {output_file}")

if __name__ == "__main__":
    main()