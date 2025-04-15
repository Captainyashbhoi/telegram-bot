# main.py

import requests
from bs4 import BeautifulSoup
import json
import datetime
import schedule
import time
import telegram
from config import BOT_TOKEN, CHAT_ID

# Telegram Bot Setup
bot = telegram.Bot(token=BOT_TOKEN)

# Price history file
price_file = 'price_history.json'

# Function to fetch metal prices
def fetch_prices():
    url = "https://www.metalsdaily.com"  # Replace with an actual live metals price website
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extracting price (replace these lines based on the website structure)
    gold_price = soup.find('span', {'class': 'gold-price'}).text
    silver_price = soup.find('span', {'class': 'silver-price'}).text
    platinum_price = soup.find('span', {'class': 'platinum-price'}).text

    return {
        'gold': float(gold_price.strip().replace('₹', '').replace(',', '')),
        'silver': float(silver_price.strip().replace('₹', '').replace(',', '')),
        'platinum': float(platinum_price.strip().replace('₹', '').replace(',', ''))
    }

# Function to load previous price data
def load_previous_prices():
    try:
        with open(price_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Function to save current price data
def save_prices(prices):
    with open(price_file, 'w') as f:
        json.dump(prices, f)

# Function to generate a summary
def generate_summary(current_prices, previous_prices):
    summary = ""
    for metal in current_prices:
        change = current_prices[metal] - previous_prices.get(metal, current_prices[metal])
        if change > 0:
            summary += f"{metal.capitalize()} is up ₹{change}.\n"
        elif change < 0:
            summary += f"{metal.capitalize()} is down ₹{abs(change)}.\n"
        else:
            summary += f"{metal.capitalize()} is stable.\n"
    
    return summary

# Function to send message via Telegram
def send_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

# Main function to fetch prices, analyze, and send updates
def job():
    current_prices = fetch_prices()
    previous_prices = load_previous_prices()

    # Generate the summary based on the comparison
    summary = generate_summary(current_prices, previous_prices)

    # Save the current prices for future comparison
    save_prices(current_prices)

    # Send summary via Telegram
    send_message(f"📊 Precious Metals Update — {datetime.datetime.now().strftime('%H:%M:%S')}\n\n{summary}")

# Schedule to run every 4 hours (from 8 AM to 8 PM IST)
schedule.every().day.at("08:00").do(job)
schedule.every().day.at("12:00").do(job)
schedule.every().day.at("16:00").do(job)
schedule.every().day.at("20:00").do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)  # Wait 1 minute before checking again
