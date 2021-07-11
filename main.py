# -*- coding: utf-8 -*-
import datetime

import requests
from datetime import date
from secrets import ALPHA_VANTAGE_API_KEY

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"


def day_before(last_trading_day):
    return last_trading_day - datetime.timedelta(days=1)


# TODO refact to recursive
def get_last_trading_day_data_for(day, daily_time_series):
    last_trading_day = day
    last_trading_day_formatted = last_trading_day.strftime("%Y-%m-%d")
    trade_data = daily_time_series.get(last_trading_day_formatted)
    while not trade_data:
        last_trading_day = day_before(last_trading_day)
        last_trading_day_formatted = last_trading_day.strftime("%Y-%m-%d")
        trade_data = daily_time_series.get(last_trading_day_formatted)
    return last_trading_day, trade_data


def calculate_stock_price_change():
    url = "https://www.alphavantage.co/query"
    query_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }
    response = requests.get(url, params=query_params)
    data = response.json()
    daily_time_series = data["Time Series (Daily)"]
    last_trading_day, most_recent_trading_day_data = get_last_trading_day_data_for(date.today(), daily_time_series)
    current_closing_price = most_recent_trading_day_data["closing"]
    day_before_last_trading_day = day_before(last_trading_day)
    _, penultimate_trading_day_data = get_last_trading_day_data_for(day_before_last_trading_day, daily_time_series)


stock_price_change = calculate_stock_price_change()
if abs(stock_price_change) > 0:
    print("Get News")

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

