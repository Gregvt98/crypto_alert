import requests
import pandas as pd
from scipy import stats
import time

coin_api_key = 'your api key'
slack_token = 'your slack token'

#define functions
def coin_prices(crypto):
    url = 'https://rest.coinapi.io/v1/exchangerate/{0}/USD'.format(crypto)
    headers = {'X-CoinAPI-Key' : coin_api_key}
    response = requests.get(url, headers=headers)
    content = response.json()
    current_price = content['rate']
    current_time = content['time']

    #get historical prices (30 days)
    url = 'https://rest.coinapi.io/v1/ohlcv/{0}/USD/latest?period_id=1DAY&limit=30'.format(crypto)
    headers = {'X-CoinAPI-Key' : 'D8BF3050-A2BB-47DD-81AB-E450A38EF329'}
    response = requests.get(url, headers=headers)
    content = response.json()
    df_30 = pd.DataFrame(content)

     # get historical prices (90 days)
    url = 'https://rest.coinapi.io/v1/ohlcv/{0}/USD/latest?period_id=1DAY&limit=90'.format(crypto)
    headers = {'X-CoinAPI-Key' : coin_api_key}
    response = requests.get(url, headers=headers)
    content = response.json()
    df_90 = pd.DataFrame(content)

    #calculate percentiles
    day_30_percentile = stats.percentileofscore(df_30.price_close, current_price)
    day_90_percentile = stats.percentileofscore(df_90.price_close, current_price)

    return {'current_price': current_price, 'day_30_percentile': day_30_percentile , 'day_90_percentile': day_90_percentile}

def create_message(crypto, current_price, day_30_percentile):
    if day_30_percentile <= 20:
        status = 'BARGAIN'
    elif day_30_percentile <= 80:
        status = 'NORMAL'
    else:
        status = 'RIP-OFF'

    percentile_formatted = "{:.1%}".format(day_30_percentile/100)
    current_price_formatted = '${:,.2f}'.format(current_price)

    message = '{0} is a {1} today. The current price of {2} is higher than {3} of closing prices during the last 30 days.'.format(crypto, status, current_price_formatted, percentile_formatted)
    return(message)

def slack_message(text):
    slack_api_url = 'https://slack.com/api/chat.postMessage'
    data = {'token': slack_token,
            'channel': "#app",
             "text": text}
    # post message to crypto_alerts slack channel
    r = requests.post(url = slack_api_url, data = data)

cryptos = ['BTC', 'ETH', 'XRP']
for crypto in cryptos:
    time.sleep(4)
    result = coin_prices(crypto)
    current_price = result['current_price']
    day_30_percentile = result['day_30_percentile']
    day_90_percentile = result['day_90_percentile']
    message = create_message(crypto, current_price, day_30_percentile)
    slack_message(message)
    print(crypto, current_price, day_30_percentile, day_90_percentile)
