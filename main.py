import requests
from twilio.rest import Client
from dotenv import dotenv_values

# unpacking dict from env
config = {
    **dotenv_values('.env')
}

STOCK = config['STOCK']
COMPANY_NAME = "Tesla Inc"
stock_api_key = config['stock_api_key']
news_api_key = config['news_api_key']
twilio_account_sid = config['t_account_sid']
twilio_auth_token = config['t_auth_token']
sender_number = config['from']
recipient_number = config['to']
up_or_down = None

# When STOCK price increase/decreases by 1% between yesterday and the day before yesterday then print("Get News").

response = requests.get(
    f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={STOCK}&apikey={stock_api_key}")
result = response.json()['Time Series (Daily)']
data_list = [value for value in result.values()]
y_day_closing_price = data_list[0]['4. close']
d_before_closing_price = data_list[1]['4. close']
p_diff = float(y_day_closing_price) - float(d_before_closing_price)
if p_diff > 0:
    up_or_down = "🔺"
else:
    up_or_down = "🔻"

percentage = p_diff / float(y_day_closing_price) * 100

# if percentage greater than 1% send the relevant news to the user
if abs(percentage) > 1:
    news_articles = requests.get(f'https://newsapi.org/v2/everything?q=tesla&apiKey={news_api_key}').json()['articles']

    # extracting first three articles
    three_news_list = news_articles[:3]
    # formatting the sms in a list

    formatted_article_list = [
        f"{STOCK}:{up_or_down} {round(percentage)}%\nHeadline:{article['title']}\nBrief:{article['description']}" for
        article in
        three_news_list]

    client = Client(twilio_account_sid, twilio_auth_token)
    for article in formatted_article_list:
        message = client.messages.create(body=article,
                                         from_=sender_number,
                                         to=recipient_number)
