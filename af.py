import json
import ast
import datetime
import requests
from bs4 import BeautifulSoup
from lxml import html
from lxml import etree
from urllib.parse import urlparse
import os
from PyPDF2 import PdfFileReader
import sys
if not sys.warnoptions: #https://stackoverflow.com/questions/49939085/xref-table-not-zero-indexed-id-numbers-for-objects-will-be-corrected-wont-con
    import warnings
    warnings.simplefilter("ignore")

local_file = ''
aktuel_cekim_hatasi = False

def createAktuelJSONFile(filename,data):
    with open('{name}.txt'.format(name=filename),'w',encoding = "utf8") as file:
        file.write(json.dumps(data))
    print('\n{name}.txt olusturuldu.'.format(name=filename))

def readAktuelsFromJSON(filename):
    try:
        with open('{}.txt'.format(filename), encoding='utf-8') as f:
            data = f.readline()
        return ast.literal_eval(data)
    except:
        return []

def readAktuelFromJSON(filename,aktuel):
    localAktuel = []
    with open('{}.txt'.format(filename), encoding='utf-8') as f:
        data = f.readline()
    for i in ast.literal_eval(data):
        if i['magaza'] == aktuel:
            localAktuel.append(i)
    return localAktuel

def getPdfTitle(filename):
    with open(filename, 'rb') as f: #http://www.blog.pythonlibrary.org/2018/04/10/extracting-pdf-metadata-and-text-with-python/
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        pdf.getNumPages()
##    author = info.author
##    creator = info.creator
##    producer = info.producer
##    subject = info.subject
    title = info.title
    return title.strip()

def downloadPdf(url):
    parse = urlparse(url)
    base_url = parse.scheme + '://' + parse.netloc
    try:
        redirect = requests.get(url, allow_redirects=False)
    except Exception as e:
        return None
    if redirect.status_code == 302:
        url = base_url + redirect.headers['location']
    else: 
        pass
    filename = url.split('/')[-1]
    
    if filename[-4:] != '.pdf':
        return None
    else:
        pass
    if os.path.isfile(filename):
        return filename.strip()
    else:
        print(filename,'downloading')
        request = requests.get(url)
        with open(filename, 'wb') as f: #https://stackoverflow.com/questions/34503412/download-and-save-pdf-file-with-python-requests-module
            f.write(request.content)
        clear()
        return filename.strip()

def girdiDuzenleyici(silinecekler):
    silinecekler = sorted(set(''.join(silinecekler.split()).split(',')))
    for a in silinecekler:
        if not a:
            silinecekler.remove(a)
            
    return silinecekler

def girdiKontrol(silinecekler, limitEkle, limitSil):
    try:
        if not silinecekler:
##            print(False)
            return False
        for sayi in silinecekler:
            if sayi == '#':
                return True
            elif sayi[0] == ':':
                if not sayi[1:].isnumeric() or not int(sayi[1:]) >= 0 or not int(sayi[1:]) <= limitSil or not limitSil != 0:
##                    print(sayi,False)
                    return False
            elif not sayi.isnumeric() or not int(sayi) >= 0 or not int(sayi) <= limitEkle or not limitEkle != 0:
##                print(sayi,False)
                return False
            else:
                pass
##        print(True)
        return True
    except Exception as e:
##        print(e,False)
        return False

def girdiIslemleri(silinecekler,summary,news,olds):
    summary_new = summary.copy()
    
    for silinecek in silinecekler:
        if silinecek == '#':
            return summary
        elif silinecek == ':0':
            for aktuel in summary:
                if aktuel['durum']=='old':
                    summary_new.remove(aktuel)
                else:
                    pass
            break
        elif silinecek[0] == ':':
            for aktuel in summary:
                if aktuel == olds[int(silinecek[1:])-1]:
                    summary_new.remove(aktuel)
                else:
                    pass
                
    for silinecek in silinecekler:     
        if silinecek == '0':
            for aktuel in summary_new:
                if aktuel['durum']=='new':
                    aktuel['durum'] = 'active'
                else:
                    pass
            break
        elif silinecek[0] != ':':
            for aktuel in summary_new:
                if aktuel == news[int(silinecek)-1]:
                    aktuel['durum'] = 'active'
                else:
                    pass
    return summary_new

