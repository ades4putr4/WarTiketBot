import schedule
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

# Input data pengguna
chat_id = "terminal_user"
user_data[chat_id] = {}
user_data[chat_id]["nama"] = input("Masukkan Nama: ")
user_data[chat_id]["nik"] = input("Masukkan NIK: ")
user_data[chat_id]["hp"] = input("Masukkan No HP: ")
user_data[chat_id]["lokasi"] = input("Masukkan lokasi penukaran: ")
user_data[chat_id]["tanggal"] = input("Masukkan tanggal penukaran (YYYY-MM-DD): ")
user_data[chat_id]["sesi"] = input("Masukkan sesi (misal: 13:00 atau 14:00): ")
user_data[chat_id]["step"] = "done"
save_data()

print("✅ Data berhasil disimpan! Tiket akan dipesan otomatis pada jam yang ditentukan.")

# Fungsi untuk booking tiket otomatis
def war_tiket():
    data = user_data[chat_id]
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
        print(f"✅ Tiket berhasil dipesan!")
    except Exception as e:
        print(f"❌ Gagal mendapatkan tiket: {str(e)}")

# Jalankan war tiket otomatis pada pukul 00:00
schedule.every().day.at("00:00").do(war_tiket)

# Jalankan scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
