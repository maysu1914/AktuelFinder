import datetime

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
    url = 'https://kurumsal.sokmarket.com.tr'

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
        try:
            tree = html.fromstring(str(page_content))

            currents = [self.url + tree.xpath('//html/body/div[1]/div[3]/div[1]/div[2]/p/a/@href')[0],
                        self.url + tree.xpath('//html/body/div[1]/div[3]/div[3]/div[2]/p/a/@href')[0]]
            for brosur in currents:
                filename = download_pdf(brosur)
                if filename is not None:
                    aktuel = {'magaza': 'ŞOK'}
                    aktuel['aktuel'] = get_pdf_title(filename)
                    aktuel['durum'] = 'new'
                    aktuel['tarih'] = str(datetime.datetime.now())
                    aktuel['url'] = brosur
                    aktuels.append(aktuel)
                else:
                    pass
            clear()
        except Exception as e:
            clear()
            print(e, 9)
            raise
        return aktuels
