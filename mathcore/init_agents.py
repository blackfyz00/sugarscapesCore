import random as rand
from classes import create_agent

def initialize_agents(grid: list[list[dict]], config: dict) -> tuple[dict, int]:
    """Создает и расставляет агентов на сетке в соответствии с конфигурацией."""
    grid_size = config.get("grid_size", len(grid))
    num_agents = config.get("num_agents", 60)
    sugar_range = config.get("sugar_range", [15, 25])
    spicy_range = config.get("spicy_range", [15, 25])
    
    agents_map = {}
    next_agent_id = 1
    
    for _ in range(1, num_agents + 1):
        placed = False
        while not placed:
            x = rand.randint(0, grid_size - 1)
            y = rand.randint(0, grid_size - 1)
            if grid[y][x]["agent_id"] is None:
                agent = create_agent(
                    id=next_agent_id, 
                    x=x, 
                    y=y, 
                    sugar=rand.randint(sugar_range[0], sugar_range[1]), 
                    spicy=rand.randint(spicy_range[0], spicy_range[1]),
                    config=config
                )
                agents_map[next_agent_id] = agent
                grid[y][x]["agent_id"] = next_agent_id
                next_agent_id += 1
                placed = True
                
    return agents_map, next_agent_id
