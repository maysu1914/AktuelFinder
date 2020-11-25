import ast
import datetime
import json
import os
import requests
import sys
from multiprocessing import Pool
from urllib.parse import urlparse, urljoin

from PyPDF2 import PdfFileReader
from bs4 import BeautifulSoup
from lxml import html

if not sys.warnoptions:  # https://stackoverflow.com/questions/49939085/xref-table-not-zero-indexed-id-numbers-for-objects-will-be-corrected-wont-con
    import warnings

    warnings.simplefilter("ignore")


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


class PdfTask:
    @staticmethod
    def download_pdf(url):
        parse = urlparse(url)
        base_url = parse.scheme + '://' + parse.netloc
        try:
            redirect = requests.get(url, allow_redirects=False)
        except requests.exceptions.ConnectionError as e:
            print(e, 2)
            raise

        if redirect.status_code == 302:
            url = base_url + redirect.headers['location']
        else:
            pass

        filename = url.split('/')[-1]

        if not PdfTask.is_pdf(filename):
            return None

        if os.path.isfile(filename):
            return filename.strip()
        else:
            print(filename, 'downloading')
            request = requests.get(url)
            # https://stackoverflow.com/questions/34503412/download-and-save-pdf-file-with-python-requests-module
            with open(filename, 'wb') as f:
                f.write(request.content)
            return filename.strip()

    @staticmethod
    def is_pdf(filename):
        if filename[-4:] != '.pdf':
            return False
        else:
            return True

    @staticmethod
    def get_pdf_title(filename):
        # http://www.blog.pythonlibrary.org/2018/04/10/extracting-pdf-metadata-and-text-with-python/
        with open(filename, 'rb') as f:
            pdf = PdfFileReader(f)
            info = pdf.getDocumentInfo()
            pdf.getNumPages()
        title = info.title if info else filename
        return title.strip()


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
            pdf_task = PdfTask()

            currents = [self.url + tree.xpath('//html/body/div[1]/div[3]/div[1]/div[2]/p/a/@href')[0],
                        self.url + tree.xpath('//html/body/div[1]/div[3]/div[3]/div[2]/p/a/@href')[0]]
            for brosur in currents:
                filename = pdf_task.download_pdf(brosur)
                if filename is not None:
                    aktuel = {'magaza': 'ŞOK'}
                    aktuel['aktuel'] = pdf_task.get_pdf_title(filename)
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


class AktuelDB:

    def __init__(self, filename):
        self.filename = filename

    def save_aktuels(self, data):
        old_filename = self.filename + ".txt.{}".format(datetime.datetime.now().strftime("%Y%m%d%H%M"))
        if os.path.isfile(self.filename + ".txt"):
            if os.path.isfile(old_filename):
                os.remove(old_filename)
            else:
                pass
            os.rename(self.filename + ".txt", old_filename)
        else:
            pass

        with open('{name}.txt'.format(name=self.filename), 'w', encoding="utf8") as file:
            file.write(json.dumps(data))
        print('\n{name}.txt created.'.format(name=self.filename))

    def read_aktuels(self):
        try:
            if os.path.isfile(self.filename + ".txt"):
                with open('{}.txt'.format(self.filename), encoding='utf-8') as f:
                    data = f.readline()

                data = ast.literal_eval(data)
                data = sorted(data, key=lambda k: k['tarih'], reverse=False)
                data = sorted(data, key=lambda k: k['magaza'], reverse=False)
                return data
            else:
                return []
        except Exception as e:
            print(e, 10)
            return []

    def read_aktuel(self, aktuel):
        local_aktuel = []
        if os.path.isfile(self.filename + ".txt"):
            with open('{}.txt'.format(self.filename), encoding='utf-8') as f:
                data = f.readline()
            for i in ast.literal_eval(data):
                if i['magaza'] == aktuel:
                    local_aktuel.append(i)
            local_aktuel = sorted(local_aktuel, key=lambda k: k['tarih'], reverse=False)
            local_aktuel = sorted(local_aktuel, key=lambda k: k['magaza'], reverse=False)
            return local_aktuel
        else:
            return local_aktuel


def clear():  # https://stackoverflow.com/a/4810595
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')


