import sqlite3
import time

import requests
from bs4 import BeautifulSoup


def to_db(cursor, con, links: list):
    for item in links:
        link = item[0]
        price = item[1]
        query = f'INSERT INTO test (link, price) VALUES ("{link}", "{price}")'
        cursor.execute(query)
    con.commit()


def update_db(links, cur):
    for item in links:
        link = item[0]
        price = item[1]
        query = f'UPDATE test SET price = "{price}" WHERE link = "{link}"'
        print(query)
        cur.execute(query)



def parse_links(url):
    links = []
    cookie = {
        'timezoneOffset': '10800,0',
        'teamMachineAuth76561198314351317': 'A455996711052F061FC5B355D06CE0608EBCA1FE',
        'steamCurrencyId': '5',
        'browserid': '2414494782528880041',
        'strInventoryLastContext': '730_2',
        'sessionid': 'dc62347f57a28d3fdbd84ab5',
        'recentlyVisitedAppHubs': '431960%2C570%2C1563180%2C730%2C331470',
        'CONSENT': 'YES+',
        'Steam_Language': 'english',
        'steamMachineAuth76561198187797831': '5D344C3FE3146E5DBCEDBA4EAD2862D97EC806D3',
        'steamCountry': 'RU%7C25b97fde74b857ff83332f021335727b',
        'steamLoginSecure': '76561198187797831%7C%7C7723F4CAE08FEE8FCB3A2DF6CDB57065AC8174DB',
        'steamRememberLogin': '76561198187797831%7C%7C75b393f03a167562c26e489962c25de6',
        'webTradeEligibility': '%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C%22steamguard_required_days%22%3A15%'
                               '2C%22new_device_cooldown_days%22%3A7%2C%22time_checked%22%3A1646486303%7D'}
    response = requests.get(url, cookies=cookie)
    print(response)
    # while response != '<Response [200]>':
    #     time.sleep(5)
    #     response = requests.get(url, cookies=cookie)
    soup = BeautifulSoup(response.json()['results_html'], 'lxml')
    links_row = soup.find_all('a', class_='market_listing_row_link')
    for link in links_row:
        price = float(link.find('span', class_='normal_price').find(class_="normal_price").get('data-price'))/100
        links.append((link['href'], price))

    return links


def main():
    db = sqlite3.connect('CS.db')
    cur = db.cursor()
    for page in range(1, 180):
        print('Страница: ', page)
        url = f'https://steamcommunity.com/market/search/render/?query=&start={page * 100}&count=100&appid=730'
        print(url)
        links = parse_links(url)
        # to_db(cur, db, links)
        update_db(links, cur)
        db.commit()
        time.sleep(1)


if __name__ == "__main__":
    main()
