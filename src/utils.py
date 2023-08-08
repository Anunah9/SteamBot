import urllib.parse


def convert_price(price):
    return float(price.split(' ')[0].replace(',', '.'))


def convert_name(market_hash_name):
    return urllib.parse.quote(market_hash_name)