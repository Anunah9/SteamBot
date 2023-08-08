import random
import sqlite3
import time

import requests

cookie = header_search = {
    'ActListPageSize': '100',
    'timezoneOffset': '10800,0',
    'teamMachineAuth76561198314351317': 'A455996711052F061FC5B355D06CE0608EBCA1FE',
    'extproviders_730': 'marketcsgocom,steam',
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
                           '2C%22new_device_cooldown_days%22%3A7%2C%22time_checked%22%3A1646486303%7D'
}

proxies = dict(http='socks5://user:pass@51.79.52.80:3080',
               https='socks5://user:pass@51.79.52.80:3080')


def get_empty_strings():
    return cur.execute('SELECT link FROM test WHERE itemnameid is Null').fetchall()


def get_itemNameId_market_hash_name(_link):
    response = requests.get(_link, cookies=cookie)
    response_for_content = str(response.content, 'UTF-8')
    _item_name_id = str(response_for_content[response_for_content.find("Market_LoadOrderSpread") +
                                             len("Market_LoadOrderSpread"):].split()[1])
    print(_item_name_id)
    _item_name = str(response_for_content[response_for_content.find("market_listing_item_name") +
                                          len("market_listing_item_name"):].split('>')[2].split('<')[0])
    print(_item_name)
    return _item_name, _item_name_id


def to_db(_market_hash_name, _link, _itemnameid):
    cur.execute('UPDATE test SET market_hash_name= "{}", itemnameid = {} WHERE link = "{}"'.format(_market_hash_name,
                                                                                                   _itemnameid, _link))


if __name__ == "__main__":
    con_CS = sqlite3.connect('CS.db')
    cur = con_CS.cursor()
    empty_strings_links = get_empty_strings()
    k = 1
    for link in empty_strings_links:
        print("Предмет {} из {}".format(k, len(empty_strings_links)))
        k += 1
        item_name, item_name_id = get_itemNameId_market_hash_name(link[0])
        to_db(item_name, link[0], item_name_id)
        delay = random.random()
        time.sleep(delay + 1)
        con_CS.commit()
