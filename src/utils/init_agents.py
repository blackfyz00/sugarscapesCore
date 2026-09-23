import random as rand
from classes import create_agent # Или откуда у тебя эта функция

def initialize_agents(grid: list[list[dict]], config: dict) -> tuple[dict, int]:
    """Создает и расставляет агентов, полагаясь на конфиг."""
    
    grid_size = config.get("grid_size", len(grid))
    num_agents = config.get("num_agents", 60)
    
    agents_map = {}
    next_agent_id = 1
    
    for _ in range(num_agents):
        placed = False
        while not placed:
            x = rand.randint(0, grid_size - 1)
            y = rand.randint(0, grid_size - 1)
            
            if grid[y][x]["agent_id"] is None:
                agent = create_agent(
                    id=next_agent_id, 
                    x=x, 
                    y=y, 
                    config=config
                )
                
                agents_map[next_agent_id] = agent
                grid[y][x]["agent_id"] = next_agent_id
                
                next_agent_id += 1
                placed = True
                
    return agents_map, next_agent_id
