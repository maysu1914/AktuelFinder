import os
from urllib.parse import urlparse

import requests
from PyPDF2 import PdfFileReader


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

    if not is_pdf(filename):
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


def is_pdf(filename):
    if filename[-4:] != '.pdf':
        return False
    else:
        return True


def get_pdf_title(filename):
    # http://www.blog.pythonlibrary.org/2018/04/10/extracting-pdf-metadata-and-text-with-python/
    with open(filename, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        pdf.getNumPages()
    title = info.title if info.title else filename
    return title.strip()
