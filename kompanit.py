import requests
import os
import re
from bs4 import BeautifulSoup
import time
import xlsxwriter

FOLDER = 'Kompanit'
DOMAIN = 'https://kompanit.com.ua/'

start_time = time.time()


def main():
    check_path = os.path.exists(FOLDER)
    if not check_path:
        os.mkdir(FOLDER)
        print(f'### Folder "{FOLDER}" create. Starting the download')
    else:
        print(f'### Folder "{FOLDER}" already exists. Starting the Download')

    data = get_categories_url()
    exel_data = []
    for category in data:
        data_category = get_single_category_data(category['cat_url'], category['cat_name'])
        exel_data.append({
            'sheet_name': category['cat_name'],
            'sheet_data': data_category
        })

    write_exel(exel_data)

    end_time = time.time() - start_time
    print('### Files downloaded. Time: ' + str(end_time) + 'seconds')
    input("### Press \"Enter\" to exit")


def get_content(url):
    raw_content = requests.get(url)
    soup = BeautifulSoup(raw_content.text, 'html.parser')
    return soup


def get_categories_url():
    data = [{
        'cat_url': 'https://kompanit.com.ua/catalog/tryumo/c23',
        'cat_name': 'Трюмо'
    }]
    return data

# def get_categories_url():
#     soup = get_content('https://kompanit.com.ua/catalog')
#     blocks = soup.find_all('a', class_='category__block')
#     data = []
#     for block in blocks:
#         category_url = block.get('href')
#         category_name = block.find('span', class_='category__title').get_text(strip=True)
#         cat_name = category_name.replace('/', '_')
#         name = cat_name.replace('"', '_')
#         data.append({
#             'cat_url': category_url,
#             'cat_name': name
#         })
#     return data


def get_single_category_data(cat_url, cat_name):
    soup = get_content(cat_url)
    check_path = os.path.exists(FOLDER + '/' + cat_name)
    if not check_path:
        os.mkdir(FOLDER + '/' + cat_name)

    blocks = soup.find_all('a', class_='product__name')
    increment2 = 0
    data_advert = []
    for block in blocks:
        increment2 += 1
        advert_url = block.get('href')
        advert_name = block.get_text(strip=True)

        adv_name = advert_name.replace('/', '-')
        name = adv_name.replace('"', '-')

        # get_advert(advert_url, name, cat_name)

        description, color_list = get_advert(advert_url, name, cat_name, increment2)
        data_advert.append(
            {
                'number': increment2,
                'name': advert_name,
                'description': description,
                'color_list': color_list
            }
        )

    # write_exel(data_advert)

    next_page = get_next_page(soup)
    if next_page:
        next = DOMAIN + next_page
        get_single_category_data(next, cat_name)

    return data_advert


def get_advert(advert_url, advert_name, category_name, increment2):
    saved_images = []
    path = FOLDER + '/' + category_name + '/' + str(increment2)
    check_path = os.path.exists(path)
    if not check_path:
        print('### Downloaded: ' + advert_name)
        os.makedirs(path)
    else:
        print('### Folder already exists: ' + path)
    soup = get_content(advert_url)
    advert_img = soup.find_all('meta', property='og:image')
    advert_img2 = soup.find_all('img', class_='js-lazyload slider__slide-img')
    descriptions = soup.find_all('li', class_='item-characteristics__item')
    descriptions2 = soup.find_all('div', class_='item-descr js-static')
    colors = soup.find_all('span', class_='item-colors__name')
    description = ''
    color_list = ''

    for color in colors:
        color_list += color.get_text(strip=True)
        color_list += ','

    for descr in descriptions:
        # description += descr.get_text(strip=True)
        d1 = descr.find('span', class_='item-characteristics__name').get_text(strip=True)
        d2 = descr.find('span', class_='item-characteristics__value').get_text(strip=True)
        description += f'{d1} {d2} '

    for descr2 in descriptions2:
        description += descr2.get_text(strip=True)

    increment = 0
    if advert_img:
        for advert in advert_img:
            image = advert.get('content')
            if image:
                if image not in saved_images:
                    increment += 1
                    saved_images.append(image)
                    download_image(image, path, increment)

    if advert_img2:
        for advert in advert_img2:
            image = advert.get('data-zzload-source-img')
            if image:
                if image not in saved_images:
                    increment += 1
                    saved_images.append(image)
                    download_image(image, path, increment)

    return description, color_list


def get_next_page(soup):
    pagination = soup.find('a', class_='pagination__arrow pagination__arrow--next')
    if pagination:
        pag = pagination.find('a')
        if pag:
            next_page = pag.get('href')
            return next_page
        else:
            return False


def download_image(image, path, increment):
    full_url = image
    # name = re.findall(r'big/(\w+).(?:JPEG|jpg)', image)
    check_img = os.path.isfile(path + '/' + str(increment))
    if not check_img:
        p = requests.get(full_url)
        out = open(path + '/' + str(increment), "wb")
        print('Image downloaded: ' + str(increment))
        # else:
        #     second = time.time() - start_time
        #     name = str(second)
        #     out = open(path + '/' + str(increment) + '_' + name.replace('.', '') + '.jpg', "wb")
        #     print('Image downloaded: ' + name)

        out.write(p.content)
        out.close()


def write_exel(write_exel):
    workbook = xlsxwriter.Workbook(FOLDER + '/' + 'kompanit.xlsx')
    print('### Write in exel file')
    for exel in write_exel:
        worksheet = workbook.add_worksheet(exel['sheet_name'])
        for data in exel['sheet_data']:
            worksheet.write('A' + str(data['number']), data['number'])
            worksheet.write('B' + str(data['number']), data['name'])
            worksheet.write('C' + str(data['number']), data['description'])
            worksheet.write('D' + str(data['number']), data['color_list'])

    workbook.close()


main()
