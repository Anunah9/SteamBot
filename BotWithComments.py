import random
import sqlite3
import time
import traceback
from os import path
import telebot
import src.steam_price as steam_price
from urllib.parse import unquote
import Database


def get_items_from_db():
    """Функция извлекает предметы из базы данных с определенными исключениями и включениями"""
    # Список исключений
    types_deny = ['%Graffiti%', '%Souvenir%', '%Pin%', '%Music Kit%', '%Case%', '%Sticker%', '%Capsule%',
                  '%UMP-45%', '%Nova%', '%Sawed-Off%', '%PP-Bizon%', '%XM1014%', '%G3SG1%', '%Negev%',
                  '%R8 Revolver%', '%MAG-7%', '%SCAR-20%', '%P2000%', '%Patch%', '%Sealed%']
    # Список включений
    types = ("%Gloves%", "%Wraps%", "%Knife%", "%Karambit%", "%Daggers%", "%Bayonet%")
    # Создание и подключение к базе данных
    path_to_db = path.join(path.curdir, 'src', 'db') + path.sep
    db = sqlite3.connect(path_to_db + 'CS.db')
    cur = db.cursor()

    # Формирование запроса для выборки предметов из базы данных
    NOT_LIKE = ' AND '.join([f"market_hash_name NOT LIKE '{_type}'" for _type in types_deny[1:]])
    LIKE = ' OR '.join([f"market_hash_name LIKE '{_type}'" for _type in types_deny[1:]])
    query = f"SELECT * FROM items WHERE market_hash_name NOT LIKE '{types[0]}' AND ({NOT_LIKE})"

    print(query)
    # Выполнение запроса и получение результата
    result = cur.execute(query).fetchall()
    return result


def find_price_on_tm(market_hash_name, min_limit_price, max_limit_price, db_TM):
    """Функция проверяет цену предмета на торговой площадке csgo market"""
    # Получение минимальной цены предмета на торговой площадке Steam
    tm_price = db_TM.get_min_price(market_hash_name)
    if not tm_price:
        return True
    tm_price = tm_price[0] / 100
    # Проверка, находится ли цена в указанном диапазоне
    return min_limit_price <= tm_price <= max_limit_price


def compare_prices(sell_price, sorted_prices_row, days=14):
    """Сравнивает цену первой вещи выставленной на продажу и цены из истории продаж за последние n продаж"""
    if days == 'ALL':
        sorted_prices = sorted_prices_row[:]
    elif days > 0:
        sorted_prices = sorted_prices_row[-days:]
    else:
        sorted_prices = sorted_prices_row

    count_bigger_than_sell_price = sum(1 for price in sorted_prices if price[1] > sell_price)
    try:
        compare = count_bigger_than_sell_price / len(sorted_prices)
    except ZeroDivisionError:
        return 0
    return compare, count_bigger_than_sell_price


def calc_profit(_buy_price, _sell_price):
    """Функция расчитывает прибыль от сделки"""
    _profit = ((_sell_price * 0.87 / _buy_price) - 1) * 100

    return round(_profit, 2)


def main():
    # Вывод количества предметов которые не прошли по параметрам compare_err, profit_err, count_err
    print(errors)
    # Получение названия предмета из URL
    market_hash_name = unquote(item[1].split('/')[6])
    print(market_hash_name)
    print(item[1])
    # Проверка цены предмета на торговой площадке csgo market
    tm_price = db_TM.get_min_price(market_hash_name)
    if tm_price:
        tm_price = tm_price[0] / 100
        if tm_price < min_limit_price or tm_price > max_limit_price:
            return False

    # Получение цены покупки и продажи предмета с торговой площадки Steam
    buy_price, second_buy_price, sell_price, second_sell_price = steamAcc.get_steam_prices(item[2])
    print(f"Buy: {buy_price} \n Sell: {sell_price}")
    if buy_price < min_limit_price:
        print('Buy_price_err')
        return False
    if not sell_price:
        print('Sell_price_err')
        return False
    time.sleep(random.random())
    # Получение истории продаж предмета
    price_history = steamAcc.get_price_history(market_hash_name)
    if not price_history:
        print('Price_history_err')
        return False
    elif price_history == 0:
        bot.send_message(368333609, 'Error response code')  # Я

    # Получение истории продаж за определенный период
    price_history_days = steamAcc.get_sales_for_days(price_history, target_days)
    # Получение "чистой" истории продаж без выбросов
    price_history_peaks = steamAcc.get_clear_price_history(price_history_days)
    # Расчет средней цены предмета
    middle_price = steamAcc.get_avg_price(price_history_peaks)
    # Расчет количества продаж предмета за определенный период
    count = steamAcc.get_count_sales(price_history_days)
    if count <= min_limit_count:
        print('Count_err')
        errors[2] += 1
        return False

    # Сравнение цены предмета с историей продаж
    compare, count_bigger_then_sell_price = compare_prices(sell_price, price_history_peaks, 14)
    if compare < min_limit_compare:
        errors[0] += 1
        print('Compare_err')
        return False
    # Сравнение второй цены предмета с историей продаж
    compare_second_sell_price, count_nahui_nenugen = compare_prices(second_sell_price, price_history_peaks, 14)
    # Расчет потенциальной прибыли
    profit = calc_profit(buy_price, sell_price)
    profit_second_price = calc_profit(buy_price, second_sell_price)
    profit_middle = calc_profit(buy_price, middle_price)
    if profit < min_profit:
        errors[1] += 1
        print('Profit_err')
        return False

    # Вывод информации о предмете
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

    # Формирование сообщения с информацией о предмете
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
        f"Совпадение по второй цене: {compare_second_sell_price * 100}%\n"

    # Если включена опция автозакупки, то создается ордер на покупку
    if autobuy == 'ON':
        steamAcc.create_buy_order(market_hash_name, round(buy_price, 0), 1)

    # Отправка сообщения с информацией о предмете через Telegram бота
    bot.send_message(368333609, message)  # Я

if __name__ == "__main__":
    # Создание объекта для работы с Steam Marketplace
    steamAcc = steam_price.SteamMarketMethods()
    print(steamAcc.steamclient.is_session_alive())

    # Создание объекта для работы с Telegram ботом
    bot = telebot.TeleBot('5096520863:AAHHvfFpQTH5fuXHjjAfzYklNGBPw4z57zA')
    # Создание объекта для работы с базой данных Steam Marketplace
    db_TM = Database.DatabaseTM()  # Обновляет базу данных ТМ при первом запуске
    db_TM.full_update_db()
    # Получение списка предметов из базы данных
    items = get_items_from_db()

    # Задание параметров фильтрации и анализа предметов
    target_days = 14  # Период истории продаж в днях
    min_limit_price = 5000
    max_limit_price = 800000
    min_limit_count = 15
    min_profit = 2
    min_profit_AVG = 0
    min_limit_compare = 0.2
    autobuy = 'ON'

    # Счетчики ошибок
    errors = [0, 0, 0]
    compare_err, profit_err, count_err = errors
    start = 3800
    counter = start
    try:
        # Цикл обработки предметов
        for item in items[start::]:
            print('----------------------------------------------')
            print(f"Предмет {counter} из {len(items)}")
            print("Название: ", item[0])
            counter += 1
            try:
                # Вызов основной функции для обработки предмета
                if not main():
                    continue
            except TypeError:
                traceback.print_exc()
                continue

    except Exception:
        traceback.print_exc()
        bot.send_message(368333609, 'Error')  # Я