def getBimAktuel():
    global local_file
    global aktuel_cekim_hatasi
    url = 'https://www.bim.com.tr/default.aspx'
    json_list = []
    try:
        page = requests.get(url, timeout=10)
##        json_list + False
    except Exception as e:
        aktuel_cekim_hatasi = True
        print('BİM aktüel kontrolü basarisiz!')
        return readAktuelFromJSON(local_file,'BİM')
    
    soup = BeautifulSoup(page.content,"lxml")
    currentAktuel = BeautifulSoup(str(soup.select('div.subButtonArea.active')),"lxml") #https://stackoverflow.com/a/40305745
    for brosur in currentAktuel.find_all('a','subButton'):
        json_data = {'magaza':'BİM','aktuel':"",'durum':'','tarih':''}
        json_data['aktuel'] = brosur.text.strip() + ' ' + brosur['href'].split('_')[-1]
        json_data['durum'] = 'new'
        json_data['tarih'] = str(datetime.datetime.now())
        json_list.append(json_data)
        
    futureAktuel = BeautifulSoup(str(soup.select('div.subButtonArea-5')),"lxml")
    for brosur in futureAktuel.find_all('a','subButton'): 
        json_data = {'magaza':'BİM','aktuel':"",'durum':'','tarih':''}
        json_data['aktuel'] = brosur.text.strip() + ' ' + brosur['href'].split('_')[-1]
        json_data['durum'] = 'new'
        json_data['tarih'] = str(datetime.datetime.now())
        json_list.append(json_data)
    return json_list

def getA101Aktuel():
    global local_file
    global aktuel_cekim_hatasi
    url = 'https://www.a101.com.tr/afisler'
    json_list = []
    try:
        page = requests.get(url, timeout=10)
##        json_list + False
    except Exception as e:
        aktuel_cekim_hatasi = True
        print('A101 aktüel kontrolü basarisiz!')
        return readAktuelFromJSON(local_file,'A101')

    soup = BeautifulSoup(page.content,"lxml")
    brosurler = soup.find("div","brochures-list").find("ul", recursive=False)
    for brosur in brosurler.find_all("li", recursive=False):
        json_data = {'magaza':'A101','aktuel':"",'durum':'','tarih':''}
        json_data['aktuel'] = brosur.find("span").text #+ ' ' + brosur.a['href']
        json_data['durum'] = 'new'
        json_data['tarih'] = str(datetime.datetime.now())
        json_list.append(json_data)
    return json_list

def getSokAktuel():
    global local_file
    global aktuel_cekim_hatasi
    url = 'https://kurumsal.sokmarket.com.tr'
    link_list = []
    json_list = []
    try:
        page = requests.get(url, timeout=10)
##        json_list + False
    except Exception as e:
        aktuel_cekim_hatasi = True
        print('ŞOK aktüel kontrolü basarisiz!')
        return readAktuelFromJSON(local_file,'ŞOK')
    
    tree = html.fromstring(page.content)
    
    aktuelHaftaici = url + tree.xpath('//html/body/div[1]/div[3]/div[1]/div[2]/p/a/@href')[0]
    aktuelHaftasonu = url + tree.xpath('//html/body/div[1]/div[3]/div[3]/div[2]/p/a/@href')[0]
    link_list.append(aktuelHaftaici)
    link_list.append(aktuelHaftasonu)

    for link in link_list:
        filename = downloadPdf(link)
        if filename is not None:
            json_data = {'magaza':'ŞOK','aktuel':"",'durum':'','tarih':''}
            json_data['aktuel'] = getPdfTitle(filename)
            json_data['durum'] = 'new'
            json_data['tarih'] = str(datetime.datetime.now())
            json_list.append(json_data)
        else: pass
    return json_list

def getAktuels():
    bim_aktuel = getBimAktuel()
    a101_aktuel = getA101Aktuel()
    sok_aktuel = getSokAktuel()
    return bim_aktuel + a101_aktuel + sok_aktuel
    
