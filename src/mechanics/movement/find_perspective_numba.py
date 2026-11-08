import numpy as np
from numba import njit

@njit(cache=True, fastmath=True)
def _move_core(
    alive_idx,
    agents_x,
    agents_y,
    agents_vis,
    agents_sugarm,
    agents_spicym,
    agents_sugar,
    agents_spicy,
    agents_id,
    world_sugar,
    world_spicy,
    world_occ,
    size
):
    n_alive = len(alive_idx)
    if n_alive == 0:
        return

    rand_keys = np.random.rand(n_alive)
    order = np.argsort(rand_keys)

    for k in range(n_alive):
        local_i = order[k]
        global_i = alive_idx[local_i]
        
        x = agents_x[global_i]
        y = agents_y[global_i]
        v = agents_vis[global_i]
        
        sm = agents_sugarm[global_i]
        spm = agents_spicym[global_i]
        mt = sm + spm
        if mt == 0.0:
            mt = 1.0
            
        cur_s = agents_sugar[global_i]
        cur_p = agents_spicy[global_i]
        
        ymin = max(0, y - v)
        ymax = min(size, y + v + 1)
        xmin = max(0, x - v)
        xmax = min(size, x + v + 1)
        
        sub_s = world_sugar[ymin:ymax, xmin:xmax]
        sub_p = world_spicy[ymin:ymax, xmin:xmax]
        sub_o = world_occ[ymin:ymax, xmin:xmax]
        
        h = ymax - ymin
        w = xmax - xmin
        
        pot_s = cur_s + sub_s
        pot_p = cur_p + sub_p
        
        welfares = (np.maximum(0.0, pot_s) ** (sm / mt)) * (np.maximum(0.0, pot_p) ** (spm / mt))
        
        max_w = -1.0
        best_dx = 0
        best_dy = 0
        found_better = False
        
        curr_w = (max(0.0, cur_s) ** (sm / mt)) * (max(0.0, cur_p) ** (spm / mt))
        
        for dy in range(h):
            abs_y = ymin + dy
            dist_y_sq = (abs_y - y) ** 2
            
            for dx in range(w):
                abs_x = xmin + dx
                dist_x_sq = (abs_x - x) ** 2
                
                if dist_x_sq + dist_y_sq > v * v:
                    continue
                
                is_current_pos = (abs_x == x) and (abs_y == y)
                is_empty = sub_o[dy, dx] == -1
                
                if not (is_empty or is_current_pos):
                    continue
                
                w_val = welfares[dy, dx]
                
                if w_val > curr_w + 1e-5:
                    if w_val > max_w:
                        max_w = w_val
                        best_dx = dx
                        best_dy = dy
                        found_better = True
                    elif w_val == max_w:
                        old_dist_sq = best_dx**2 + best_dy**2
                        new_dist_sq = dx**2 + dy**2
                        if new_dist_sq < old_dist_sq:
                            best_dx = dx
                            best_dy = dy

        if found_better:
            target_x = xmin + best_dx
            target_y = ymin + best_dy
            
            dx_step = np.sign(target_x - x)
            dy_step = np.sign(target_y - y)
            
            nx = int(x + dx_step)
            ny = int(y + dy_step)
            
            if 0 <= nx < size and 0 <= ny < size and world_occ[ny, nx] == -1:
                world_occ[y, x] = -1
                world_occ[ny, nx] = agents_id[global_i]
                agents_x[global_i] = nx
                agents_y[global_i] = ny

def find_perspective_cell_vectorized(world, agents):
    """Подготавливает данные и вызывает ядро Numba БЕЗ КОПИРОВАНИЯ"""
    alive = agents.get_alive_indices()
    if len(alive) == 0:
        return
    
    ws = world.sugar_map.astype(np.float32, copy=False)
    wp = world.spicy_map.astype(np.float32, copy=False)
    wo = world.occupancy.astype(np.int32, copy=False)
    
    ax = agents.x.astype(np.int32, copy=False)
    ay = agents.y.astype(np.int32, copy=False)
    av = agents.vis.astype(np.int32, copy=False)
    asm = agents.sugarm.astype(np.float32, copy=False)
    apm = agents.spicym.astype(np.float32, copy=False)
    asg = agents.sugar.astype(np.float32, copy=False)
    asp = agents.spicy.astype(np.float32, copy=False)
    aid = agents.id.astype(np.int32, copy=False)
    
    size = np.int32(world.size)
    
    _move_core(
        alive.astype(np.int32, copy=False),
        ax, ay, av, asm, apm, asg, asp, aid,
        ws, wp, wo,
        size
    )
    
