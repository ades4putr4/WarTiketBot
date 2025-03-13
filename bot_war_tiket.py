import telebot
import schedule
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading

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

# Handler untuk perintah /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    bot.send_message(chat_id, "Halo! Silakan masukkan data Anda untuk war tiket.\n\nKetik `/daftar` untuk mulai.")

# Handler untuk perintah /daftar (memasukkan data)
@bot.message_handler(commands=['daftar'])
def start_registration(message):
    chat_id = str(message.chat.id)
    bot.send_message(chat_id, "Silakan kirim nama Anda:")
    user_data[chat_id] = {"step": "nama"}
    save_data()

# Handler untuk menangkap input pengguna
@bot.message_handler(func=lambda message: str(message.chat.id) in user_data and user_data[str(message.chat.id)]["step"] in ["nama", "nik", "hp", "lokasi", "tanggal", "sesi"])
def handle_user_input(message):
    chat_id = str(message.chat.id)
    step = user_data[chat_id]["step"]

    if step == "nama":
        user_data[chat_id]["nama"] = message.text
        bot.send_message(chat_id, "Masukkan NIK:")
        user_data[chat_id]["step"] = "nik"
    
    elif step == "nik":
        user_data[chat_id]["nik"] = message.text
        bot.send_message(chat_id, "Masukkan No HP:")
        user_data[chat_id]["step"] = "hp"
    
    elif step == "hp":
        user_data[chat_id]["hp"] = message.text
        bot.send_message(chat_id, "Masukkan lokasi penukaran:")
        user_data[chat_id]["step"] = "lokasi"
    
    elif step == "lokasi":
        user_data[chat_id]["lokasi"] = message.text
        bot.send_message(chat_id, "Masukkan tanggal penukaran (YYYY-MM-DD):")
        user_data[chat_id]["step"] = "tanggal"
    
    elif step == "tanggal":
        user_data[chat_id]["tanggal"] = message.text
        bot.send_message(chat_id, "Masukkan sesi (misal: 13:00 atau 14:00):")
        user_data[chat_id]["step"] = "sesi"
    
    elif step == "sesi":
        user_data[chat_id]["sesi"] = message.text
        user_data[chat_id]["step"] = "done"
        bot.send_message(chat_id, "✅ Data berhasil disimpan! Tiket akan dipesan otomatis pada jam yang ditentukan.")
    
    save_data()

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

        # Isi formulir
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

        # Klik Submit
        driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]").click()
        time.sleep(2)

        driver.quit()
        
        # Kirim notifikasi ke Telegram setelah sukses
        bot.send_message(chat_id, f"✅ Tiket berhasil dipesan!\n\n👤 Nama: {data['nama']}\n📍 Lokasi: {data['lokasi']}\n📅 Tanggal: {data['tanggal']}\n🕐 Sesi: {data['sesi']}")

    except Exception as e:
        bot.send_message(chat_id, f"❌ Gagal mendapatkan tiket: {str(e)}")

# Fungsi untuk menjalankan war tiket otomatis pada jam 00:00
def run_war():
    for chat_id, data in user_data.items():
        if data.get("step") == "done":
            bot.send_message(chat_id, "⏳ Memulai war tiket...")
            war_tiket(chat_id, data)

# Jadwalkan eksekusi pada pukul 00:00
schedule.every().day.at("00:00").do(run_war)

# Jalankan bot dan scheduler
def run_bot():
    while True:
        schedule.run_pending()
        time.sleep(1)

print("Bot berjalan...")

# Menjalankan bot dalam thread agar tidak memblokir
bot_thread = threading.Thread(target=bot.polling, kwargs={"none_stop": True})
bot_thread.start()

# Menjalankan scheduler dalam thread terpisah
schedule_thread = threading.Thread(target=run_bot)
schedule_thread.start()
