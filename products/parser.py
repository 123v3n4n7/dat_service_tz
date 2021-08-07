from products.models import Category, Product
import requests
import json
from bs4 import BeautifulSoup
import urllib.request
import os
from trainees_one.settings import BASE_DIR
import asyncio
import aiohttp


class CitilinkParse:
    """Класс для парсинга сайта Citilink.ru по трём категориям"""
    """Запускается путём вызова main_method"""
    """Создаёт объекты Категорий и Товаров"""
    def __init__(self):
        self.get_response = requests.get('https://www.citilink.ru/catalog/')
        self.soup = BeautifulSoup(self.get_response.text, 'html.parser')
        self.category_names = ['Смартфоны', 'Web-камеры', 'Сетевые хранилища NAS']

    def main_method(self):
        for category in self.category_names:
            try:
                os.makedirs(str(BASE_DIR) + '/' + 'media' + '/products_images/' + category + '/')
            except Exception:
                pass
        for element in self.soup.find_all('li', class_='CatalogLayout__children-item'):
            name = element.find('a').getText()
            if name in self.category_names:
                href = element.find('a')['href']
                Category.objects.get_or_create(name=name, href=href)
            else:
                pass
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [asyncio.ensure_future(self.download(category)) for category in
                 Category.objects.all()]
        tasks = asyncio.gather(*tasks)
        loop.run_until_complete(tasks)
        print('Done')

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text(encoding='utf-8')

    async def download(self, category):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, category.href)
            await self.parse_product(html, category)

    async def parse_product(self, html, category):
        soup = BeautifulSoup(html, 'html.parser')
        category_name = category.name
        for element in soup.find_all('div', class_='product_data__gtm-js product_data__pageevents-js '
                                                  'ProductCardHorizontal js--ProductCardInListing '
                                                  'js--ProductCardInWishlist'):
            x = element.find('source')
            image_name = x['srcset'].split('/')[-1]
            element_dict = json.loads(element['data-params'])
            name = element_dict['shortName']
            price = element_dict['price']
            urllib.request.urlretrieve(x['srcset'], os.path.
                                       join(BASE_DIR, f'media/products_images/{category_name}/{image_name}'))
            Product.objects.get_or_create(name=name, price=price, category=category,
                                          image=f'products_images/{category_name}/{image_name}')
