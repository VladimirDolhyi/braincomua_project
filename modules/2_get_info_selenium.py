"""
Script for searching and parsing product details from brain.com.ua using Selenium and saving them to PostgreSQL.
"""
from pprint import pprint
from typing import Any

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

from load_django import * # noqa
from parser_app.models import Phone

url = 'https://brain.com.ua'
search_query = 'Apple iPhone 15 128GB Black'

driver = Driver(uc=True)
driver.maximize_window()
wait = WebDriverWait(driver, 20)

product: dict[str, Any] = {}

try:
    # Open the main page
    driver.get(url)

    # Enter the search query into the visible desktop search bar
    search_input = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'header-bottom-in')]//input[@class='quick-search-input']")
        )
    )
    search_input.clear()
    search_input.send_keys(search_query)

    # Click the Find button via JS to avoid header/autocomplete interception
    search_button = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'header-bottom-in')]//input[@class='search-button-first-form']")
        )
    )
    driver.execute_script('arguments[0].click();', search_button)

    # Click on the first product in search results
    first_product_link = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'br-pp-desc')]//a"))
    )
    first_product_link.click()

    # Wait until the product page title is loaded
    wait.until(
        EC.presence_of_element_located((By.XPATH, "//h1[@class='main-title']"))
    )

    # Collect product information
    try:
        title_el = driver.find_element(By.XPATH, "//h1[contains(@class, 'main-title')]")
        product['title'] = title_el.get_attribute('textContent').strip()
    except NoSuchElementException:
        product['title'] = None

    # Find the characteristics container once to avoid code duplication
    try:
        char_wrapper = driver.find_element(By.XPATH, "//div[contains(@class, 'br-characteristics-wrapper')]")
    except NoSuchElementException:
        char_wrapper = None

    try:
        color_el = char_wrapper.find_element(By.XPATH, ".//span[text()='Колір']/following-sibling::span")
        product['color'] = color_el.get_attribute('textContent').strip()
    except (AttributeError, NoSuchElementException):
        product['color'] = None

    try:
        memory_el = char_wrapper.find_element(By.XPATH, './/span[text()="Вбудована пам\'ять"]/following-sibling::span')
        product['memory'] = memory_el.get_attribute('textContent').strip()
    except (AttributeError, NoSuchElementException):
        product['memory'] = None

    try:
        brand_el = char_wrapper.find_element(By.XPATH, ".//span[text()='Виробник']/following-sibling::span")
        product['brand'] = brand_el.get_attribute('textContent').strip()
    except (AttributeError, NoSuchElementException):
        product['brand'] = None

    try:
        product['price'] = float(
            driver.find_element(By.XPATH, "//meta[@property='product:price:amount']").get_attribute('content')
        )
    except (NoSuchElementException, TypeError, ValueError):
        product['price'] = None

    try:
        product['promo_price'] = float(
            driver.find_element(By.XPATH, "//div[contains(@class, 'br-pr-price')]//*[contains(@class, 'red-price')]")
            .get_attribute('textContent').replace(' ', '').strip()
        )
    except (NoSuchElementException, TypeError, ValueError):
        product['promo_price'] = None

    try:
        code_el = driver.find_element(By.XPATH, "//span[contains(@class, 'br-pr-code-val')]")
        product['code'] = code_el.get_attribute('textContent').strip()
    except NoSuchElementException:
        product['code'] = None

    try:
        diagonal_el = char_wrapper.find_element(By.XPATH, ".//span[text()='Діагональ екрана']/following-sibling::span")
        product['screen_diagonal'] = diagonal_el.get_attribute('textContent').strip()
    except (AttributeError, NoSuchElementException):
        product['screen_diagonal'] = None

    try:
        resolution_el = char_wrapper.find_element(By.XPATH,
                                                  ".//span[text()='Роздільна здатність екрану']/following-sibling::span")
        product['screen_resolution'] = resolution_el.get_attribute('textContent').strip()
    except (AttributeError, NoSuchElementException):
        product['screen_resolution'] = None

    try:
        reviews_el = driver.find_element(By.XPATH, "//a[contains(@class, 'reviews-count')]//span")
        product['reviews_count'] = int(reviews_el.get_attribute('textContent').strip())
    except (NoSuchElementException, TypeError, ValueError):
        product['reviews_count'] = None

    try:
        photo_elements = driver.find_elements(By.XPATH, "//img[contains(@class, 'dots-image')]")
        photos = list(dict.fromkeys(
            img.get_attribute('data-big-picture-src')
            for img in photo_elements
            if img.get_attribute('data-big-picture-src')
        ))
        product['photos'] = photos if photos else None
    except NoSuchElementException:
        product['photos'] = None

    characteristics = {}
    try:
        rows = char_wrapper.find_elements(By.XPATH, ".//div[contains(@class, 'br-pr-chr-item')]//div/div")
        for row in rows:
            spans = row.find_elements(By.XPATH, "./span")
            if len(spans) == 2:
                title = ' '.join(spans[0].get_attribute('textContent').split()).strip().replace(':', '')
                value = ' '.join(spans[1].get_attribute('textContent').split()).strip()
                if title and value:
                    characteristics[title] = value
        product['characteristics'] = characteristics if characteristics else None
    except (AttributeError, NoSuchElementException):
        product['characteristics'] = None

finally:
    driver.quit()

# Print collected data using pprint
pprint(product, sort_dicts=False)

# Save to DB via get_or_create without defaults
obj, created = Phone.objects.get_or_create(**product)

print(f"DB status: {'Created' if created else 'Already exists'} -> {obj}")
