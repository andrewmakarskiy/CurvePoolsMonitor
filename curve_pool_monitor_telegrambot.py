import json
import requests
import os
from decimal import Decimal

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def fetch_curve_api():
    url = 'https://api.curve.fi/v1/getPools/big/ethereum'
    response = requests.get(url)
    return response.json()

def parse_curve_api_response(api_response):
    if 'data' in api_response and 'poolData' in api_response['data']:
        pool_data = api_response['data']['poolData']
        for pool in pool_data:
            if pool.get('name') == 'sDAI/sUSDe':
                return pool
    return None

def format_with_decimals(number):
    return f"{Decimal(number):,.2f}"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, json=payload)
    return response.json()

def print_pool_info(pool_info):
    if pool_info:
        total_pool_balance_usd = Decimal(pool_info['usdTotal'])
        total_percent = Decimal('0.00')
        message = "Currency reserves\n"
        
        for coin in pool_info['coins']:
            usd_price = Decimal(coin['usdPrice'])
            pool_balance = Decimal(coin['poolBalance'])
            pool_balance_decimal = pool_balance / (10 ** int(coin['decimals']))
            equivalent_value_usd = pool_balance_decimal * usd_price
            percent_share = (equivalent_value_usd / total_pool_balance_usd) * 100

            total_percent += percent_share

            message += f"{coin['symbol']}\n"
            message += f"${usd_price:.5f} (current USD price)\n"
            message += f"{format_with_decimals(pool_balance_decimal)} {coin['symbol']}\n"
            message += f"${format_with_decimals(equivalent_value_usd)} USD (equivalent value)\n"
            message += f"{percent_share:.2f}% (share in the pool)\n\n"

        message += f"USD total ${format_with_decimals(total_pool_balance_usd)}\n"
        message += f"Total percentage: {total_percent:.2f}%\n"
        message += "(Note: Total percentage may not add up to 100% due to rounding)"
        
        send_telegram_message(message)

def main():
    api_response = fetch_curve_api()
    if api_response:
        pool_info = parse_curve_api_response(api_response)
        print_pool_info(pool_info)

if __name__ == "__main__":
    main()
