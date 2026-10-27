# src/mechanics/trade/trade.py
import numpy as np


_DIRECTIONS = np.array(
    [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)],
    dtype=np.int64,
)


def trade_vectorized(world, agents) -> list[dict]:
    """
    Векторизованная торговля.

    Возвращает список сделок:
    [
        {
            "seller_id": int,
            "buyer_id": int,
            "sugar_qty": int,
            "spice_qty": int,
        },
        ...
    ]

    Логика:
    - обмен только между соседями по 8 направлениям;
    - оба агента должны иметь sugar > 0 и spicy > 0;
    - сделка возможна, если MRS различаются;
    - покупатель сахара — агент с более высоким MRS;
    - продавец сахара — агент с более низким MRS;
    - цена: sqrt(MRS_a * MRS_b), округляется до целого;
    - количество сахара всегда 1;
    - каждый агент участвует максимум в одной сделке за шаг.
    """
    alive = np.asarray(agents.get_alive_indices(), dtype=np.int64)
    n = alive.size

    if n < 2:
        return []

    ids = np.asarray(agents.id[alive], dtype=np.int64)
    x = np.asarray(agents.x[alive], dtype=np.int64)
    y = np.asarray(agents.y[alive], dtype=np.int64)

    sugar = np.asarray(agents.sugar[alive], dtype=np.float64)
    spice = np.asarray(agents.spicy[alive], dtype=np.float64)
    sugar_m = np.asarray(agents.sugarm[alive], dtype=np.float64)
    spice_m = np.asarray(agents.spicym[alive], dtype=np.float64)

    size = int(world.size)
    occ = np.asarray(world.occupancy)

    if size <= 0 or occ.size == 0:
        return []

    dx = _DIRECTIONS[:, 0]
    dy = _DIRECTIONS[:, 1]

    # Координаты всех соседей для всех живых агентов.
    nx = x[:, None] + dx[None, :]
    ny = y[:, None] + dy[None, :]

    inside = (nx >= 0) & (nx < size) & (ny >= 0) & (ny < size)

    # Клипуем только для безопасного индексирования occupancy.
    nx_c = np.clip(nx, 0, size - 1)
    ny_c = np.clip(ny, 0, size - 1)

    neigh_ids = occ[ny_c, nx_c]

    # Валидные соседи:
    # - внутри мира;
    # - не пусто;
    # - не сам агент.
    mask = inside & (neigh_ids != -1) & (neigh_ids != ids[:, None])

    if not mask.any():
        return []

    src, _ = np.nonzero(mask)
    src = src.astype(np.int64, copy=False)
    tgt_ids = neigh_ids[mask].astype(np.int64, copy=False)

    # Быстрый перевод neighbor_id -> позиция в alive.
    order = np.argsort(ids, kind="stable")
    sorted_ids = ids[order]

    pos = np.searchsorted(sorted_ids, tgt_ids)
    pos_c = np.clip(pos, 0, n - 1)
    found = sorted_ids[pos_c] == tgt_ids

    if not found.any():
        return []

    src = src[found]
    tgt = order[pos_c[found]].astype(np.int64, copy=False)

    # MRS = (spice * marginal_sugar) / (sugar * marginal_spice)
    with np.errstate(divide="ignore", invalid="ignore"):
        mrs_src = (spice[src] * sugar_m[src]) / (sugar[src] * spice_m[src])
        mrs_tgt = (spice[tgt] * sugar_m[tgt]) / (sugar[tgt] * spice_m[tgt])

    valid = (
        np.isfinite(mrs_src)
        & np.isfinite(mrs_tgt)
        & (sugar[src] > 0)
        & (spice[src] > 0)
        & (sugar[tgt] > 0)
        & (spice[tgt] > 0)
        & ~np.isclose(mrs_src, mrs_tgt, rtol=1e-5)
    )

    src = src[valid]
    tgt = tgt[valid]
    mrs_src = mrs_src[valid]
    mrs_tgt = mrs_tgt[valid]

    if src.size == 0:
        return []

    # Одна недирективная пара может встретиться дважды: A->B и B->A.
    lo = np.minimum(src, tgt)
    hi = np.maximum(src, tgt)
    pair_key = lo * np.int64(n) + hi

    _, first = np.unique(pair_key, return_index=True)

    src = src[first]
    tgt = tgt[first]
    mrs_src = mrs_src[first]
    mrs_tgt = mrs_tgt[first]
    pair_key = pair_key[first]

    diff = mrs_src - mrs_tgt
    score = np.abs(diff)

    # Если MRS_src > MRS_tgt, значит src сильнее хочет сахар и является покупателем.
    buyer = np.where(diff > 0, src, tgt)
    seller = np.where(diff > 0, tgt, src)

    # Цена в специях за 1 сахар.
    with np.errstate(invalid="ignore"):
        price = np.sqrt(np.abs(mrs_src * mrs_tgt))

    price_ok = np.isfinite(price) & (price >= 0)

    spice_qty = np.ones(price.shape, dtype=np.int64)

    if price_ok.any():
        rounded = np.rint(price[price_ok])
        spice_qty[price_ok] = np.maximum(1, rounded).astype(np.int64)

    # Финальная проверка ресурсов.
    ok = (
        price_ok
        & (sugar[seller] >= 1.0)
        & (spice[buyer] >= spice_qty.astype(np.float64))
    )

    buyer = buyer[ok]
    seller = seller[ok]
    spice_qty = spice_qty[ok]
    score = score[ok]
    pair_key = pair_key[ok]

    if buyer.size == 0:
        return []

    # Жадный выбор непересекающихся сделок.
    # Сначала берём самую выгодную по разнице MRS.
    # pair_key используется для детерминированного разрешения ничьих.
    greedy_order = np.lexsort((pair_key, -score))

    used = np.zeros(n, dtype=bool)

    chosen_seller = []
    chosen_buyer = []
    chosen_spice = []

    for k in greedy_order:
        s = int(seller[k])
        b = int(buyer[k])

        if used[s] or used[b]:
            continue

        used[s] = True
        used[b] = True

        chosen_seller.append(s)
        chosen_buyer.append(b)
        chosen_spice.append(int(spice_qty[k]))

    if not chosen_seller:
        return []

    seller_pos = np.asarray(chosen_seller, dtype=np.int64)
    buyer_pos = np.asarray(chosen_buyer, dtype=np.int64)
    spice_amt = np.asarray(chosen_spice, dtype=np.int64)

    seller_gid = alive[seller_pos]
    buyer_gid = alive[buyer_pos]

    # Применяем сделки к глобальным массивам агентов.
    agents.sugar[seller_gid] -= 1
    agents.spicy[seller_gid] += spice_amt

    agents.sugar[buyer_gid] += 1
    agents.spicy[buyer_gid] -= spice_amt

    agents.is_trading[seller_gid] = True
    agents.is_trading[buyer_gid] = True

    return [
        {
            "seller_id": int(ids[s]),
            "buyer_id": int(ids[b]),
            "sugar_qty": 1,
            "spice_qty": int(q),
        }
        for s, b, q in zip(seller_pos, buyer_pos, spice_amt)
    ]
