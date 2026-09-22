def regenerate_resources(grid, max_val=4):
    for row in grid:
        for cell in row:
            if cell["sugar"] < max_val:
                cell["sugar"] += 1
            if cell["spicy"] < max_val:
                cell["spicy"] += 1
