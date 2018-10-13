import requests
from decimal import Decimal, ROUND_UP
from urllib.parse import quote

FIXED_RATES = {"BTC": 1}
BTC_MSAT_RATIO = Decimal('100000000000')


def get_rate(currency):
    """
    Fetches the current exchange rate from BitcoinAverage
    """
    resp = requests.get(f'https://apiv2.bitcoinaverage.com/indices/global/ticker/short?crypto=BTC&fiat={quote(currency)}')
    if resp.status_code == 404:
        raise ValueError(f"unknown currency: {currency}")
    print(resp.json())
    return resp.json()[f'BTC{currency}'].get('last')


def to_msat(currency, amount):
    """
    convert to msatoshis
    """
    if currency in FIXED_RATES:
        rate = FIXED_RATES[currency]
    else:
        rate = get_rate(currency)
    return int(((Decimal(amount) / Decimal(rate)) * BTC_MSAT_RATIO).quantize(Decimal('1'), rounding=ROUND_UP))
