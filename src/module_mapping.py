# module_mapping.py
MODULE_MAPPING = {
    "regeneration_map": {
        "strategy": "regenerate_res.regenerate_resources_strategy",
        "required_fields": [],
        "defaults": {}
    },
    "movement_cobb_douglas": {
        "strategy": "movement.move_cobb_strategy",
        "required_fields": ["vis", "sugar", "spicy", "sugarm", "spicym"],
        "defaults": {"vis": 15}
    },
    "eat_all": {
        "strategy": "eat.eat_all_strategy",
        "required_fields": ["sugar", "spicy", "sugarm", "spicym"],
        "defaults": {}
    },
    "trading_cobb_douglas": {
        "strategy": "trade.trade_cobb_strategy",
        "required_fields": ["sugarm", "spicym", "history_trades"],
        "defaults": {"history_trades": []} 
    },
    "reproduction": {
          "strategy": "reproduce.reproduce_strategy",
          "required_fields": ["sugar", "spicy", "children_count"],
          "defaults": {"children_count": 0}
    },
    "aging": {
        "strategy": "aging.aging_strategy",
        "required_fields": ["age", "max_age"],
        "defaults": {}
    },
    "death": {
        "strategy": "death.death_strategy",
        "required_fields": ["age", "max_age"],
        "defaults": {}
    },
    "disease": {
        "strategy": "disease.disease_strategy",
        "required_fields": ["is_infected"],
        "defaults": {"is_infected": False}
    }
}