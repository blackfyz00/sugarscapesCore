from death import check_and_remove_agent # Импортируем новую функцию

def eat(cell: dict, agents_map: dict, grid: list[list[dict]]): # Добавляем grid в сигнатуру
    agent_id = cell.get("agent_id")
    if agent_id is None:
        return
    agent = agents_map[agent_id]
    harvested_sugar = cell["sugar"]
    harvested_spicy = cell["spicy"]
    cell["sugar"] = 0
    cell["spicy"] = 0
    agent["sugar"] += harvested_sugar - agent["sugarm"]
    agent["spicy"] += harvested_spicy - agent["spicym"]
    
    # Используем централизованную функцию для проверки и удаления агента
    check_and_remove_agent(agent_id, agents_map, grid)
