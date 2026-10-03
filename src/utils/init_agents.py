import random as rand
from classes import create_agent
from core.world import WorldState

def initialize_agents(grid: WorldState | list[list[dict]], config: dict) -> tuple[dict, int]:
    """Создает и расставляет агентов, поддерживая WorldState или legacy grid."""
    
    is_world_state = isinstance(grid, WorldState)
    grid_size = config.get("grid_size", grid.size if is_world_state else len(grid))
    
    agents_map = {}
    next_agent_id = 1
    
    for _ in range(num_agents := config.get("num_agents", 60)):
        placed = False
        while not placed:
            x = rand.randint(0, grid_size - 1)
            y = rand.randint(0, grid_size - 1)
            
            # Проверяем занятость
            if is_world_state:
                cell_occupied = grid.occupancy[y, x] != -1
            else:
                cell_occupied = grid[y][x]["agent_id"] is not None
                
            if not cell_occupied:
                agent = create_agent(
                    id=next_agent_id, 
                    x=x, 
                    y=y, 
                    config=config
                )
                
                agents_map[next_agent_id] = agent
                
                if is_world_state:
                    grid.occupancy[y, x] = next_agent_id
                else:
                    grid[y][x]["agent_id"] = next_agent_id
                
                next_agent_id += 1
                placed = True
                
    return agents_map, next_agent_id
