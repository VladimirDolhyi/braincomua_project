"""
Script for parsing product details from brain.com.ua and saving them to PostgreSQL.
"""
from pprint import pprint
from typing import Any

import requests
from bs4 import BeautifulSoup

from load_django import * # noqa
from parser_app.models import Phone

headers = {
	'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0',
	'Accept-Language': 'uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	'Referer': 'https://www.google.com/',
	'Connection': 'keep-alive',
	'Cache-Control': 'no-cache',
	'Pragma': 'no-cache',
	'Upgrade-Insecure-Requests': '1',
	'DNT': '1',
	'Sec-Fetch-Dest': 'document',
	'Sec-Fetch-Mode': 'navigate',
	'Sec-Fetch-Site': 'cross-site',
	'Sec-Fetch-User': '?1',
	'TE': 'Trailers',
}

url = 'https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html'

product: dict[str, Any] = {}

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

try:
	product['title'] = soup.select_one('h1.main-title').text.strip()
except AttributeError:
	product['title'] = None

# Find the characteristics container once to avoid code duplication
char_wrapper = soup.select_one('.br-characteristics-wrapper')

try:
	product['color'] = char_wrapper.find('span', string='Колір').find_next('span').text.strip()
except AttributeError:
	product['color'] = None

try:
	product['memory'] = char_wrapper.find('span', string="Вбудована пам'ять").find_next('span').text.strip()
except AttributeError:
	product['memory'] = None

try:
	product['brand'] = char_wrapper.find('span', string='Виробник').find_next('span').text.strip()
except AttributeError:
	product['brand'] = None

try:
	product['price'] = float(soup.find('meta', property='product:price:amount')['content'])
except (AttributeError, KeyError, TypeError, ValueError):
	product['price'] = None

try:
	product['promo_price'] = float(soup.select_one('.br-pr-price .red-price').text.replace(' ', '').strip())
except (AttributeError, TypeError, ValueError):
	product['promo_price'] = None

try:
	product['code'] = soup.select_one('.br-pr-code-val').text.strip()
except AttributeError:
	product['code'] = None

try:
	product['screen_diagonal'] = char_wrapper.find('span', string='Діагональ екрана').find_next('span').text.strip()
except AttributeError:
	product['screen_diagonal'] = None

try:
	product['screen_resolution'] = char_wrapper.find('span', string='Роздільна здатність екрану').find_next('span').text.strip()
except AttributeError:
	product['screen_resolution'] = None

try:
	product['reviews_count'] = int(soup.select_one(".reviews-count span").text.strip())
except (AttributeError, TypeError, ValueError):
	product['reviews_count'] = None

try:
	photos = [
		img.get('data-big-picture-src')
		for img in soup.select('.dots-image')
		if img.get('data-big-picture-src')
	]
	product['photos'] = photos if photos else None
except AttributeError:
	product['photos'] = None

characteristics = {}
try:
	for row in char_wrapper.select('.br-pr-chr-item div > div'):
		spans = row.find_all('span', recursive=False)
		if len(spans) == 2:
			title = ' '.join(spans[0].text.split()).strip().replace(':', '')
			value = ' '.join(spans[1].text.split()).strip()
			if title and value:
				characteristics[title] = value
	product['characteristics'] = characteristics if characteristics else None
except AttributeError:
	product['characteristics'] = None

# Print collected data using pprint
pprint(product, sort_dicts=False)

obj, created = Phone.objects.get_or_create(**product)

print(f"DB status: {'Created' if created else 'Already exists'} -> {obj}")
