from mechanics.death.death import check_and_remove_agent # Импортируем новую функцию

def eat(cell: dict, agents_map: dict, grid: list[list[dict]],
        procent: float = 1, **kwargs):
            
    agent_id = cell.get("agent_id")
    if agent_id is None:
        return
    agent = agents_map[agent_id]
    harvested_sugar = cell["sugar"] * procent
    harvested_spicy = cell["spicy"] * procent
    cell["sugar"] = 0
    cell["spicy"] = 0
    
    # Добавляем собранные ресурсы и вычитаем метаболизм за ход
    agent["sugar"] += harvested_sugar - agent["sugarm"]
    agent["spicy"] += harvested_spicy - agent["spicym"]
