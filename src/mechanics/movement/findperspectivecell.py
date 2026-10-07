import numpy as np
import random  
from utils.welfare_cobb import calculate_welfare_cobb_douglas
def find_perspective_cell_vectorized(world, agents):
    """
    Vectorized movement calculation with randomized update order to prevent bias.
    """
    alive = agents.get_alive_indices()
    if len(alive) == 0:
        return
    shuffled_indices = list(range(len(alive)))
    random.shuffle(shuffled_indices)
    size = world.size
    sugar_map = world.sugar_map.astype(np.float32)
    spicy_map = world.spicy_map.astype(np.float32)
    occupancy = world.occupancy
    sugarm = agents.sugarm[alive]
    spicym = agents.spicym[alive]
    m_total = sugarm + spicym
    m_total = np.where(m_total == 0, 1.0, m_total)
    xs = agents.x[alive]
    ys = agents.y[alive]
    current_sugar = agents.sugar[alive]
    current_spicy = agents.spicy[alive]
    vis = agents.vis[alive]
    for i_local in shuffled_indices:
        idx = alive[i_local] 
        x, y = int(xs[i_local]), int(ys[i_local])
        v = int(vis[i_local])
        sm = sugarm[i_local]
        spm = spicym[i_local]
        mt = m_total[i_local]
        ymin, ymax = max(0, y - v), min(size, y + v + 1)
        xmin, xmax = max(0, x - v), min(size, x + v + 1)
        sub_sugar = sugar_map[ymin:ymax, xmin:xmax]
        sub_spicy = spicy_map[ymin:ymax, xmin:xmax]
        sub_occupancy = occupancy[ymin:ymax, xmin:xmax]
        pot_sugar = current_sugar[i_local] + sub_sugar
        pot_spicy = current_spicy[i_local] + sub_spicy
        welfares = (np.maximum(0.0, pot_sugar) ** (sm / mt)) * (np.maximum(0.0, pot_spicy) ** (spm / mt))
        sub_y, sub_x = np.ogrid[ymin:ymax, xmin:xmax]
        dist_sq = (sub_x - x)**2 + (sub_y - y)**2
        valid_mask = (dist_sq <= v**2) & ((sub_occupancy == -1) | ((sub_x == x) & (sub_y == y)))
        if not np.any(valid_mask):
            continue
        welfares[~valid_mask] = -1.0
        max_w = np.max(welfares)
        current_w = (max(0.0, current_sugar[i_local]) ** (sm / mt)) * (max(0.0, current_spicy[i_local]) ** (spm / mt))
        if max_w <= current_w + 1e-5:
            continue
        best_locs = np.argwhere(welfares == max_w)
        dists = (best_locs[:, 0] + ymin - y)**2 + (best_locs[:, 1] + xmin - x)**2
        best_loc = best_locs[np.argmin(dists)]
        target_y = best_loc[0] + ymin
        target_x = best_loc[1] + xmin
        dx = np.sign(target_x - x)
        dy = np.sign(target_y - y)
        nx, ny = x + int(dx), y + int(dy)
        if 0 <= nx < size and 0 <= ny < size and occupancy[ny, nx] == -1:
            occupancy[y, x] = -1
            occupancy[ny, nx] = int(agents.id[idx])
            agents.x[idx] = nx
            agents.y[idx] = ny
