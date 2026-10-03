import numpy as np

class WorldState:
    def __init__(self, size: int):
        self.size = size
        self.sugar_map = np.zeros((size, size), dtype=np.int16)
        self.spicy_map = np.zeros((size, size), dtype=np.int16)
        self.occupancy = np.full((size, size), -1, dtype=np.int32)

    def regenerate(self, rate_s: int, rate_p: int, max_val: int):
        """Vectorized regeneration using boolean masks."""
        # Sugar regeneration
        mask_s = self.sugar_map < max_val
        self.sugar_map[mask_s] = np.minimum(max_val, self.sugar_map[mask_s] + rate_s)

        # Spicy regeneration
        mask_p = self.spicy_map < max_val
        self.spicy_map[mask_p] = np.minimum(max_val, self.spicy_map[mask_p] + rate_p)

    def to_dict_list(self) -> list[list[dict]]:
        """Converts the NumPy arrays back to list[list[dict]] for compatibility with legacy mechanics."""
        grid = []
        for y in range(self.size):
            row = []
            for x in range(self.size):
                agent_id = int(self.occupancy[y, x])
                cell = {
                    "x": x,
                    "y": y,
                    "sugar": int(self.sugar_map[y, x]),
                    "spicy": int(self.spicy_map[y, x]),
                    "agent_id": agent_id if agent_id != -1 else None
                }
                row.append(cell)
            grid.append(row)
        return grid
