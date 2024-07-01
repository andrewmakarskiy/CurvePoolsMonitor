import requests
from decimal import Decimal, getcontext

# Function to fetch Curve.fi API response
def fetch_curve_api():
    url = 'https://api.curve.fi/v1/getPools/big/ethereum'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad response status
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Curve.fi API: {e}")
        return None

# Function to parse and format pool information
def parse_curve_api_response(api_response):
    if 'data' in api_response and 'poolData' in api_response['data']:
        pool_data = api_response['data']['poolData']
        for pool in pool_data:
            if pool.get('name') == 'sDAI/sUSDe':
                return pool
        print("sDAI/sUSDe pool not found in the API response. Check the structure of the API response.")
    else:
        print("Expected 'data' key with 'poolData' in the API response. Check the structure of the API response.")
    return None

# Function to format number with commas and adjust decimals
def format_with_decimals(number):
    return f"{Decimal(number):,.2f}"  # Format with two decimal places and commas

# Function to print pool information in required format
def print_pool_info(pool_info):
    if pool_info:
        total_pool_balance_usd = Decimal(pool_info['usdTotal'])
        total_percent = Decimal('0.00')

        print("Currency reserves")
        for coin in pool_info['coins']:
            usd_price = Decimal(coin['usdPrice'])
            pool_balance = coin['poolBalance']
            pool_balance_decimal = Decimal(pool_balance) / (10 ** int(coin['decimals']))  # Convert pool balance to Decimal
            percent_share = (pool_balance_decimal * usd_price / total_pool_balance_usd) * 100

            total_percent += percent_share

            print(f"{coin['symbol']}")
            print(f"${usd_price:.5f} (current USD price)")
            print(f"{format_with_decimals(pool_balance_decimal)} {coin['symbol']}")
            
            # Calculate equivalent value in USD
            pool_balance_usd = pool_balance_decimal * usd_price
            print(f"${format_with_decimals(pool_balance_usd)} USD (equivalent value)")

            print(f"{percent_share:.2f}% (share in the pool)")
            print()

        # Calculate total percentage
        print(f"USD total ${format_with_decimals(total_pool_balance_usd)}")
        print(f"Total percentage: {total_percent:.2f}%")
        print("(Note: Total percentage may not add up to 100% due to rounding)")

# Main function to execute the script
def main():
    # Fetch Curve.fi API response
    api_response = fetch_curve_api()
    if api_response:
        # Parse API response and extract pool information
        pool_info = parse_curve_api_response(api_response)
        # Print pool information in required format
        print_pool_info(pool_info)

if __name__ == "__main__":
    main()
