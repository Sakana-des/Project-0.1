# ZEA (Voice Controlled Assistant)

ZEA adalah asisten virtual berbasis suara (Voice Assistant) yang dikontrol menggunakan perintah suara. Program ini dapat menerima perintah langsung melalui mikrofon komputer atau menggunakan mikrofon dari HP secara *remote* melalui jaringan lokal (WiFi).

## Fitur Utama

- **Panggilan Pintar (Wake Word):** ZEA akan merespon jika Anda memanggil namanya ("Zea").
- **Voice Remote via HP:** ZEA menyediakan web server lokal yang bisa diakses dari browser HP untuk menggunakan HP sebagai mikrofon jarak jauh.
- **Web UI Modern:** Tampilan web futuristik dengan avatar 3D, tombol voice recording, dan tombol manual command.
- **Custom Audio Response:** ZEA membalas perintah dengan file suara MP3 custom (bukan TTS robot).
- **Perintah Suara (Speech-to-Text):** Menggunakan Google Speech Recognition (mengutamakan pengenalan Bahasa Indonesia, dengan adaptasi lafal bahasa inggris).
- **Background Listening:** Mendengarkan perintah secara terus-menerus di latar belakang tanpa membuat antarmuka aplikasi menjadi lambat (freeze).

## Prasyarat (Requirements)

Pastikan Python sudah terinstal di komputer/laptop Anda. Sebelum menjalankan program, Anda perlu menginstal *library* yang dibutuhkan:

```bash
pip install SpeechRecognition sounddevice numpy scipy Flask flask-cors cryptography playsound==1.2.2
```

## File Suara (Wajib Ada di Folder Project)

Pastikan file-file MP3 berikut ada di folder yang sama dengan `zea.py`:
- `whatsYourCommandsSir.mp3` → Diputar saat ZEA dipanggil / startup.
- `AsYourCommandSir,LockingThePc.mp3` → Diputar saat perintah **Lock PC**.
- `shutdown.mp3` → Diputar saat perintah **Shutdown PC**.
- `ZeaExit.mp3` → Diputar saat perintah **Stop/Exit** (mematikan aplikasi ZEA).

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
- Anda bisa memanggil "Zea" terlebih dahulu, lalu tunggu ZEA membalas, kemudian ucapkan perintahnya.
- Atau Anda bisa langsung menggabungkan panggilan dan perintah (contoh: "Zea lock pc").

### Penggunaan Menggunakan Remote HP (Web/Github.io)
Sekarang ZEA memiliki tampilan antarmuka web modern yang canggih (dilengkapi Avatar 3D dan UI futuristik).
Anda dapat langsung membukanya di browser HP (akses via IP Lokal) atau menghosting `index.html` beserta `there.webp` ke **GitHub Pages**.

**Jika menggunakan IP Lokal:**
1. Buka browser HP dan ketik IP dari ZEA (contoh: `https://192.168.1.5:5000`).
2. Izinkan sertifikat SSL (klik Advanced -> Proceed).

**Jika menggunakan GitHub Pages:**
1. Hosting file `index.html` dan `there.webp` ke repositori GitHub Anda dan aktifkan GitHub Pages.
2. Buka link web GitHub Pages Anda di HP.
3. Masukkan IP Address PC Anda pada kolom "IP PC" (contoh: `192.168.1.5`).
4. Klik tombol mikrofon (🎤) untuk memberikan perintah suara atau gunakan tombol-tombol command manual yang tersedia.

### Membuka Firewall (Jika HP Tidak Bisa Konek)
Jika HP Anda tidak bisa mengakses ZEA (error `ERR_CONNECTION_TIMED_OUT`), itu karena **Windows Firewall memblokir port 5000**.
**Tanpa perlu mematikan seluruh Firewall**, cukup jalankan file `open_firewall.bat` yang sudah disediakan:
1. Klik kanan file `open_firewall.bat`.
2. Pilih **"Run as administrator"**.
3. Selesai! Port 5000 akan terbuka dan HP bisa mengakses ZEA.

## Daftar Perintah (Commands)

Berikut adalah daftar perintah suara yang saat ini dikenali oleh ZEA. ZEA mengenali banyak variasi pengucapan/grammar.

### 1. Memanggil ZEA (Wake Words)
Anda bisa memanggil ZEA menggunakan beberapa variasi lafal berikut untuk mengaktifkan mode siaga.
- **Kata kunci yang dikenali:** `"zea"`, `"sea"`, `"zia"`, `"dea"`, `"dia"`, `"jea"`, `"z"`
- **Contoh pengucapan:** `"Zea"`
- **Respon Sistem:** Memutar suara `whatsYourCommandsSir.mp3`

### 2. Mengunci Komputer (Lock PC)
Memerintahkan ZEA untuk mengunci layar Windows (Windows + L).
- **Kata kerja yang dikenali:** `"lock"`, `"look"`, `"log"`, `"blok"`, `"kunci"`, `"lok"`, `"luk"`, `"loc"`, `"locked"`, `"block"`, `"blokkir"`, `"blokir"`, `"gembok"`, `"tutup"`, `"close"`
- **Kata target yang dikenali:** `"pc"`, `"computer"`, `"komputer"`, `"laptop"`, `"leptop"`, `"this"`, `"the pc"`, `"screen"`, `"layar"`, `"monitor"`
- **Contoh Perintah:** `"Zea lock the pc"`, `"Zea kunci laptop"`, `"Zea gembok layar"`
- **Respon Sistem:** Memutar suara `AsYourCommandSir,LockingThePc.mp3` lalu layar Windows terkunci.

### 3. Mematikan Komputer (Shutdown PC)
Memerintahkan ZEA untuk mematikan perangkat Anda secara total.
- **Kata kerja yang dikenali:** `"shutdown"`, `"shut down"`, `"matikan"`, `"mati"`, `"turn off"`, `"power off"`, `"shut"`, `"shat down"`, `"setdown"`, `"shatdown"`, `"saddown"`, `"sutdown"`, `"shutdaun"`, `"setdaun"`
- **Kata target yang dikenali:** (sama dengan Lock PC di atas)
- **Contoh Perintah:** `"Zea shutdown the pc"`, `"Zea matikan komputer"`, `"Zea shutdown"`
- **Respon Sistem:** Memutar suara `shutdown.mp3` lalu komputer dimatikan (mati total dalam 3 detik).

### 4. Menghentikan Aplikasi ZEA (Exit/Stop)
Memerintahkan aplikasi ZEA untuk menutup diri dan berhenti berjalan.
- **Kata kunci yang dikenali:** `"keluar"`, `"exit"`, `"stop"`, `"quit"`, `"berhenti"`, `"close zea"`, `"tutup zea"`, `"matikan zea"`
- **Contoh Perintah:** `"Zea stop"`, `"Zea keluar"`, `"Zea quit"`
- **Respon Sistem:** Memutar suara `ZeaExit.mp3` lalu aplikasi akan tertutup.

---

**Tips Tambahan:**
- Terdapat juga tombol **EMERGENCY STOP** berwarna merah di tampilan aplikasi di PC. Anda dapat mengkliknya secara manual kapan saja jika ingin menghentikan aplikasi dengan cepat.
- Di halaman web terdapat tombol-tombol manual (Lock PC, Stop, Shutdown) sebagai alternatif jika perintah suara tidak terdeteksi.
