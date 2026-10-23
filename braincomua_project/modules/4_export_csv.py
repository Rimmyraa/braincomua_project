"""
Exports all records from the Product model to a CSV file in the results folder
"""
from load_django import *
from parser_app.models import *

import os
import csv
import json

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(project_dir, 'results', 'products.csv')

fields = [
    'title', 'color', 'memory', 'manufacturer', 'price', 'sale_price',
    'images', 'product_code', 'reviews_count', 'screen_diagonal',
    'screen_resolution', 'specifications',
]

with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(fields)

    for item in Product.objects.all():
        writer.writerow([
            item.title,
            item.color,
            item.memory,
            item.manufacturer,
            item.price,
            item.sale_price,
            json.dumps(item.images, ensure_ascii=False),
            item.product_code,
            item.reviews_count,
            item.screen_diagonal,
            item.screen_resolution,
            json.dumps(item.specifications, ensure_ascii=False),
        ])

print(f'Saved to {file_path}')