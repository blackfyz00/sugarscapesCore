def eat(cell: dict, agents_map: dict):
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