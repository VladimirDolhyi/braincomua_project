"""
Script for searching and parsing product details from brain.com.ua using Playwright.
"""
from pprint import pprint
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from load_django import * # noqa
from parser_app.models import Phone

url = 'https://brain.com.ua'
search_query = 'Apple iPhone 15 128GB Black'

product: dict[str, Any] = {}

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--start-maximized', '--disable-blink-features=AutomationControlled'],
    )
    context = browser.new_context(no_viewport=True)
    page = context.new_page()

    try:
        # Open the main page
        page.goto(url, wait_until='domcontentloaded')

        # Type the search query sequentially into the visible desktop search bar
        search_input = page.locator(
            "//div[contains(@class, 'header-bottom-in')]//input[@class='quick-search-input']"
        )
        search_input.click()
        search_input.press_sequentially(search_query, delay=50)

        # Click the Find button via JS evaluate to avoid autocomplete interception
        search_button = page.locator(
            "//div[contains(@class, 'header-bottom-in')]//input[@class='search-button-first-form']"
        )
        search_button.evaluate("el => el.click()")

        # Wait until search results with the requested product appear
        first_product_link = page.locator("//div[contains(@class, 'br-pp-desc')]//a").first
        first_product_link.wait_for(state='visible', timeout=20000)

        # Click on the first product in search results
        first_product_link.click()

        # Wait until the product page title is loaded
        page.locator("//h1[contains(@class, 'main-title')]").wait_for(state='attached', timeout=20000)

        # Collect product information
        try:
            title_text = page.locator("//h1[contains(@class, 'main-title')]").first.text_content(timeout=2000)
            product['title'] = title_text.strip() if title_text else None
        except PlaywrightTimeoutError:
            product['title'] = None

        # Find the characteristics container once to avoid code duplication
        char_wrapper = page.locator("//div[contains(@class, 'br-characteristics-wrapper')]").first

        try:
            color_text = char_wrapper.locator(
                "xpath=.//span[text()='Колір']/following-sibling::span"
            ).first.text_content(timeout=2000)
            product['color'] = color_text.strip() if color_text else None
        except PlaywrightTimeoutError:
            product['color'] = None

        try:
            memory_text = char_wrapper.locator(
                "xpath=.//span[text()=\"Вбудована пам'ять\"]/following-sibling::span"
            ).first.text_content(timeout=2000)
            product['memory'] = memory_text.strip() if memory_text else None
        except PlaywrightTimeoutError:
            product['memory'] = None

        try:
            brand_text = char_wrapper.locator(
                "xpath=.//span[text()='Виробник']/following-sibling::span"
            ).first.text_content(timeout=2000)
            product['brand'] = brand_text.strip() if brand_text else None
        except PlaywrightTimeoutError:
            product['brand'] = None

        try:
            product['price'] = float(
                page.locator("//meta[@property='product:price:amount']").first.get_attribute('content', timeout=2000)
            )
        except (PlaywrightTimeoutError, TypeError, ValueError):
            product['price'] = None

        try:
            product['promo_price'] = float(
                page.locator("//div[contains(@class, 'br-pr-price')]//*[contains(@class, 'red-price')]")
                .first.text_content(timeout=2000).replace(' ', '').strip()
            )
        except (PlaywrightTimeoutError, AttributeError, TypeError, ValueError):
            product['promo_price'] = None

        try:
            code_text = page.locator("//span[contains(@class, 'br-pr-code-val')]").first.text_content(timeout=2000)
            product['code'] = code_text.strip() if code_text else None
        except PlaywrightTimeoutError:
            product['code'] = None

        try:
            diagonal_text = char_wrapper.locator(
                "xpath=.//span[text()='Діагональ екрана']/following-sibling::span"
            ).first.text_content(timeout=2000)
            product['screen_diagonal'] = diagonal_text.strip() if diagonal_text else None
        except PlaywrightTimeoutError:
            product['screen_diagonal'] = None

        try:
            resolution_text = char_wrapper.locator(
                "xpath=.//span[text()='Роздільна здатність екрану']/following-sibling::span"
            ).first.text_content(timeout=2000)
            product['screen_resolution'] = resolution_text.strip() if resolution_text else None
        except PlaywrightTimeoutError:
            product['screen_resolution'] = None

        try:
            reviews_text = page.locator("//a[contains(@class, 'reviews-count')]//span").first.text_content(timeout=2000)
            product['reviews_count'] = int(reviews_text.strip())
        except (PlaywrightTimeoutError, TypeError, ValueError):
            product['reviews_count'] = None

        try:
            photo_elements = page.locator("//img[contains(@class, 'dots-image')]").all()
            photos = list(dict.fromkeys(
                img.get_attribute('data-big-picture-src')
                for img in photo_elements
                if img.get_attribute('data-big-picture-src')
            ))
            product['photos'] = photos if photos else None
        except PlaywrightTimeoutError:
            product['photos'] = None

        characteristics = {}
        try:
            rows = char_wrapper.locator("xpath=.//div[contains(@class, 'br-pr-chr-item')]//div/div").all()
            for row in rows:
                spans = row.locator("xpath=./span").all()
                if len(spans) == 2:
                    title = ' '.join((spans[0].text_content() or '').split()).rstrip(':')
                    value = ' '.join((spans[1].text_content() or '').split()).strip()
                    if title and value:
                        characteristics[title] = value
            product['characteristics'] = characteristics if characteristics else None
        except PlaywrightTimeoutError:
            product['characteristics'] = None

    finally:
        browser.close()

# Print collected data using pprint
pprint(product, sort_dicts=False)

# Save to DB via get_or_create without defaults
obj, created = Phone.objects.get_or_create(**product)

print(f"DB status: {'Created' if created else 'Already exists'} -> {obj}")
