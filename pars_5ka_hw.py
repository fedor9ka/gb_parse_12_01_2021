import json
import time
from pathlib import Path
import requests

url = 'https://5ka.ru/api/v2/special_offers/'


# ?store=&records_per_page=12&page=1&categories=&ordering=&price_promo__gte=&price_promo__lte=&search=




class Parse_Error(Exception):
    def __init__(self, txt):
        self.txt = txt


class Parse_5ka:

    params = {
        'records_per_page': 100,
        'page': 1
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'
    }

    def __init__(self, start_url, result_path):
        self.start_url = start_url
        self.result_path = result_path

    @staticmethod
    def __get_response(url, *args, **kwargs) -> requests.Response:
        while True:
            try:
                response = requests.get(url, *args, **kwargs)
                if response.status_code > 399:
                    raise Parse_Error('response.status_code')
                return response
                time.sleep(0.1)
            except (requests.RequestException, Parse_Error):
                time.sleep(0.5)
                continue

    def run(self):
        for product in self.parse(self.start_url):
            path = self.result_path.joinpath(f"{product['id']}.json")
            self.save(product, path)

    def parse(self, url):
        params = self.params
        while url:
            response = self.__get_response(url, params=params, headers=self.headers)
            if params:
                params = {}
            data = json.loads(response.text)
            url = data.get('next')
            for product in data.get('results'):
                yield product

    @   staticmethod
    def save(data, file_name):
        with open(f'products/{file_name}.json, 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False)
        print(1)


class ParserCatalog(Parse_5ka):
    def __init__(self, start_url, category_url):
        self.categoty_url = category_url
        super().__init__(start_url)

    def get_categories(self, url):
        response = requests.get(url, headers=self.headers)
        return response.json()

    def run(self):
        for category in self.get_categories(self.categoty_url):
            data = {
                'name': category['parent_group_name'],
                'code': category['parent_group_code'],
                'products': []
            }

            self._params['categorirs'] = category['parent_group_code']

            for products in self.parse(self.start_url):
                data['products'].extend(products)
            self.save_to_json_file(data, category['parent_group_code'])

if __name__ == '__main__':
    # result_path = Path(__file__).parent.joinpath('products')
    # url = 'https://5ka.ru/api/v2/special_offers/'
    # parser = Parse_5ka(url, result_path)
    # parser.run()
    parser = ParserCatalog(
        'https://5ka.ru/api/v2/special_offers/', 'https://5ka.ru/api/v2/categories/'
    )
    parser.run()

print(1)