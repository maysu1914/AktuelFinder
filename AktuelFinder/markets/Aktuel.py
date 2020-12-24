import requests
from bs4 import BeautifulSoup


class Aktuel:

    def __init__(self):
        self.aktuels = []

    @staticmethod
    def get_content(url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
            page = requests.get(url, timeout=10, headers=headers)
            page_content = BeautifulSoup(page.content, "lxml")
            return page_content
        except requests.exceptions.ConnectionError as e:
            # print(e, 1)
            raise