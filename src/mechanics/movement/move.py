def move(cell_from: dict, cell_to: dict, agents_map: dict):
    agent_id = cell_from.get("agent_id")
    if agent_id is None or cell_to.get("agent_id") is not None:
        return False
    cell_to["agent_id"] = agent_id
    cell_from["agent_id"] = None
    agents_map[agent_id]["x"] = cell_to["x"]
    agents_map[agent_id]["y"] = cell_to["y"]
    return True
