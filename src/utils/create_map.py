# src/utils/create_map.py
import random as rand
from pathlib import Path
from classes import create_cell

def create_map(grid_size: int = None, map_filename: str = None) -> list[list[dict]]:
    if map_filename:
        map_path = Path(__file__).parent.parent / "maps" / map_filename
    else:
        map_path = Path(__file__).parent.parent / "maps" / "map1.txt"
    
    if not map_path.exists():
        size = grid_size or 15
        print(f"⚠️ Файл карты '{map_path}' не найден! Генерирую случайную карту {size}x{size}.")
        return [
            [create_cell(x=x, y=y, sugar=rand.randint(0, 4), spicy=rand.randint(0, 4)) 
             for x in range(size)] 
             for y in range(size)
        ]
    
    with open(map_path, 'r') as f:
        content = f.read()

    # Разделяем контент на два блока по пустым строкам
    blocks = [block.strip() for block in content.split('\n\n') if block.strip()]
    
    if len(blocks) < 2:
        print("⚠️ В файле не найдено две карты. Использую старую логику (одна карта + формула).")
        # Здесь можно оставить старую логику или выдать ошибку
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        src_rows = len(lines)
        src_cols = len(lines[0].split()) if lines else 0
        sugar_map = lines
        spicy_map = None
    else:
        sugar_map = [line.strip() for line in blocks[0].splitlines() if line.strip()]
        spicy_map = [line.strip() for line in blocks[1].splitlines() if line.strip()]
        src_rows = len(sugar_map)
        src_cols = len(sugar_map[0].split()) if sugar_map else 0

    target_size = grid_size if grid_size else src_rows
    
    print(f"🗺️ Масштабирую карты из {src_rows}x{src_cols} в {target_size}x{target_size}")

    grid = []
    for y in range(target_size):
        row = []
        for x in range(target_size):
            # Находим соответствующие координаты в исходных картах
            src_y = min(int(y * src_rows / target_size), src_rows - 1)
            src_x = min(int(x * src_cols / target_size), src_cols - 1)
            
            # Получаем сахар
            try:
                s_val = int(sugar_map[src_y].split()[src_x])
            except (IndexError, ValueError):
                s_val = 0
            
            # Получаем специи (если есть вторая карта)
            if spicy_map:
                try:
                    sp_val = int(spicy_map[src_y].split()[src_x])
                except (IndexError, ValueError):
                    sp_val = 0
            else:
                # Старая логика, если второй карты нет
                sp_val = max(0, 90 - s_val)

            # Добавляем шум
            sugar = max(0, s_val + rand.randint(-2, 2))
            spicy = max(0, sp_val + rand.randint(-2, 2))

            row.append(create_cell(x=x, y=y, sugar=sugar, spicy=spicy))
        grid.append(row)
        
    return grid
