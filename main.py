# -*- coding: utf-8 -*-
import datetime
from math import ceil

import requests
from datetime import date
from secrets import (
    ALPHA_VANTAGE_API_KEY,
    NEWSAPI_API_KEY,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_TEST_PHONE_NUMBER,
    TWILIO_MESSAGING_SERVICE_SID,
)
from twilio.rest import Client


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"


def one_day_before(day):
    return day - datetime.timedelta(days=1)


def get_last_trading_day_closing_price_for(day, daily_time_series):
    day_formatted = day.strftime("%Y-%m-%d")
    trade_data = daily_time_series.get(day_formatted)
    if trade_data:
        return day, float(trade_data["4. close"])
    else:
        one_day_before_current = one_day_before(day)
        return get_last_trading_day_closing_price_for(one_day_before_current, daily_time_series)


def calculate_stock_price_change_percentage():
    url = "https://www.alphavantage.co/query"
    query_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }
    response = requests.get(url, params=query_params)
    data = response.json()
    daily_time_series = data["Time Series (Daily)"]
    last_trading_day, most_recent_trading_day_price = get_last_trading_day_closing_price_for(
        date.today(),
        daily_time_series,
    )
    day_before_last_trading_day = one_day_before(last_trading_day)
    _, penultimate_trading_day_price = get_last_trading_day_closing_price_for(
        day_before_last_trading_day,
        daily_time_series,
    )
    difference = most_recent_trading_day_price - penultimate_trading_day_price
    difference_percent = difference / most_recent_trading_day_price * 100
    return ceil(difference_percent)


def get_latest_news_about(company_name):
    url = "https://newsapi.org/v2/top-headlines"
    query_params = {
        "q": company_name,
        "apiKey": NEWSAPI_API_KEY,
        "pageSize": 3,
    }
    response = requests.get(url, params=query_params)
    data = response.json()
    articles = data['articles']
    return [{'title': article['title'], 'description': article['description']} for article in articles]


def create_message_from(stock_price_change, news):
    formatted_news = f"{STOCK}: {'🔺' if stock_price_change > 0 else '🔻'}{stock_price_change}%"
    for article in news:
        formatted_news += f"""
    Headline: {article['title']}
    Brief: {article['description']}
    """
    return formatted_news


def send_sms(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        to=TWILIO_TEST_PHONE_NUMBER,
        messaging_service_sid=TWILIO_MESSAGING_SERVICE_SID,
        body=message,
    )


stock_price_change = calculate_stock_price_change_percentage()
if abs(stock_price_change) > 0:
    news = get_latest_news_about(COMPANY_NAME)
    message = create_message_from(stock_price_change, news)
    send_sms(message)
