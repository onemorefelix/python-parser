import requests
from bs4 import BeautifulSoup

url = 'http://mebli-site/login'

r = requests.get(url) #url is create form
soup = BeautifulSoup(r.text, 'html.parser')
for link in soup.find_all('input'):
    token = link.get('value')

    jar = requests.cookies.RequestsCookieJar()
    jar.set('XSRF-TOKEN', r.cookies['XSRF-TOKEN'])

    url_post = "http://mebli-site/login"
    data = {
        "_token": token,
        "email": "onemorefelix@gmail.com",
        "password": "super9gjQ3",

    }

    login_request = requests.post(url_post, data=data, cookies=jar)
    print(login_request)