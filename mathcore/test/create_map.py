from classes import create_cell
import random as rand

# def create_map(grid_size: int = 3) -> list[list[dict]]:
#     return [
#         [
#             create_cell(
#                 posx=x,
#                 posy=y,
#                 sugar=rand.randint(0, 5),
#                 spicy=rand.randint(0, 5)
#             )
#             for x in range(grid_size)
#         ]
#         for y in range(grid_size)
#     ]

from pathlib import Path

def create_map(grid_size: int = None) -> list[list[dict]]:
    """
    Создает карту на основе файла map.txt.
    Если grid_size указан, он используется как проверка размера.
    """
    map_path = Path(__file__).parent / "map.txt"
    
    if not map_path.exists():
        print(f"⚠️ Файл {map_path} не найден! Генерирую случайную карту {grid_size or 15}x{grid_size or 15}.")
        return [
            [
                create_cell(posx=x, posy=y, sugar=rand.randint(0, 4), spicy=rand.randint(0, 4))
                for x in range(grid_size or 15)
            ]
            for y in range(grid_size or 15)
        ]

    grid = []
    with open(map_path, 'r') as f:
        lines = f.readlines()
        
    # Очищаем строки от пробелов и пустых строк
    clean_lines = [line.strip() for line in lines if line.strip()]
    
    actual_rows = len(clean_lines)
    actual_cols = len(clean_lines[0].split()) if actual_rows > 0 else 0
    
    if grid_size and (actual_rows != grid_size or actual_cols != grid_size):
        print(f"⚠️ Размер карты в файле ({actual_rows}x{actual_cols}) не совпадает с grid_size={grid_size}. Использую размер из файла.")

    print(f"🗺️ Загружаю карту из map.txt: {actual_rows}x{actual_cols}")

    for y, line in enumerate(clean_lines):
        row = []
        values = line.split()
        for x, val_str in enumerate(values):
            try:
                resource_val = int(val_str)
                # В твоем map.txt одна цифра - это и сахар, и специи одновременно? 
                # Или это только сахар? Обычно в Sugarscape две разные карты.
                # Допустим, что это базовый уровень сахара, а специи генерируем случайно или зеркально.
                # Для простоты пока сделаем: сахар = значение из файла, специи = то же значение (или рандом).
                
                # Вариант А: Зеркальная карта специй (как в классике)
                # Но так как у нас один файл, давай сделаем так:
                # Sugar = значение из файла
                # Spice = (max_val - значение из файла) или просто рандом 0-2
                
                sugar = resource_val
                spicy = max(0, resource_val - rand.randint(0, 2)) # Немного вариативности для специй
                
                row.append(create_cell(posx=x, posy=y, sugar=sugar, spicy=spicy))
            except ValueError:
                # Если встретился нецифровой символ, ставим 0
                row.append(create_cell(posx=x, posy=y, sugar=0, spicy=0))
        grid.append(row)
        
    return grid