# ZEA (Voice Controlled Assistant)

ZEA adalah asisten virtual berbasis suara (Voice Assistant) yang dikontrol menggunakan perintah suara. Program ini dapat menerima perintah langsung melalui mikrofon komputer atau menggunakan mikrofon dari HP secara *remote* melalui jaringan lokal (WiFi).

## Fitur Utama

- **Panggilan Pintar (Wake Word):** ZEA akan merespon jika Anda memanggil namanya ("Zea").
- **Voice Remote via HP:** ZEA menyediakan web server lokal yang bisa diakses dari browser HP untuk menggunakan HP sebagai mikrofon jarak jauh.
- **Perintah Suara (Speech-to-Text):** Menggunakan Google Speech Recognition (mengutamakan pengenalan Bahasa Indonesia, dengan adaptasi lafal bahasa inggris).
- **Text-to-Speech:** ZEA akan merespon atau membalas secara interaktif dengan suara.
- **Background Listening:** Mendengarkan perintah secara terus-menerus di latar belakang tanpa membuat antarmuka aplikasi menjadi lambat (freeze).

## Prasyarat (Requirements)

Pastikan Python sudah terinstal di komputer/laptop Anda. Sebelum menjalankan program, Anda perlu menginstal *library* yang dibutuhkan dengan cara membuka Terminal/Command Prompt dan menjalankan perintah berikut:

```bash
pip install SpeechRecognition pyttsx3 sounddevice numpy scipy Flask pywin32
```

## Cara Menjalankan

1. Buka terminal atau command prompt di dalam folder project ini.
2. Jalankan file `zea.py` menggunakan Python:
   ```bash
   python zea.py
   ```
3. Akan muncul jendela aplikasi ZEA dengan status "Standby".
4. Di jendela tersebut, Anda akan melihat alamat IP untuk diakses via HP (contoh: `https://192.168.x.x:5000`).

### Penggunaan Melalui Mikrofon Lokal (Laptop/PC)
- Secara default, aplikasi sudah terus mendengarkan melalui mikrofon PC Anda.
- Anda bisa memanggil "Zea" terlebih dahulu, lalu tunggu ZEA membalas *"What's your command sir?"*, kemudian ucapkan perintahnya.
- Atau Anda bisa langsung menggabungkan panggilan dan perintah (contoh: "Zea lock pc").

### Penggunaan Menggunakan Remote HP
Fitur ini sangat berguna jika Anda sedang jauh dari jangkauan mikrofon laptop.

1. Pastikan HP dan PC Anda terhubung ke jaringan WiFi/Internet yang sama.
2. Buka browser di HP (disarankan Chrome atau Safari).
3. Masukkan alamat IP beserta port yang tertera di aplikasi ZEA (contoh: `https://192.168.1.5:5000`).
4. **Penting:** Karena aplikasi ini menggunakan sertifikat SSL *adhoc* buatan sendiri agar izin mikrofon di browser HP terbuka, browser akan memberi peringatan **"Connection is not private"** atau **"Koneksi Tidak Aman"**. 
   - Anda cukup klik tombol **Advanced (Lanjutan)**, lalu klik tulisan **Proceed / Lanjutkan** ke alamat tersebut.
5. Pada halaman web yang terbuka, klik tombol **TAP TO SPEAK** dan izinkan akses mikrofon jika muncul *pop-up* permintaan dari browser.
6. Ucapkan perintah Anda.

## Daftar Perintah (Commands)

Berikut adalah daftar perintah suara yang saat ini dikenali oleh ZEA. Program mendeteksi kata kunci dari kalimat yang Anda ucapkan.

### 1. Memanggil ZEA (Wake Words)
Anda bisa memanggil ZEA menggunakan beberapa variasi lafal berikut untuk mengaktifkan mode siaga.
- **Kata kunci yang dikenali:** `"zea"`, `"sea"`, `"zia"`, `"dea"`, `"dia"`, `"jea"`, `"z"`
- **Contoh pengucapan:** `"Zea"`
- **Respon Sistem:** ZEA akan membalas *"What's your command sir?"*

### 2. Mematikan Komputer (Shutdown / Lock PC)
Memerintahkan ZEA untuk mematikan PC dalam waktu 3 detik.
- **Syarat:** Sistem mendeteksi gabungan dari kata kerja dan kata bendanya.
  - Kata kerja: `"lock"`, `"look"`, `"log"`, `"blok"`
  - Kata benda: `"pc"`, `"visi"` (menyerupai *pc*/*this pc*), `"this"`, `"the pc"`, `"dpc"`
- **Contoh Perintah:** `"Zea lock pc"` atau `"Zea lock the pc"`
- **Respon Sistem:** *"As your command sir"* lalu PC akan **shutdown** (mati total).

*(Catatan: Saat ini sistem diatur untuk mematikan perangkat `shutdown /s`, bukan sekadar lock screen)*

### 3. Menghentikan Aplikasi ZEA (Exit/Stop)
Memerintahkan aplikasi ZEA untuk menutup diri dan berhenti berjalan.
- **Kata kunci yang dikenali:** `"keluar"`, `"exit"`, `"stop"`
- **Contoh Perintah:** `"Zea stop"` atau `"Zea keluar"`
- **Respon Sistem:** *"Emergency stop diaktifkan. Mematikan sistem ZEA."* lalu aplikasi akan tertutup.

---

**Tips Tambahan:**
- Terdapat juga tombol **EMERGENCY STOP** berwarna merah di tampilan aplikasi di PC. Anda dapat mengkliknya secara manual kapan saja jika ingin menghentikan aplikasi dengan cepat.
