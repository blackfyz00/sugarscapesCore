from classes import create_cell
import random as rand
from pathlib import Path

def interpolate_value(val1, val2, factor):
    """Простая линейная интерполяция между двумя значениями"""
    return int(val1 + (val2 - val1) * factor)

def create_map(grid_size: int = None) -> list[list[dict]]:
    map_path = Path(__file__).parent.parent / "maps" / "map1.txt"
    
    # Если файла нет, генерируем случайную карту
    if not map_path.exists():
        size = grid_size or 15
        print(f"⚠️ Файл не найден! Генерирую случайную карту {size}x{size}.")
        return [
            [create_cell(posx=x, posy=y, sugar=rand.randint(0, 4), spicy=rand.randint(0, 4)) 
             for x in range(size)] 
            for y in range(size)
        ]

    with open(map_path, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # Исходные размеры из файла
    src_rows = len(lines)
    src_cols = len(lines[0].split())
    
    # Целевой размер (если не задан, берем из файла)
    target_size = grid_size if grid_size else src_rows
    
    print(f"🗺️ Масштабирую карту из {src_rows}x{src_cols} в {target_size}x{target_size}")

    grid = []
    for y in range(target_size):
        row = []
        for x in range(target_size):
            # Находим соответствующие координаты в исходной карте
            src_y = min(int(y * src_rows / target_size), src_rows - 1)
            src_x = min(int(x * src_cols / target_size), src_cols - 1)
            
            values = lines[src_y].split()
            try:
                base_val = int(values[src_x])
            except (IndexError, ValueError):
                base_val = 0

            sugar = base_val
            
            spicy = max(0, 90 - base_val) 
            
            # Добавляем немного шума для естественности
            sugar = max(0, sugar + rand.randint(-2, 2))
            spicy = max(0, spicy + rand.randint(-2, 2))

            row.append(create_cell(posx=x, posy=y, sugar=sugar, spicy=spicy))
        grid.append(row)
        
    return grid
