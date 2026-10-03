import numpy as np
from scipy.ndimage import maximum_filter
from utils.welfare_cobb import calculate_welfare_cobb_douglas

def find_perspective_cell_vectorized(world, agents):
    """
    Vectorized movement calculation using numpy and scipy maximum_filter.
    Determines target movement steps for all active agents.
    """
    alive = agents.get_alive_indices()
    if len(alive) == 0:
        return

    size = world.size
    sugar_map = world.sugar_map.astype(np.float32)
    spicy_map = world.spicy_map.astype(np.float32)
    occupancy = world.occupancy

    # For each agent, calculate current welfare
    sugarm = agents.sugarm[alive]
    spicym = agents.spicym[alive]
    m_total = sugarm + spicym
    m_total = np.where(m_total == 0, 1.0, m_total)

    # We want to find the best cell within agent's visibility `vis`.
    # Since `vis` can vary per agent or be uniform, let's process agent positions or use max possible neighborhood.
    # To be efficient and robust, let's iterate through unique vis or handle per-agent locally if vis varies,
    # but typically vis is uniform or bounded. Let's do a fast vectorized pass.
    
    xs = agents.x[alive]
    ys = agents.y[alive]
    current_sugar = agents.sugar[alive]
    current_spicy = agents.spicy[alive]
    vis = agents.vis[alive]

    # Pre-calculate welfare map for the entire grid
    # Welfare function: (sugar ^ (sugarm/m_total)) * (spicy ^ (spicym/m_total))
    # Since welfare depends on agent's specific weights (sugarm, spicym), 
    # if weights vary per agent, we can compute local neighborhoods.
    
    for i, idx in enumerate(alive):
        x, y = xs[i], ys[i]
        v = int(vis[i])
        sm = sugarm[i]
        spm = spicym[i]
        mt = m_total[i]
        
        # Local window bounds
        ymin, ymax = max(0, y - v), min(size, y + v + 1)
        xmin, xmax = max(0, x - v), min(size, x + v + 1)
        
        sub_sugar = sugar_map[ymin:ymax, xmin:xmax]
        sub_spicy = spicy_map[ymin:ymax, xmin:xmax]
        sub_occupancy = occupancy[ymin:ymax, xmin:xmax]
        
        # Potential resources = agent's current + cell's resources
        pot_sugar = current_sugar[i] + sub_sugar
        pot_spicy = current_spicy[i] + sub_spicy
        
        # Calculate welfare in window
        welfares = (np.maximum(0.0, pot_sugar) ** (sm / mt)) * (np.maximum(0.0, pot_spicy) ** (spm / mt))
        
        # Mask out occupied cells (except current cell)
        sub_y, sub_x = np.ogrid[ymin:ymax, xmin:xmax]
        dist_sq = (sub_x - x)**2 + (sub_y - y)**2
        valid_mask = (dist_sq <= v**2) & ((sub_occupancy == -1) | ((sub_x == x) & (sub_y == y)))
        
        if not np.any(valid_mask):
            continue
            
        welfares[~valid_mask] = -1.0
        
        # Find max welfare location
        max_w = np.max(welfares)
        current_w = (max(0.0, current_sugar[i]) ** (sm / mt)) * (max(0.0, current_spicy[i]) ** (spm / mt))
        
        if max_w <= current_w + 1e-5:
            # Stay put
            continue
            
        best_locs = np.argwhere(welfares == max_w)
        # Choose closest by distance
        dists = (best_locs[:, 0] + ymin - y)**2 + (best_locs[:, 1] + xmin - x)**2
        best_loc = best_locs[np.argmin(dists)]
        
        target_y = best_loc[0] + ymin
        target_x = best_loc[1] + xmin
        
        # Determine 1-step move towards target_y, target_x using Moore neighborhood (8 directions)
        dx = np.sign(target_x - x)
        dy = np.sign(target_y - y)
        
        nx, ny = x + int(dx), y + int(dy)
        if 0 <= nx < size and 0 <= ny < size and occupancy[ny, nx] == -1:
            # Move agent
            occupancy[y, x] = -1
            occupancy[ny, nx] = int(agents.id[idx])
            agents.x[idx] = nx
            agents.y[idx] = ny
