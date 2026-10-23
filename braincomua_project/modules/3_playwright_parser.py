"""
Searches for a product on brain.com.ua via the site search,
parses its data using Playwright and saves it to the Product model
"""
from load_django import *
from parser_app.models import *

import re
from pprint import pprint
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

product = {}

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    page.set_default_timeout(15000)

    # Step 1: open the main page
    page.goto('https://brain.com.ua/')

    # Step 2: type the search query
    search_input = page.locator('xpath=//div[@class="header-bottom-in"]//input[@class="quick-search-input"]')
    search_input.fill('Apple iPhone 15 128GB Black')
    page.wait_for_timeout(1000)

    # Step 3: click the search button
    search_button = page.locator('xpath=//div[@class="header-bottom-in"]//input[@class="search-button-first-form"]')
    search_button.dispatch_event('click')

    # Step 4: open the first search result
    first_result = page.locator('xpath=(//div[contains(@class, "br-pp-desc")]/a)[1]')
    first_result.wait_for(timeout=90000)
    first_result.click()

    page.locator('xpath=//h1[contains(@class, "main-title")]').first.wait_for(state='attached', timeout=90000)
    page.wait_for_timeout(2000)

    # Step 5: collect product data
    try:
        title_text = page.locator('xpath=//h1[contains(@class, "main-title")]').first.text_content(timeout=3000)
        product['title'] = ' '.join(title_text.split()) or None
    except PlaywrightTimeoutError:
        product['title'] = None

    try:
        current_price = int(page.locator('xpath=//meta[@property="product:price:amount"]').first.get_attribute('content', timeout=3000))
    except (PlaywrightTimeoutError, TypeError, ValueError):
        current_price = None

    try:
        old_price_text = page.locator(
            'xpath=(//div[contains(@class, "main-price-block")]//div[contains(@class, "br-pr-op")]//span)[1]'
        ).text_content(timeout=3000)
        old_price = int(re.sub(r'\D', '', old_price_text))
    except (PlaywrightTimeoutError, ValueError):
        old_price = None

    if old_price:
        product['price'] = old_price
        product['sale_price'] = current_price
    else:
        product['price'] = current_price
        product['sale_price'] = None

    try:
        product['manufacturer'] = page.locator('xpath=//meta[@property="product:brand"]').first.get_attribute('content', timeout=3000)
    except PlaywrightTimeoutError:
        product['manufacturer'] = None

    try:
        product['product_code'] = page.locator('xpath=//span[@class="br-pr-code-val"]').first.text_content(timeout=3000).strip()
    except PlaywrightTimeoutError:
        product['product_code'] = None

    try:
        reviews_text = page.locator('xpath=//a[contains(@class, "brackets-reviews")]').first.text_content(timeout=3000)
        product['reviews_count'] = int(re.search(r'\d+', reviews_text).group())
    except (PlaywrightTimeoutError, AttributeError):
        product['reviews_count'] = None

    images = page.locator(
        'xpath=//div[contains(@class, "main-pictures-block")]//img[not(ancestor::div[contains(@class, "slick-cloned")])]'
    ).all()
    image_urls = [img.get_attribute('src') for img in images]
    product['images'] = list(dict.fromkeys(image_urls)) or None

    try:
        product['color'] = page.locator(
            'xpath=//span[text()="Колір"]/following-sibling::span'
        ).first.text_content(timeout=3000).strip()
    except PlaywrightTimeoutError:
        product['color'] = None

    try:
        product['memory'] = page.locator(
            "xpath=//span[text()=\"Вбудована пам'ять\"]/following-sibling::span"
        ).first.text_content(timeout=3000).strip()
    except PlaywrightTimeoutError:
        product['memory'] = None

    try:
        product['screen_diagonal'] = page.locator(
            'xpath=//span[text()="Діагональ екрану"]/following-sibling::span'
        ).first.text_content(timeout=3000).strip()
    except PlaywrightTimeoutError:
        product['screen_diagonal'] = None

    try:
        product['screen_resolution'] = page.locator(
            'xpath=//span[text()="Роздільна здатність екрану"]/following-sibling::span'
        ).first.text_content(timeout=3000).strip()
    except PlaywrightTimeoutError:
        product['screen_resolution'] = None

    specifications = {}
    rows = page.locator('xpath=//div[contains(@class, "br-pr-chr-item")]//div[count(span)=2]').all()
    for row in rows:
        spans = row.locator('xpath=./span')
        key = ' '.join(spans.nth(0).text_content().split())
        value = ' '.join(spans.nth(1).text_content().split())
        specifications[key] = value
    product['specifications'] = specifications or None

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