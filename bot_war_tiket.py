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
except FileNotFoundError:
    user_data = {}

# Fungsi untuk menyimpan data ke JSON
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

# Fungsi untuk booking tiket otomatis
def war_tiket(chat_id, data):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Mode tanpa GUI agar lebih cepat
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get("https://pintar.bi.go.id/Order/ListKasKeliling")
        time.sleep(2)

        # Klik tombol 'Daftar Penukaran'
        driver.find_element(By.XPATH, "//button[contains(text(), 'Daftar')]").click()
        time.sleep(1)

        # Isi Nama
        driver.find_element(By.NAME, "nama").send_keys(data["nama"])

        # Isi NIK
        driver.find_element(By.NAME, "nik").send_keys(data["nik"])

        # Isi Nomor HP
        driver.find_element(By.NAME, "no_hp").send_keys(data["hp"])

        # Pilih Lokasi
        lokasi = driver.find_element(By.NAME, "lokasi")
        lokasi.send_keys(data["lokasi"])
        lokasi.send_keys(Keys.RETURN)

        # Pilih Tanggal
        driver.find_element(By.NAME, "tanggal").send_keys(data["tanggal"])

        # Pilih Sesi
        sesi_dropdown = driver.find_element(By.NAME, "sesi")
        sesi_dropdown.send_keys(data["sesi"])
        sesi_dropdown.send_keys(Keys.RETURN)

        # Klik Submit
        driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]").click()
        time.sleep(2)

        driver.quit()
        
        # Kirim notifikasi ke Telegram setelah sukses
        bot.send_message(chat_id, f"✅ Tiket berhasil dipesan!\n\n👤 Nama: {data['nama']}\n📍 Lokasi: {data['lokasi']}\n📅 Tanggal: {data['tanggal']}\n🕐 Sesi: {data['sesi']}")

    except Exception as e:
        bot.send_message(chat_id, f"❌ Gagal mendapatkan tiket: {str(e)}")

# Fungsi untuk menjalankan war tiket otomatis pada jam 13:00 dan 14:00
def run_war():
    for chat_id, data in user_data.items():
        if data.get("step") == "done":
            bot.send_message(chat_id, "⏳ Memulai war tiket...")
            war_tiket(chat_id, data)

# Jadwalkan eksekusi pada pukul 13:00 dan 14:00
schedule.every().day.at("13:00").do(run_war)
schedule.every().day.at("14:00").do(run_war)

# Jalankan bot dan scheduler
def run_bot():
    while True:
        schedule.run_pending()
        time.sleep(1)

import threading

print("Bot berjalan...")
bot_thread = threading.Thread(target=bot.polling)
bot_thread.start()

schedule_thread = threading.Thread(target=run_bot)
schedule_thread.start()
