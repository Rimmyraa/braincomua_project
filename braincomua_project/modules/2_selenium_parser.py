"""
Searches for a product on brain.com.ua via the site search,
parses its data using Selenium and saves it to the Product model
"""
from load_django import *
from parser_app.models import *

import re
import time
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

options = webdriver.ChromeOptions()
options.debugger_address = '127.0.0.1:9222'

driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 15)

# Step 1: open the main page
driver.get('https://brain.com.ua/')

# Step 2: type the search query
search_input = wait.until(EC.element_to_be_clickable(
    (By.XPATH, '//div[@class="header-bottom-in"]//input[@class="quick-search-input"]')
))
search_input.clear()
search_input.send_keys('Apple iPhone 15 128GB Black')
time.sleep(1)

# Step 3: click the search button
search_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, '//div[@class="header-bottom-in"]//input[@class="search-button-first-form"]')
))
driver.execute_script('arguments[0].click();', search_button)

# Step 4: open the first search result
first_result = WebDriverWait(driver, 90).until(EC.element_to_be_clickable(
    (By.XPATH, '(//div[contains(@class, "br-pp-desc")]/a)[1]')
))
first_result.click()

if len(driver.window_handles) > 1:
    driver.switch_to.window(driver.window_handles[-1])

WebDriverWait(driver, 90).until(EC.presence_of_element_located(
    (By.XPATH, '//h1[contains(@class, "main-title")]')
))
time.sleep(2)

# Step 5: collect product data
product = {}

try:
    title_text = driver.find_element(By.XPATH, '//h1[contains(@class, "main-title")]').get_attribute('textContent')
    product['title'] = ' '.join(title_text.split()) or None
except NoSuchElementException:
    product['title'] = None

try:
    current_price = int(driver.find_element(By.XPATH, '//meta[@property="product:price:amount"]').get_attribute('content'))
except (NoSuchElementException, TypeError, ValueError):
    current_price = None

try:
    old_price_text = driver.find_element(
        By.XPATH, '(//div[contains(@class, "main-price-block")]//div[contains(@class, "br-pr-op")]//span)[1]'
    ).get_attribute('textContent')
    old_price = int(re.sub(r'\D', '', old_price_text))
except (NoSuchElementException, ValueError):
    old_price = None

if old_price:
    product['price'] = old_price
    product['sale_price'] = current_price
else:
    product['price'] = current_price
    product['sale_price'] = None

try:
    product['manufacturer'] = driver.find_element(By.XPATH, '//meta[@property="product:brand"]').get_attribute('content')
except NoSuchElementException:
    product['manufacturer'] = None

try:
    product['product_code'] = driver.find_element(
        By.XPATH, '//span[@class="br-pr-code-val"]'
    ).get_attribute('textContent').strip()
except NoSuchElementException:
    product['product_code'] = None

try:
    reviews_text = driver.find_element(By.XPATH, '//a[contains(@class, "brackets-reviews")]').get_attribute('textContent')
    product['reviews_count'] = int(re.search(r'\d+', reviews_text).group())
except (NoSuchElementException, AttributeError):
    product['reviews_count'] = None

try:
    images = driver.find_elements(
        By.XPATH,
        '//div[contains(@class, "main-pictures-block")]//img[not(ancestor::div[contains(@class, "slick-cloned")])]'
    )
    image_urls = [img.get_attribute('src') for img in images]
    product['images'] = list(dict.fromkeys(image_urls)) or None
except NoSuchElementException:
    product['images'] = None

try:
    product['color'] = driver.find_element(
        By.XPATH, '//span[text()="Колір"]/following-sibling::span'
    ).get_attribute('textContent').strip()
except NoSuchElementException:
    product['color'] = None

try:
    product['memory'] = driver.find_element(
        By.XPATH, "//span[text()=\"Вбудована пам'ять\"]/following-sibling::span"
    ).get_attribute('textContent').strip()
except NoSuchElementException:
    product['memory'] = None

try:
    product['screen_diagonal'] = driver.find_element(
        By.XPATH, '//span[text()="Діагональ екрану"]/following-sibling::span'
    ).get_attribute('textContent').strip()
except NoSuchElementException:
    product['screen_diagonal'] = None

try:
    product['screen_resolution'] = driver.find_element(
        By.XPATH, '//span[text()="Роздільна здатність екрану"]/following-sibling::span'
    ).get_attribute('textContent').strip()
except NoSuchElementException:
    product['screen_resolution'] = None

try:
    specifications = {}
    rows = driver.find_elements(By.XPATH, '//div[contains(@class, "br-pr-chr-item")]//div[count(span)=2]')
    for row in rows:
        spans = row.find_elements(By.XPATH, './span')
        key = ' '.join(spans[0].get_attribute('textContent').split())
        value = ' '.join(spans[1].get_attribute('textContent').split())
        specifications[key] = value
    product['specifications'] = specifications or None
except NoSuchElementException:
    product['specifications'] = None

# Step 6: print the result
pprint(product)

# Step 7: save to the database
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