class AktuelFinder:

    def __init__(self):
        self.exception = False
        self.markets = {'BİM': BimAktuel, 'A101': A101Aktuel, 'ŞOK': SokAktuel}
        self.aktuel_db = AktuelDB('aktuels')
        self.active_aktuels = {}
        self.still_active_aktuels = {}
        self.expired_aktuels = {}
        self.new_aktuels = {}

    def get_aktuels(self):
        aktuels = []
        processes = {}
        with Pool() as pool:
            for name, market in self.markets.items():
                processes[name] = pool.apply_async(market().get_aktuels)
            for name, process in processes.items():
                try:
                    aktuels += process.get()
                except requests.exceptions.ConnectionError as e:
                    # print(e, 11)
                    aktuels += self.aktuel_db.read_aktuel(name)
                    self.exception = True

        aktuels = sorted(aktuels, key=lambda k: k['tarih'], reverse=False)
        aktuels = sorted(aktuels, key=lambda k: k['magaza'], reverse=False)

        return aktuels

    def show_summary(self):
        saved_aktuels = self.aktuel_db.read_aktuels()
        aktuels = self.get_aktuels()

        self.active_aktuels = self.get_active_aktuels(saved_aktuels)
        self.still_active_aktuels = {}
        self.expired_aktuels = self.get_expired_aktuels(aktuels, self.active_aktuels)
        self.new_aktuels = self.get_new_aktuels(aktuels, self.active_aktuels)

        if self.exception:
            print('')

        if self.active_aktuels:
            print("Chosen campaigns:")
            for key, active_aktuel in self.active_aktuels.items():
                print(active_aktuel['magaza'], active_aktuel['aktuel'])
            print('')
        else:
            pass

        if self.expired_aktuels:
            print("Expired campaigns:")
            for key, expired_aktuel in self.expired_aktuels.items():
                print(str(key) + '.', expired_aktuel['magaza'], expired_aktuel['aktuel'])
            print(
                "* Please enter the IDs of campaigns you want to delete by adding ':' to beginning. (Enter :0 for deleting all of them)\n")
        else:
            pass

        if self.new_aktuels:
            print("New campaigns:")
            for key, new_aktuel in self.new_aktuels.items():
                print(str(key) + '.', new_aktuel['magaza'], new_aktuel['aktuel'])
            print("* Please enter the IDs of campaigns you choose. (Enter 0 for choose all of them)\n")
        else:
            pass

        if not self.expired_aktuels and not self.new_aktuels:
            print("No new campaign.")
            input()

    @staticmethod
    def get_active_aktuels(saved_aktuels):
        active_aktuels = {}
        count = 1

        for aktuel in saved_aktuels:
            if aktuel['durum'] == 'active':
                active_aktuels[count] = aktuel
                count += 1
            else:
                pass

        return active_aktuels

    def get_expired_aktuels(self, aktuels, active_aktuels):
        expired_aktuels = {}
        count = 1
        count0 = 1

        for key, active_aktuel in active_aktuels.items():
            active_market = active_aktuel['magaza']
            active_aktuel_name = active_aktuel['aktuel']

            exist = False
            for aktuel in aktuels:
                if aktuel['magaza'] == active_market and aktuel['aktuel'] == active_aktuel_name:
                    exist = True
                    break
            if not exist:
                expired_aktuels[count] = active_aktuel
                count += 1
            else:
                self.still_active_aktuels[count0] = active_aktuel
                count0 += 1

        return expired_aktuels

    @staticmethod
    def get_new_aktuels(aktuels, active_aktuels):
        new_aktuels = {}
        count = 1

        for aktuel in aktuels:
            market = aktuel['magaza']
            aktuel_name = aktuel['aktuel']

            exist = False
            for key, active_aktuel in active_aktuels.items():
                if active_aktuel['magaza'] == market and active_aktuel['aktuel'] == aktuel_name:
                    exist = True
                    break
            if not exist:
                new_aktuels[count] = aktuel
                count += 1
        return new_aktuels

    def command(self):
        user_inputs = []
        if self.expired_aktuels or self.new_aktuels:
            print("* Split every command with ',' character. (Enter '#' for saving the session)\n")
            while not self.command_control(user_inputs, len(self.new_aktuels), len(self.expired_aktuels)):
                user_inputs = input("Command Line: ")
                user_inputs = self.command_optimizer(user_inputs)
            self.command_execution(user_inputs)
            self.save_aktuels()
        else:
            pass

    @staticmethod
    def command_control(user_inputs, new_max, expired_max):
        try:
            if not user_inputs:
                return False
            for key in user_inputs:
                if key == '#':
                    return True
                elif key[0] == ':':
                    if not key[1:].isnumeric() or int(key[1:]) < 0 or int(key[1:]) > expired_max or expired_max == 0:
                        return False
                elif not key.isnumeric() or int(key) < 0 or int(key) > new_max or new_max == 0:
                    return False
                else:
                    pass
            return True
        except Exception as e:
            print(e, 12)
            return False

    @staticmethod
    def command_optimizer(user_inputs):
        user_inputs = sorted(set(''.join(user_inputs.split()).split(',')))
        for a in user_inputs:
            if not a:
                user_inputs.remove(a)

        return user_inputs

    def command_execution(self, user_inputs):
        for user_input in user_inputs:
            if user_input == '#':
                break
            elif user_input[0] == ':':
                if user_input[1] == '0':
                    self.expired_aktuels = {}
                else:
                    self.expired_aktuels.pop(int(user_input[1:]), None)
            elif user_input == '0':
                for key, new_aktuel in self.new_aktuels.items():
                    new_aktuel['durum'] = 'active'
            else:
                self.new_aktuels[int(user_input)]['durum'] = 'active'

    def save_aktuels(self):
        aktuels = []
        for key, value in self.new_aktuels.items():
            aktuels.append(value)
        for key, value in self.expired_aktuels.items():
            aktuels.append(value)
        for key, value in self.still_active_aktuels.items():
            aktuels.append(value)

        self.aktuel_db.save_aktuels(aktuels)


if __name__ == "__main__":
    app = AktuelFinder()
    while True:
        app.show_summary()
        app.command()
        clear()  # when running on command window
