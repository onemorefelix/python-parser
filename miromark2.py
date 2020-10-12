import requests
import os
import re
from bs4 import BeautifulSoup
import time
import xlsxwriter

FOLDER = 'D:/DOWN/MiroMark'
DOMAIN = 'http://miromark.com.ua/'

start_time = time.time()
#rr

def main():
    check_path = os.path.exists(FOLDER)
    if not check_path:
        os.makedirs(FOLDER)
        print('### Folder "MiroMark" create. Starting the download')
    else:
        print('### Folder already exists. Starting the Download')

    data = get_categories_url()
    for category in data:
        get_single_category_data(category['cat_url'], category['cat_name'])

    end_time = time.time() - start_time
    print('### Files downloaded. Time: ' + str(end_time) + 'seconds')


def get_content(url):
    raw_content = requests.get(url)
    soup = BeautifulSoup(raw_content.text, 'html.parser')
    return soup


def get_categories_url():
    data = [{
        'cat_url': 'http://miromark.com.ua/ua/catalog/bedroom/',
        'cat_name': 'Спальні'
    }
        #     , {
        #     'cat_url': 'http://miromark.com.ua/ua/catalog/living-room/',
        #     'cat_name': 'Вітальні'
        # }, {
        #     'cat_url': 'http://miromark.com.ua/ua/catalog/kitchens/',
        #     'cat_name': 'Кухні'
        # }
    ]
    return data


def get_single_category_data(cat_url, cat_name):
    soup = get_content(cat_url)
    check_path = os.path.exists(FOLDER + '/' + cat_name)
    if not check_path:
        os.makedirs(FOLDER + '/' + cat_name)

    blocks = soup.find_all('a', class_='uk-transition-toggle link-news')
    increment2 = 0
    data_advert = []
    for block in blocks:
        increment2 += 1
        advert_url = block.get('href')
        advert_name = block.find('div', class_='link-news-content').get_text(separator=u' ')

        adv_name = advert_name.replace('/', '_')
        name = adv_name.replace('"', '_')

        description = get_advert(advert_url, name, cat_name, increment2)
        data_advert.append(
            {
                'number': increment2,
                'name': name,
                'description': description
            }
        )

    write_exel(data_advert)


def get_advert(advert_url, advert_name, category_name, increment2):
    path = FOLDER + '/' + category_name + '/' + str(increment2)
    check_path = os.path.exists(path)
    if not check_path:
        print('### Downloaded: ' + advert_name)
        os.makedirs(path)
    else:
        print('### Folder already exists: ' + path)
    soup = get_content(advert_url)
    advert_img = soup.find_all('div', class_='uk-transition-toggle element-link')
    advert_img2 = soup.find_all('a', class_='uk-inline-clip uk-transition-toggle')
    descriptions = soup.find_all('div', class_='shop-grid')
    description = ''

    for descr in descriptions:
        description += descr.get_text(strip=True)

    increment = 0
    if advert_img:
        for advert in advert_img:
            increment += 1
            image = advert.find('a').get('href')
            if image:
                download_image(image, path, increment)
    else:
        image = soup.find('div', class_='product-card-slider-top__img').find('img').get('src')
        download_image(image, path, increment)

    if advert_img2:
        for advert in advert_img2:
            increment += 1
            image = advert.get('href')
            if image:
                download_image(image, path, increment)
    return description


def get_next_page(soup):
    pagination = soup.find('li', string="Вперед")
    if pagination:
        pag = pagination.find('a')
        if pag:
            next_page = pag.get('href')
            return next_page
        else:
            return False


def download_image(image, path, increment):
    full_url = image
    name = re.findall(r'files_ci/\d+/(\S+\.\w+)', image)
    if name:
        check_img = os.path.isfile(path + '/' + str(increment) + '_' + name[0])
        if not check_img:
            p = requests.get(full_url)
            if name:
                out = open(path + '/' + str(increment) + '_' + name[0], "wb")
                print('Image downloaded: ' + str(increment) + '_' + name[0])
            else:
                second = time.time() - start_time
                name = str(second)
                out = open(path + '/' + str(increment) + '_' + name.replace('.', '') + '.jpg', "wb")
                print('Image downloaded: ' + name)

            out.write(p.content)
            out.close()


def write_exel(data_advert):
    workbook = xlsxwriter.Workbook(FOLDER + '/' + 'miromark.xlsx')
    worksheet = workbook.add_worksheet()
    print('### writed exel file')
    for data in data_advert:
        worksheet.write('A' + str(data['number']), data['number'])
        worksheet.write('B' + str(data['number']), data['name'])
        worksheet.write('C' + str(data['number']), data['description'])

    workbook.close()


main()
