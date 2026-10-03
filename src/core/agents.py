import numpy as np
from typing import Any

class AgentSystem:
    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        # Parallel arrays (Structure of Arrays - SoA)
        self.id = np.full(capacity, -1, dtype=np.int32)
        self.x = np.zeros(capacity, dtype=np.int32)
        self.y = np.zeros(capacity, dtype=np.int32)
        self.sugar = np.zeros(capacity, dtype=np.float32)
        self.spicy = np.zeros(capacity, dtype=np.float32)
        self.sugarm = np.zeros(capacity, dtype=np.float32)
        self.spicym = np.zeros(capacity, dtype=np.float32)
        self.vis = np.ones(capacity, dtype=np.int32)
        self.age = np.zeros(capacity, dtype=np.int32)
        self.max_age = np.full(capacity, 80, dtype=np.int32)
        self.children_count = np.zeros(capacity, dtype=np.int32)
        self.alive_mask = np.zeros(capacity, dtype=bool)
        
        # Additional flexible fields stored as dicts or extra mapping if needed,
        # but standard pipeline keys are covered.
        self.history_trades = {i: [] for i in range(capacity)}
        self.is_trading = np.zeros(capacity, dtype=bool)

    def spawn(self, agent_id: int, x: int, y: int, data: dict) -> int:
        """Finds an inactive slot or appends, and initializes agent data."""
        # Find first dead slot
        dead_indices = np.where(~self.alive_mask)[0]
        if len(dead_indices) == 0:
            raise RuntimeError("AgentSystem capacity reached!")
        
        idx = dead_indices[0]
        self.id[idx] = agent_id
        self.x[idx] = x
        self.y[idx] = y
        self.sugar[idx] = data.get("sugar", 10.0)
        self.spicy[idx] = data.get("spicy", 10.0)
        self.sugarm[idx] = data.get("sugarm", 1.0)
        self.spicym[idx] = data.get("spicym", 1.0)
        self.vis[idx] = data.get("vis", 15)
        self.age[idx] = data.get("age", 0)
        self.max_age[idx] = data.get("max_age", 80)
        self.children_count[idx] = data.get("children_count", 0)
        self.alive_mask[idx] = True
        self.history_trades[idx] = data.get("history_trades", [])
        self.is_trading[idx] = False
        return idx

    def kill(self, indices: np.ndarray | list[int]):
        """Marks agents as dead."""
        self.alive_mask[indices] = False
        self.id[indices] = -1

    def get_alive_indices(self) -> np.ndarray:
        return np.where(self.alive_mask)[0]

    def to_dict_map(self) -> dict[int, dict[str, Any]]:
        """Adapter to create legacy agents_map dict for un-migrated strategies."""
        alive_indices = self.get_alive_indices()
        agents_map = {}
        for idx in alive_indices:
            aid = int(self.id[idx])
            agents_map[aid] = {
                "id": aid,
                "x": int(self.x[idx]),
                "y": int(self.y[idx]),
                "sugar": float(self.sugar[idx]),
                "spicy": float(self.spicy[idx]),
                "sugarm": float(self.sugarm[idx]),
                "spicym": float(self.spicym[idx]),
                "vis": int(self.vis[idx]),
                "age": int(self.age[idx]),
                "max_age": int(self.max_age[idx]),
                "children_count": int(self.children_count[idx]),
                "history_trades": self.history_trades[idx],
                "is_trading": bool(self.is_trading[idx])
            }
        return agents_map

    def update_from_dict_map(self, agents_map: dict[int, dict[str, Any]]):
        """Syncs changes back from legacy agents_map (e.g., after trade or move)."""
        # Create a lookup from id to array index for alive agents
        alive_indices = self.get_alive_indices()
        id_to_idx = {int(self.id[i]): i for i in alive_indices}
        
        for aid, agent in agents_map.items():
            if aid in id_to_idx:
                idx = id_to_idx[aid]
                self.x[idx] = agent["x"]
                self.y[idx] = agent["y"]
                self.sugar[idx] = agent["sugar"]
                self.spicy[idx] = agent["spicy"]
                self.children_count[idx] = agent.get("children_count", 0)
                self.is_trading[idx] = agent.get("is_trading", False)
                if "history_trades" in agent:
                    self.history_trades[idx] = agent["history_trades"]
