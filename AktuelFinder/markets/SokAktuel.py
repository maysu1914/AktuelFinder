import datetime
from urllib.parse import urljoin

from lxml import html

from .Aktuel import Aktuel
from ..operations.PdfTask import *


def clear():  # https://stackoverflow.com/a/4810595
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')


class SokAktuel(Aktuel):
    market = "ŞOK"
    url = 'https://kurumsal.sokmarket.com.tr/haftanin-firsatlari/firsatlar'

    def get_aktuels(self):
        try:
            page_content = self.get_content(self.url)
            self.aktuels += self.get_current_aktuels(page_content)
        except requests.exceptions.ConnectionError as e:
            print('ŞOK campaign check is failed!')
            # print(e, 8)
            raise
        return self.aktuels

    def get_current_aktuels(self, page_content):
        aktuels = []
        threads = {}
        try:
            tree = html.fromstring(str(page_content))

            currents = [urljoin(self.url, tree.xpath('//html/body/div[1]/div[4]/div[1]/a/@href')[0]),
                        urljoin(self.url, tree.xpath('//html/body/div[1]/div[4]/div[2]/a/@href')[0])]
            for index, url in enumerate(currents):
                threads[index] = {
                    'thread': self.executor.submit(download_pdf, url),
                    'url': url
                }

            for index, data in threads.items():
                filename = data['thread'].result()
                if filename is not None:
                    aktuel = {'magaza': 'ŞOK'}
                    aktuel['aktuel'] = get_pdf_title(filename)
                    aktuel['durum'] = 'new'
                    aktuel['tarih'] = str(datetime.datetime.now())
                    aktuel['url'] = data['url']
                    aktuels.append(aktuel)
                else:
                    pass
            clear()
        except Exception as e:
            clear()
            print(e, 9)
            raise
        return aktuels
