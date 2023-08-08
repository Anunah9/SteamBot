import random
import sqlite3
import time
import traceback
from os import path
import telebot
import src.steam_price as steam_price
from http.cookies import SimpleCookie
from urllib.parse import unquote
import Database


def get_items_from_db():
    types_deny = ['%Graffiti%', '%Souvenir%', '%Pin%', '%Music Kit%', '%Case%', '%Sticker%', '%Capsule%',
                  '%UMP-45%', '%Nova%', '%Sawed-Off%', '%PP-Bizon%', '%XM1014%', '%G3SG1%', '%Negev%',
                  '%R8 Revolver%', '%MAG-7%', '%SCAR-20%', '%P2000%', '%Patch%', '%Sealed%']
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


def find_price_on_tm(market_hash_name, min_limit_price, max_limit_price):

    tm_price = db_TM.get_min_price(market_hash_name)
    if not tm_price:
        return True
    tm_price = tm_price[0] / 100
    if tm_price < min_limit_price or tm_price > max_limit_price:
        return False
    else:
        return True


def filter_items_by_price(_items):
    print(_items[0])
    return list(filter(lambda x: find_price_on_tm(x[0], min_limit_price, max_limit_price), _items))


def compare_prices(_sell_price, sorted_prices_row, days):
    """Сравнивает цену первой вещи выставленной на продажу и цены из истории продаж за последние n продаж"""
    if days == 'ALL':
        sorted_prices = sorted_prices_row[0::]
    elif days > 0:
        sorted_prices = sorted_prices_row[-days::]
    else:
        sorted_prices = sorted_prices_row

    _count = 0
    for price in sorted_prices:
        if price[1] > _sell_price:
            _count += 1
    try:
        _compare = _count / len(sorted_prices)
    except ZeroDivisionError:
        return 0
    return _compare, _count


def calc_profit(_buy_price, _sell_price):
    """Выгодность сделки"""
    _profit = ((_sell_price * 0.87 / _buy_price) - 1) * 100

    return round(_profit, 2)


def main():

    print(errors)
    market_hash_name = unquote(item[1].split('/')[6])
    print(market_hash_name)
    print(item[1])
    tm_price = db_TM.get_min_price(market_hash_name)
    if tm_price:
        tm_price = tm_price[0] / 100
        if tm_price < min_limit_price or tm_price > max_limit_price:
            return False

    # time.sleep(1 + random.random())
    buy_price, second_buy_price, sell_price, second_sell_price = steamAcc.get_steam_prices(item[2])
    print(f"Buy: {buy_price} \n Sell: {sell_price}")
    if buy_price < min_limit_price:
        print('Buy_price_err')
        return False
    if not sell_price:
        print('Sell_price_err')
        return False
    time.sleep(random.random())
    price_history = steamAcc.get_price_history(market_hash_name)
    if not price_history:
        print('Price_history_err')
        return False

    elif price_history == 0:
        bot.send_message(368333609, 'Error response code')  # Я

    price_history_days = steamAcc.get_sales_for_days(price_history, target_days)
    price_history_peaks = steamAcc.get_clear_price_history(price_history_days)
    middle_price = steamAcc.get_avg_price(price_history_peaks)
    count = steamAcc.get_count_sales(price_history_days)
    if count <= min_limit_count:
        print('Count_err')
        errors[2] += 1
        return False

    compare, count_bigger_then_sell_price = compare_prices(sell_price, price_history_peaks, 'ALL')
    if compare < min_limit_compare:
        errors[0] += 1
        print('Compare_err')
        return False
    compare_second_sell_price, count_nahui_nenugen = compare_prices(second_sell_price, price_history_peaks, 'ALL')
    profit = calc_profit(buy_price, sell_price)
    profit_second_price = calc_profit(buy_price, second_sell_price)
    profit_middle = calc_profit(buy_price, middle_price)
    if profit < min_profit:
        errors[1] += 1
        print('Profit_err')
        return False

    print('------------------------------------------')
    print("Название: ", market_hash_name)
    print(item[1])
    print("Цена покупки: ", buy_price)
    print("Средняя цена: ", middle_price)
    print("Количество продаж: ", count)
    print("Профит: ", profit, "%")
    print("Профит ко второй цене: ", profit_second_price, '%')
    print("Профит к средней цене: ", profit_middle, '%')
    print(f"Совпадение цен: {compare * 100}%\n")
    print(f"Совпадение по второй цене: {compare_second_sell_price * 100}%\n")
    print('------------------------------------------')
    message = \
        f"Название: {market_hash_name}\n" \
        f"Ссылка: {item[1]}\n" \
        f"Цена покупки: {buy_price} Руб\n" \
        f"Цена продажи: {sell_price} Руб\n" \
        f"Средняя цена: {middle_price}\n" \
        f"Количество продаж за 2 недели: {count}\n" \
        f"Профит: {profit}%\n" \
        f"Профит ко второй цене: {profit_second_price}% \n" \
        f"Профит к средней цене: {profit_middle}%\n" \
        f"Совпадение цен: {compare * 100}%\n" \
        f"количество продаж больше чем первый ордер: {count_bigger_then_sell_price}\n" \
        f"Совпадение по второй цене: {compare_second_sell_price * 100}%\n" \
        # f"Средняя цена запросов на покупку: {middle_price_order}\n" \
    # f"Количество продаж по запросу за 14 дней: {count_order}\n"
    if autobuy == 'ON':
        steamAcc.create_buy_order(market_hash_name, buy_price, 1)

    bot.send_message(368333609, message)  # Я
    # bot.send_message(1178860614, message)  # Булат


if __name__ == "__main__":
    ## Посчитать минимальную цену продажи чтобы не уйти в минус и посмотреть сколько продаж выше этой цены и есть ли лоты выше такой цены

    steamAcc = steam_price.SteamMarketMethods()
    print(steamAcc.steamclient.is_session_alive())

    bot = telebot.TeleBot('5096520863:AAHHvfFpQTH5fuXHjjAfzYklNGBPw4z57zA')
    db_TM = Database.DatabaseTM()  # Обновляет базу данных ТМ при первом запуске
    db_TM.full_update_db()
    items = get_items_from_db()


    print(items[0])
    target_days = 14  # Период истории продаж в днях
    min_limit_price = 600
    max_limit_price = 800000
    min_limit_count = 15
    min_profit = 4
    min_profit_AVG = 0
    min_limit_compare = 0.2
    autobuy = 'ON'

    errors = [0, 0, 0]
    compare_err, profit_err, count_err = errors
    start = 0
    counter = start
    try:
        for item in items[start::]:
            print('----------------------------------------------')
            print(f"Предмет {counter} из {len(items)}")
            print("Название: ", item[0])
            counter += 1
            try:
                if not main():
                    continue
            except TypeError:
                traceback.print_exc()
                continue

    except Exception:
        traceback.print_exc()
        bot.send_message(368333609, 'Error')  # Я
