import random
import sqlite3
import time
from http.cookies import SimpleCookie
from os import path
from urllib.parse import unquote

import src.steam_price as steam_price
import requests


def get_items_from_db():
    types_deny = ['%Graffiti%', '%Souvenir%', '%Pin%', '%Music Kit%', '%Case%', '%Sticker%', '%Capsule%',
                  '%UMP-45%', '%Nova%', '%Sawed-Off%', '%PP-Bizon%', '%XM1014%', '%G3SG1%', '%Negev%',
                  '%R8 Revolver%', '%MAG-7%', '%SCAR-20%', '%P2000%']
    types = ("%Gloves%", "%Wraps%", "%Knife%", "%Karambit%", "%Daggers%", "%Bayonet%")
    path_to_db = path.join(path.curdir, 'src', 'db') + path.sep
    db = sqlite3.connect(path_to_db + 'CS.db')
    cur = db.cursor()
    NOT_LIKE = ''
    LIKE = ''
    for _type in types_deny[1::]:
        LIKE += f' OR market_hash_name LIKE "{_type}"'
        NOT_LIKE += f' AND market_hash_name NOT LIKE "{_type}"'
    query = f'SELECT * FROM items WHERE market_hash_name NOT LIKE "{types[0]}"' + NOT_LIKE
    print(query)
    result = cur.execute(query).fetchall()
    return result


def get_steam_prices(id):
    """ Получаем первые две позиции по покупке и продаже"""
    url = 'https://steamcommunity.com/market/itemordershistogram?'
    headers = {
           'Referer': 'https://steamcommunity.com/market/listings/730/',
           'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         'like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.3.818 Yowser/2.5 Safari/537.36 '
    }
    params = {
        'country': 'RU',
        'language': 'english',
        'currency': 5,
        'item_nameid': id,
        'two_factor': 0
    }
    response = requests.get(url, cookies=cookies, params=params, headers=headers)

    print(response)
    print(response.url)


