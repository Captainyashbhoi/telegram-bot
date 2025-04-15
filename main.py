# main.py

import requests
from bs4 import BeautifulSoup
import json
import datetime
import telegram
import os

# Use GitHub Actions secrets
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telegram.Bot(token=BOT_TOKEN)

price_file = 'price_history.json'

def fetch_prices():
    url = "https://www.metalsdaily.com"  # Replace with a valid source!
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Dummy parsing – replace with actual class names from real site
    gold_price = soup.find('span', {'class': 'gold-price'}).text
    silver_price = soup.find('span', {'class': 'silver-price'}).text
    platinum_price = soup.find('span', {'class': 'platinum-price'}).text

    return {
        'gold': float(gold_price.strip().replace('₹', '').replace(',', '')),
        'silver': float(silver_price.strip().replace('₹', '').replace(',', '')),
        'platinum': float(platinum_price.strip().replace('₹', '').replace(',', ''))
    }

def load_previous_prices():
    try:
        with open(price_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_prices(prices):
    with open(price_file, 'w') as f:
        json.dump(prices, f)

def generate_summary(current_prices, previous_prices):
    summary = ""
    for metal in current_prices:
        change = current_prices[metal] - previous_prices.get(metal, current_prices[metal])
        if change > 0:
            summary += f"{metal.capitalize()} is up ₹{round(change, 2)}.\n"
        elif change < 0:
            summary += f"{metal.capitalize()} is down ₹{abs(round(change, 2))}.\n"
        else:
            summary += f"{metal.capitalize()} is stable.\n"
    return summary

def send_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def job():
    current_prices = fetch_prices()
    previous_prices = load_previous_prices()
    summary = generate_summary(current_prices, previous_prices)
    save_prices(current_prices)
    send_message(f"📊 Precious Metals Update — {datetime.datetime.now().strftime('%H:%M:%S')}\n\n{summary}")

# Run job once (GitHub Actions will call this script every 4 hours)
job()
