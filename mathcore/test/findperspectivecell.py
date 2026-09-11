import math
def calculate_welfare_for_move(agent: dict, cell: dict) -> float:
    """
    Книжная логика: Cobb-Douglas Welfare Function.
    Считает потенциальное благосостояние, если агент перейдет в эту клетку.
    """
    potential_sugar = agent["sugar"] + cell["sugar"]
    potential_spicy = agent["spicy"] + cell["spicy"]
    s = max(1e-9, potential_sugar)
    p = max(1e-9, potential_spicy)
    m_total = agent["sugarm"] + agent["spicym"]
    if m_total == 0: return 0
    return (s ** (agent["sugarm"] / m_total)) * (p ** (agent["spicym"] / m_total))
def find_perspective_cell(current_cell: dict, map_matrix: list[list[dict]], 
                          agents_map: dict) -> dict | None:
    """
    1. Найти все свободные клетки в радиусе зрения.
    2. Вычислить Welfare для каждой.
    3. Выбрать клетки с максимальным Welfare.
    4. Среди них выбрать ближайшие.
    5. Вернуть одну из ближайших лучших.
    """
    agent_id = current_cell.get("agent_id")
    if agent_id is None:
        return None
    agent = agents_map[agent_id]
    cx, cy = current_cell["posx"], current_cell["posy"]
    perspective_cells = []
    for row in map_matrix:
        for cell in row:
            if cell["agent_id"] is not None:
                continue
            dist = math.sqrt((cell["posx"] - cx)**2 + (cell["posy"] - cy)**2)
            if dist <= agent["vis"]:
                perspective_cells.append((cell, dist))
    if not perspective_cells:
        return None
    candidates_with_welfare = []
    for cell, dist in perspective_cells:
        w = calculate_welfare_for_move(agent, cell)
        candidates_with_welfare.append({"cell": cell, "welfare": w, "dist": dist})
    max_welfare = max(item["welfare"] for item in candidates_with_welfare)
    best_candidates = [
        item for item in candidates_with_welfare 
        if math.isclose(item["welfare"], max_welfare, rel_tol=1e-5)
    ]
    min_dist = min(item["dist"] for item in best_candidates)
    final_candidates = [
        item["cell"] for item in best_candidates 
        if math.isclose(item["dist"], min_dist, rel_tol=1e-5)
    ]
    import random
    return random.choice(final_candidates)
