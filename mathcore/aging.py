def age_agent(agent: dict, agents_map: dict, grid: list[list[dict]]) -> bool:
    """
    Increments the agent's age by 1 and checks if the agent dies of old age.
    If the agent's age exceeds or equals its max_age, removes the agent from
    the agents_map and clears the agent_id from its current cell in the grid,
    then returns True (died). Otherwise returns False (alive).
    """
    agent["age"] += 1
    
    if agent["age"] >= agent["max_age"]:
        agent_id = agent["id"]
        x, y = agent["x"], agent["y"]
        
        # Clear agent from the grid cell
        if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
            if grid[y][x].get("agent_id") == agent_id:
                grid[y][x]["agent_id"] = None
                
        # Remove agent from agents_map
        if agent_id in agents_map:
            del agents_map[agent_id]
            
        return True
        
    return False
