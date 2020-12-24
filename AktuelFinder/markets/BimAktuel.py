import datetime
import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .Aktuel import Aktuel


def clear():  # https://stackoverflow.com/a/4810595
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')


class BimAktuel(Aktuel):
    market = "BİM"
    url = 'https://www.bim.com.tr/default.aspx'

    def get_aktuels(self):
        try:
            page_content = self.get_content(self.url)
            self.aktuels += self.get_current_aktuels(page_content)
            self.aktuels += self.get_future_aktuels(page_content)
        except requests.exceptions.ConnectionError as e:
            print('BİM campaign check is failed!')
            # print(e, 3)
            raise
        return self.aktuels

    def get_future_aktuels(self, page_content):
        aktuels = []
        try:
            # https://stackoverflow.com/a/40305745
            futures = page_content.find("div", {"class": "subButtonArea-5"})
            for brosur in futures.find_all('a', 'subButton'):
                aktuel = {'magaza': 'BİM'}
                aktuel['aktuel'] = brosur.text.strip() + ' ' + brosur['href'].split('_')[-1]
                aktuel['durum'] = 'new'
                aktuel['tarih'] = str(datetime.datetime.now())
                aktuel['url'] = urljoin(self.url, brosur['href'])
                aktuels.append(aktuel)
            clear()
        except Exception as e:
            clear()
            print(e, 4)
            raise
        return aktuels

    def get_current_aktuels(self, page_content):
        aktuels = []
        try:
            currents = BeautifulSoup(str(page_content.select(
                'div.subButtonArea.active')), "lxml")  # https://stackoverflow.com/a/40305745
            for brosur in currents.find_all('a', 'subButton'):
                aktuel = {'magaza': 'BİM'}
                aktuel['aktuel'] = brosur.text.strip() + ' ' + brosur['href'].split('_')[-1]
                aktuel['durum'] = 'new'
                aktuel['tarih'] = str(datetime.datetime.now())
                aktuel['url'] = urljoin(self.url, brosur['href'])
                aktuels.append(aktuel)
            clear()
        except Exception as e:
            clear()
            print(e, 5)
            return
        return aktuels
