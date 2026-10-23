"""
Parses product data from brain.com.ua using Requests and BeautifulSoup
and saves it to the Product model
"""
from load_django import *
from parser_app.models import *

import re
import requests
from bs4 import BeautifulSoup
from pprint import pprint

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36',
    'Accept-Language': 'uk-UA,uk;q=0.9,en;q=0.8',
}

url = 'https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html'

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

product = {}

try:
    product['title'] = soup.find('h1', attrs={'class': 'main-title'}).text.strip()
except AttributeError:
    product['title'] = None

try:
    current_price = int(soup.find('meta', attrs={'property': 'product:price:amount'}).get('content'))
except (AttributeError, TypeError, ValueError):
    current_price = None

try:
    price_block = soup.find('div', attrs={'class': 'main-price-block'})
    old_price_text = price_block.find('div', attrs={'class': 'br-pr-op'}).find('span').text
    old_price = int(re.sub(r'\D', '', old_price_text))
except (AttributeError, ValueError):
    old_price = None

if old_price:
    product['price'] = old_price
    product['sale_price'] = current_price
else:
    product['price'] = current_price
    product['sale_price'] = None

try:
    product['manufacturer'] = soup.find('meta', attrs={'property': 'product:brand'}).get('content')
except AttributeError:
    product['manufacturer'] = None

try:
    product['product_code'] = soup.find('span', attrs={'class': 'br-pr-code-val'}).text.strip()
except AttributeError:
    product['product_code'] = None

try:
    reviews_text = soup.find('a', attrs={'class': 'brackets-reviews'}).text
    product['reviews_count'] = int(re.search(r'\d+', reviews_text).group())
except AttributeError:
    product['reviews_count'] = None

try:
    pictures_block = soup.find('div', attrs={'class': 'main-pictures-block'})
    product['images'] = [img.get('src') for img in pictures_block.find_all('img')]
except AttributeError:
    product['images'] = None

try:
    product['color'] = soup.find('span', string='Колір').find_next_sibling('span').text.strip()
except AttributeError:
    product['color'] = None

try:
    product['memory'] = soup.find('span', string="Вбудована пам'ять").find_next_sibling('span').text.strip()
except AttributeError:
    product['memory'] = None

try:
    product['screen_diagonal'] = soup.find('span', string='Діагональ екрану').find_next_sibling('span').text.strip()
except AttributeError:
    product['screen_diagonal'] = None

try:
    product['screen_resolution'] = soup.find('span', string='Роздільна здатність екрану').find_next_sibling('span').text.strip()
except AttributeError:
    product['screen_resolution'] = None

try:
    specifications = {}
    for group in soup.find_all('div', attrs={'class': 'br-pr-chr-item'}):
        for row in group.find_all('div'):
            spans = row.find_all('span', recursive=False)
            if len(spans) == 2:
                key = spans[0].text.strip()
                value = ' '.join(spans[1].text.split())
                specifications[key] = value
    product['specifications'] = specifications or None
except AttributeError:
    product['specifications'] = None

pprint(product)

obj, created = Product.objects.get_or_create(
    title=product['title'],
    color=product['color'],
    memory=product['memory'],
    manufacturer=product['manufacturer'],
    price=product['price'],
    sale_price=product['sale_price'],
    images=product['images'],
    product_code=product['product_code'],
    reviews_count=product['reviews_count'],
    screen_diagonal=product['screen_diagonal'],
    screen_resolution=product['screen_resolution'],
    specifications=product['specifications'],
)