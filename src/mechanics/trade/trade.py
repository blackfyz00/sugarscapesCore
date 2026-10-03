import numpy as np
def trade_vectorized(world, agents):
    """
    Векторизованная торговля между соседними агентами.
    """
    alive = agents.get_alive_indices()
    if len(alive) < 2:
        return
    id_to_idx = {}
    for i in alive:
        id_to_idx[int(agents.id[i])] = i
    xs = agents.x[alive]
    ys = agents.y[alive]
    ids = agents.id[alive]
    occupancy = world.occupancy
    size = world.size
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    traded_set = set()
    for i, idx in enumerate(alive):
        aid = int(ids[i])
        if aid in traded_set:
            continue
        x, y = xs[i], ys[i]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                neighbor_aid = occupancy[ny, nx]
                if neighbor_aid != -1 and neighbor_aid != aid and neighbor_aid not in traded_set:
                    n_idx = id_to_idx.get(neighbor_aid)
                    if n_idx is None:
                        continue
                    s_a, sp_a = agents.sugar[idx], agents.spicy[idx]
                    s_b, sp_b = agents.sugar[n_idx], agents.spicy[n_idx]
                    if s_a <= 0 or sp_a <= 0 or s_b <= 0 or sp_b <= 0:
                        continue
                    mrs_a = (sp_a * agents.sugarm[idx]) / (s_a * agents.spicym[idx])
                    mrs_b = (sp_b * agents.sugarm[n_idx]) / (s_b * agents.spicym[n_idx])
                    if np.isclose(mrs_a, mrs_b):
                        continue
                    if mrs_a > mrs_b:
                        buyer_idx, seller_idx = idx, n_idx
                    else:
                        buyer_idx, seller_idx = n_idx, idx
                    price = np.sqrt(mrs_a * mrs_b)
                    amount_sugar = 1
                    amount_spicy = max(1, round(price))
                    if agents.sugar[seller_idx] >= amount_sugar and agents.spicy[buyer_idx] >= amount_spicy:
                        agents.sugar[seller_idx] -= amount_sugar
                        agents.spicy[seller_idx] += amount_spicy
                        agents.sugar[buyer_idx] += amount_sugar
                        agents.spicy[buyer_idx] -= amount_spicy
                        agents.is_trading[idx] = True
                        agents.is_trading[n_idx] = True
                        traded_set.add(aid)
                        traded_set.add(neighbor_aid)
                        break 
