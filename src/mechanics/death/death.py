def check_and_remove_agent(agent_id: int, agents_map: dict, grid: list[list[dict]]) -> bool:
    """
    Проверяет, мертв ли агент (sugar <= 0, spicy <= 0 или age >= max_age), и если да, удаляет его из симуляции.
    Возвращает True, если агент был удален, False в противном случае.
    """
    if agent_id not in agents_map:
        return False # Агент уже удален или не существует

    agent = agents_map[agent_id]

    is_starved = agent["sugar"] <= 0 or agent["spicy"] <= 0
    is_old = "age" in agent and "max_age" in agent and agent["age"] >= agent["max_age"]

    if is_starved or is_old:
        # Удаляем агента из карты агентов
        del agents_map[agent_id]
        
        # Очищаем ссылку на агента в его ячейке на сетке
        grid[agent["y"]][agent["x"]]["agent_id"] = None
        return True
    return False
