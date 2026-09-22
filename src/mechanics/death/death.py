def check_and_remove_agent(agent_id: int, agents_map: dict, grid: list[list[dict]]) -> bool:
    """
    Проверяет, мертв ли агент (sugar <= 0 или spicy <= 0), и если да, удаляет его из симуляции.
    Возвращает True, если агент был удален, False в противном случае.
    """
    if agent_id not in agents_map:
        return False # Агент уже удален или не существует

    agent = agents_map[agent_id]

    if agent["sugar"] <= 0 or agent["spicy"] <= 0:
        # Удаляем агента из карты агентов
        del agents_map[agent_id]
        
        # Очищаем ссылку на агента в его ячейке на сетке
        # Важно: agent["y"] и agent["x"] должны быть актуальными координатами агента
        grid[agent["y"]][agent["x"]]["agent_id"] = None
        return True
    return False