def compareAktuels(local_aktuels,online_aktuels):
    for aktuel in local_aktuels:
        if not any(aktuel['magaza'] == a['magaza'] and aktuel['aktuel'] == a['aktuel'] for a in online_aktuels) and aktuel['durum'] != 'new':
            aktuel['durum'] = 'old'
            online_aktuels.append(aktuel)
        else:
            pass
    for aktuel in online_aktuels:
        if not any(aktuel['magaza'] == a['magaza'] and aktuel['aktuel'] == a['aktuel'] for a in local_aktuels):
            aktuel['durum'] = 'new'

    for aktuelOnline in online_aktuels:
        for aktuelLocal in local_aktuels:
            if aktuelOnline['magaza'] == aktuelLocal['magaza'] and aktuelOnline['aktuel'] == aktuelLocal['aktuel']:
                aktuelOnline['durum'] = aktuelLocal['durum']
                if aktuelLocal.get('tarih'):
                    aktuelOnline['tarih'] = aktuelLocal['tarih']
                break

##    for i in online_aktuels:
##        print('\n',i)

    return online_aktuels

def showSummary(summary):
    global aktuel_cekim_hatasi
    sayac = 1
    olds = []
    news = []
    silinecekler = []
    summary = sorted(summary, key=lambda k: k['tarih'], reverse=False)
    summary = sorted(summary, key=lambda k: k['magaza'], reverse=False)
    if aktuel_cekim_hatasi:
        print('')

    print("Yayindaki aktüeller:")
    for aktuel in summary:
        if(aktuel['durum'] == 'active' or aktuel['durum'] == 'old'):
            print(aktuel['magaza'],aktuel['aktuel'])
        else:
            pass
    print('')
    
    if any(a['durum'] == 'old' or a['durum'] == 'new' for a in summary):
        if any(a['durum'] == 'old' for a in summary):
            print("Biten aktüeller:")
            for aktuel in summary:
                if(aktuel['durum'] == 'old'):
                    olds.append(aktuel)
                    print(str(sayac)+'.',aktuel['magaza'],aktuel['aktuel'])
                    sayac += 1
                else:
                    pass
            print("* Kaldirilanlarin ':' ve ID'sini girin. (Hepsini kaldirmak icin :0 girin)\n")
        sayac = 1
        if any(a['durum'] == 'new' for a in summary):
            print("Yeni aktüeller:")
            for aktuel in summary:
                if(aktuel['durum'] == 'new'):
                    news.append(aktuel)
                    print(str(sayac)+'.',aktuel['magaza'],aktuel['aktuel'])
                    sayac += 1
                else:
                    pass
            print("* Eklenenlerin ID'sini girin. (Hepsini eklemek icin 0 girin)\n")
        print("* Her bir komutu ',' ile ayirin. (Sadece tarihleri kaydetmek icin '#' girin)\n")
        while(not girdiKontrol(silinecekler,len(news),len(olds))):
            silinecekler = input("Komut satiri: ")
            silinecekler = girdiDuzenleyici(silinecekler)
##            print(silinecekler)
        summary = girdiIslemleri(silinecekler,summary,news,olds)
        return summary
    else:
        print('Yeni aktüel yok.')
        return False

def main():
    global local_file
    local_file = 'aktuels'
    local_aktuels = readAktuelsFromJSON(local_file)
    online_aktuels = getAktuels()
    summary = compareAktuels(local_aktuels,online_aktuels)
    results = showSummary(summary)

    if results:
        ydk_filename = local_file+".txt.{}".format(datetime.datetime.now().strftime("%Y%m%d%H%M"))
        if os.path.isfile(local_file+".txt"):
            if os.path.isfile(ydk_filename):
                os.remove(ydk_filename)
                os.rename(local_file+".txt",ydk_filename)
            else:
                os.rename(local_file+".txt",ydk_filename)
        createAktuelJSONFile(local_file,results)
    else:
        input()

def clear(): #https://stackoverflow.com/a/4810595
    if os.name =='posix':
        os.system('clear')
    else:
        os.system('cls')
    
if __name__ == "__main__":
    while True:
        main()
        clear()
