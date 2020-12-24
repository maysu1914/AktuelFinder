import datetime
import os
from urllib.parse import urljoin

import requests

from .Aktuel import Aktuel


def clear():  # https://stackoverflow.com/a/4810595
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')


class A101Aktuel(Aktuel):
    market = "A101"
    url = 'https://www.a101.com.tr/afisler'

    def get_aktuels(self):
        try:
            page_content = self.get_content(self.url)
            self.aktuels += self.get_current_aktuels(page_content)
        except requests.exceptions.ConnectionError as e:
            print('A101 campaign check is failed!')
            # print(e, 6)
            raise
        return self.aktuels

    def get_current_aktuels(self, page_content):
        aktuels = []
        try:
            currents = page_content.find(
                "div", "brochures-list").find("ul", recursive=False)
            for brosur in currents.find_all("li", recursive=False):
                aktuel = {'magaza': 'A101'}
                aktuel['aktuel'] = brosur.find("span").text
                aktuel['durum'] = 'new'
                aktuel['tarih'] = str(datetime.datetime.now())
                aktuel['url'] = urljoin(self.url, brosur.a['href'])
                aktuels.append(aktuel)
            clear()
        except Exception as e:
            clear()
            print(e, 7)
            raise
        return aktuels
