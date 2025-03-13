import telebot
import schedule
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Masukkan API Token dari BotFather
TOKEN = "7734160291:AAFZlIe9Xovsv2FSDK8hY6822mt5Owi1C8A"
bot = telebot.TeleBot(TOKEN)

# File penyimpanan data user
DATA_FILE = "data_user.json"

# Cek apakah file JSON sudah ada, jika tidak buat file kosong
try:
    with open(DATA_FILE, "r") as file:
        user_data = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    user_data = {}

# Fungsi untuk menyimpan data ke JSON
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

# Fungsi untuk menangani perintah /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    user_data[chat_id] = {"step": "nama"}  # Mulai dengan pengisian nama
    save_data()
    bot.send_message(chat_id, "Selamat datang! Silakan masukkan nama Anda:")

# Fungsi untuk menangani input user
def handle_input(message):
    chat_id = str(message.chat.id)
    if chat_id not in user_data:
        user_data[chat_id] = {"step": "nama"}
    
    step = user_data[chat_id].get("step")
    text = message.text
    
    if step == "nama":
        user_data[chat_id]["nama"] = text
        user_data[chat_id]["step"] = "nik"
        bot.send_message(chat_id, "Masukkan NIK Anda:")
    elif step == "nik":
        user_data[chat_id]["nik"] = text
        user_data[chat_id]["step"] = "hp"
        bot.send_message(chat_id, "Masukkan Nomor HP Anda:")
    elif step == "hp":
        user_data[chat_id]["hp"] = text
        user_data[chat_id]["step"] = "lokasi"
        bot.send_message(chat_id, "Masukkan Lokasi Penukaran:")
    elif step == "lokasi":
        user_data[chat_id]["lokasi"] = text
        user_data[chat_id]["step"] = "tanggal"
        bot.send_message(chat_id, "Masukkan Tanggal (YYYY-MM-DD):")
    elif step == "tanggal":
        user_data[chat_id]["tanggal"] = text
        user_data[chat_id]["step"] = "sesi"
        bot.send_message(chat_id, "Masukkan Sesi (misal: 13:00 atau 14:00):")
    elif step == "sesi":
        user_data[chat_id]["sesi"] = text
        user_data[chat_id]["step"] = "done"
        bot.send_message(chat_id, "✅ Data berhasil disimpan! Tiket akan dipesan otomatis pada pukul 00:00.")
    
    save_data()

# Fungsi untuk booking tiket otomatis
def war_tiket():
    for chat_id, data in user_data.items():
        if data.get("step") == "done":
            try:
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

                driver.get("https://pintar.bi.go.id/Order/ListKasKeliling")
                time.sleep(2)
                driver.find_element(By.XPATH, "//button[contains(text(), 'Daftar')]").click()
                time.sleep(1)
                
                driver.find_element(By.NAME, "nama").send_keys(data["nama"])
                driver.find_element(By.NAME, "nik").send_keys(data["nik"])
                driver.find_element(By.NAME, "no_hp").send_keys(data["hp"])
                
                lokasi = driver.find_element(By.NAME, "lokasi")
                lokasi.send_keys(data["lokasi"])
                lokasi.send_keys(Keys.RETURN)
                
                driver.find_element(By.NAME, "tanggal").send_keys(data["tanggal"])
                
                sesi_dropdown = driver.find_element(By.NAME, "sesi")
                sesi_dropdown.send_keys(data["sesi"])
                sesi_dropdown.send_keys(Keys.RETURN)
                
                driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]").click()
                time.sleep(2)

                driver.quit()
                bot.send_message(chat_id, f"✅ Tiket berhasil dipesan untuk {data['nama']} pada {data['tanggal']} sesi {data['sesi']}")
            except Exception as e:
                bot.send_message(chat_id, f"❌ Gagal mendapatkan tiket: {str(e)}")

# Jadwalkan eksekusi pada pukul 00:00
schedule.every().day.at("00:00").do(war_tiket)

# Jalankan bot dan scheduler
def run_bot():
    while True:
        schedule.run_pending()
        time.sleep(1)

import threading

print("Bot berjalan...")
bot_thread = threading.Thread(target=bot.polling, kwargs={"none_stop": True})
bot_thread.start()

schedule_thread = threading.Thread(target=run_bot)
schedule_thread.start()

# Tangani semua pesan yang masuk
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    handle_input(message)

bot.polling()