def main():
    items = get_items_from_db()
    ids = [29209299, 175880270, 175880431, 175880463, 175880616, 175880573, 175880718, 175881162, 176042758, 176000161,
           176000862, 29299516, 1322114, 49419352, 49440514, 49450572, 49473128, 156229248, 156280276, 156309805,
           156425941, 156239400, 156468937, 156510397, 139718952, 139705916, 139813604, 139833934, 139873671, 50767308,
           49359126, 1689336, 1321692, 1284092, 1321999, 1322316, 1322763, 1340259, 1339428, 1338682, 1338145, 1338270,
           8997357, 8996299, 8996328, 9750600, 8993610, 8994376, 15017866, 14971874, 14974565, 14977508, 14977515,
           29235703, 29285556, 29240573, 29219908, 29222871, 29215137, 29217385, 176000012, 176000025, 176000026,
           176000046, 176000110, 176000130, 176000147, 176000275, 176000265, 176000267, 176000157, 176000190,
           176000191, 176000213, 176005151, 176000579, 176003586, 176001452, 176001595, 176000417, 176000323,
           176000342, 176000612, 176000857, 176000665, 176001375, 175880704, 175880715, 175880741, 175880775,
           175880833, 175880901, 175880577, 175880618, 175885803, 175887151, 175880994, 175881573, 14962991, 14963011,
           14963026, 14963006, 14971875, 14980588, 14983802, 14983805, 14986884, 14990005, 15008083, 15013481, 15128585,
           29405424, 29528365, 14969263, 14971872, 14966469, 14966462, 15022989, 16294128, 9007040, 9007437, 9008179,
           9015838, 9019039, 9028234, 9646079, 9673239, 9692723, 10367491, 10451702, 15015911, 8991197, 8991009,
           8993300, 8993322, 8994355, 8997213, 8989628, 5659611, 1284327, 1330984, 1331370, 1332562, 1334343, 1338031,
           1338620, 1339378, 1340919, 1358786, 1377668, 1322108, 1322123, 1321782, 1322141, 1322173, 1322178, 1322431,
           1322526, 1397881, 1400220, 1413870, 175880738, 175880879, 175880714, 175880672, 175891607, 175880992,
           175881105, 175881128, 175881188, 175881277, 175881983, 175882536, 175882701, 175884886, 175880448, 175880559,
           175880563, 175880572, 175880582, 139673187, 139833936, 142239595, 139705926, 139748201, 139778814, 139691724,
           156249199, 156249201, 156259492, 156300545, 156338220, 156516172, 156522363, 156535454, 157954575, 160052991,
           45409215, 156249197, 176000215, 176042745, 29222872, 175880622, 29213035, 49419393, 176042792, 175880465,
           176042805, 156549575, 139673203, 176000491, 49539759, 176092044, 176042756, 176042722, 156290239, 176042701,
           29682414, 1322656, 176000283, 175884373, 176000268, 176091969, 176000385, 176000144, 176097619, 9030353,
           176000474, 9003689, 49430982, 175881419, 1340661, 176000312, 176097086, 176097574, 176042908, 176000083,
           8996330, 1321689, 175881842, 176000016, 176000180, 176045218, 176000804, 176097065, 176097580, 176092002,
           49399550, 176043514, 156209808, 139748202, 1322593, 49419378, 1341753, 49419358, 176000152, 9019050,
           176000651, 175885751, 1322590, 176000679, 9678638, 9001896, 1341752, 176097534, 176097868, 176091992,
           176097664, 1322638, 1332955, 176000934, 176042836, 176097714, 176000346, 176097665, 176097750, 139705925,
           176097478, 176000436, 176043383, 176000042, 9678738, 176097642, 139854430, 139705922, 139778815, 14983801,
           1322109, 176092170, 175880684, 29523663, 176002684, 29299519, 175880920, 1348285, 176000616, 176043505,
           30704363, 175888200, 176043613, 15026899, 49440519, 1333843, 176092075, 29842592, 176097515, 176097570,
           176043328, 176097782, 176043273, 1337945, 14974570, 175882514, 49576395, 175880554, 15069272, 176000424,
           176096927, 176044224, 176043109, 176042855, 176000429, 176000613, 176000482, 176002004, 176000384, 176000099,
           176000753, 175881185, 156280279, 9751897, 1342074, 156280283, 176097723, 176096910, 9767634, 176000357,
           1322729, 176097475, 175891068, 176043722, 139778812, 9672668, 176000175, 139673208, 29425788, 156200221,
           176097558, 176097529, 176097682, 176097169, 176092012, 176091970, 176043390, 176000743, 175882692, 175880923,
           156209811, 29658103, 49710347, 9052489, 1546178, 1322120, 176000153, 176091940, 176097555, 176000467,
           156140154, 9644596]
    for id in range(len(ids)):
        random1 = random.randint(0, len(ids))
        # random2 = random.randint(0, len(items))
        name = unquote(items[random1][1].split('/')[6])
        # id = items.pop(random1)[2]
        id = ids.pop(random1)
        print(name, id)
        buy, _, sell, _ = steam_price.get_steam_prices(items[random1][2], cookies)
        time.sleep(2)
        history = steam_price.get_price_history(name, cookies)

        print(f"Buy: {buy} \n Sell: {sell}")
        # print(history[0:5])


if __name__ == "__main__":
    raw_cookie = 'ActListPageSize=10; timezoneOffset=10800,0; Steam_Language=english; browserid=2610424829677284198; steamCurrencyId=5; recentlyVisitedAppHubs=1421250; steamLoginSecure=76561198187797831%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEMwOF8yMTc4RDZBMF9GQkZGNiIsICJzdWIiOiAiNzY1NjExOTgxODc3OTc4MzEiLCAiYXVkIjogWyAid2ViIiBdLCAiZXhwIjogMTY3MjI0Mzk5MCwgIm5iZiI6IDE2NjM1MTY4NzAsICJpYXQiOiAxNjcyMTU2ODcwLCAianRpIjogIjBDRDVfMjFENDM4MThfRDRGODgiLCAib2F0IjogMTY2NjU1MDA5MSwgInJ0X2V4cCI6IDE2ODQ3NzQ1NTMsICJwZXIiOiAwLCAiaXBfc3ViamVjdCI6ICI1LjEwMS4yMi4xNzMiLCAiaXBfY29uZmlybWVyIjogIjUuMTAxLjIyLjE3MyIgfQ.80Z6DxKaVp-i9eqgl9pbSgPFaaKDZYNXvwwZ8QocWcF_8mqUZ4UNPStyNOABExmt5N3RZulzkOlOW0zgHatJBA; strInventoryLastContext=753_6; sessionid=69fdcf5a56df6ceb1cb8bb83; webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22%3A1672213930%7D; tsTradeOffersLastRead=1671517866'
    cookie = SimpleCookie()
    cookie.load(raw_cookie)
    cookies = {k: v.value for k, v in cookie.items()}
    main()
