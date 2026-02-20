import telebot
import psycopg2
import os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")

bot = telebot.TeleBot(BOT_TOKEN)

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    balance INT DEFAULT 0,
    last_active TIMESTAMP
);
""")
conn.commit()

def create_user(user_id):
    cursor.execute("""
    INSERT INTO users (user_id, balance, last_active)
    VALUES (%s, %s, %s)
    ON CONFLICT (user_id) DO NOTHING;
    """, (user_id, 100, datetime.now()))
    conn.commit()

def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id = %s;", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

def update_last_active(user_id):
    cursor.execute("""
    UPDATE users SET last_active = %s
    WHERE user_id = %s;
    """, (datetime.now(), user_id))
    conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    create_user(user_id)
    update_last_active(user_id)
    bot.send_message(message.chat.id, "🚀 Welcome! You received 100 RDX!")

@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = message.from_user.id
    update_last_active(user_id)
    bal = get_balance(user_id)
    bot.send_message(message.chat.id, f"💰 Your Balance: {bal} RDX")

print("Bot is running...")
bot.infinity_polling()
