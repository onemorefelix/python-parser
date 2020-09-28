import requests
import os
import re
from bs4 import BeautifulSoup
import time

FOLDER = 'SvitMebliv'
URL = 'https://www.svit-mebliv.ua/catalog'
DOMAIN = 'https://www.svit-mebliv.ua'

start_time = time.time()


def main():
    check_path = os.path.exists(FOLDER)
    if not check_path:
        os.mkdir(FOLDER)
        print('Folder "DOWNLOAD" create. Starting the download')
    else:
        print('Folder already exists. Starting the Download')

    data = get_categories_url()
    for category in data:
        get_single_category_data(category['cat_url'], category['cat_name'])

    end_time = time.time() - start_time
    print('Files downloaded. Time: ' + str(end_time) + 'seconds')
    input("Press \"Enter\" to exit")


def get_content(url):
    raw_content = requests.get(url)
    soup = BeautifulSoup(raw_content.text, 'html.parser')
    return soup


def get_categories_url():
    soup = get_content(URL)
    blocks = soup.find_all('a', class_='section__title-tertiary')
    data = []
    for block in blocks:
        data.append(
            {
                'cat_url': DOMAIN + block.get('href'),
                'cat_name': block.get_text(strip=True)
            }
        )
    return data


def get_single_category_data(cat_url, cat_name):
    soup = get_content(cat_url)
    check_path = os.path.exists(FOLDER + '/' + cat_name)
    if not check_path:
        os.mkdir(FOLDER + '/' + cat_name)

    blocks = soup.find_all('a', class_='bedroom-sets-block-img__title')
    for block in blocks:
        advert_url = DOMAIN + block.get('href')
        advert_name = block.get_text(strip=True)
        name = advert_name.replace('"', '_')
        get_advert(advert_url, name, cat_name)

    next_page = get_next_page(soup)
    if next_page:
        next = DOMAIN + next_page
        get_single_category_data(next, cat_name)


def get_advert(advert_url, advert_name, category_name):
    path = FOLDER + '/' + category_name + '/' + advert_name
    check_path = os.path.exists(path)
    if not check_path:
        print('Downloaded: ' + advert_name)
        os.mkdir(FOLDER + '/' + category_name + '/' + advert_name)
    else:
        print('Folder already exists: ' + advert_name)
    soup = get_content(advert_url)
    advert_img = soup.find_all('div', class_='product-card-slider-bottom__img')

    if advert_img:
        for advert in advert_img:
            image = advert.find('img').get('src')
            download_image(image, path)
    else:
        image = soup.find('div', class_='product-card-slider-top__img').find('img').get('src')
        download_image(image, path)


def get_next_page(soup):
    pagination = soup.find('li', string="Вперед")
    if pagination:
        pag = pagination.find('a')
        if pag:
            next_page = pag.get('href')
            return next_page
        else:
            return False


def download_image(image, path):
    full_url = DOMAIN + image
    name = re.findall(r'product/.+/(\w+.\w+)', image)
    check_img = os.path.isfile(path + '/' + name[0])
    if not check_img:
        p = requests.get(full_url)
        if name:
            out = open(path + '/' + name[0], "wb")
            print('Image downloaded: ' + name[0])
        else:
            second = time.time() - start_time
            name = str(second)
            out = open(path + '/' + name.replace('.', '') + '.jpg', "wb")
            print('Image downloaded: ' + name)

        out.write(p.content)
        out.close()


main()
