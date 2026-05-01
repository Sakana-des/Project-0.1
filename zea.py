import speech_recognition as sr
import os
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import threading
import queue
import tkinter as tk
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import socket
from playsound import playsound

# Matikan log Flask agar terminal lebih bersih
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Mendapatkan path absolut dari folder script ini
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)
cmd_queue = queue.Queue()
audio_queue = queue.Queue()

# Mapping file suara MP3
SOUND_FILES = {
    "wake":     os.path.join(SCRIPT_DIR, "whatsYourCommandsSir.mp3"),
    "lock":     os.path.join(SCRIPT_DIR, "AsYourCommandSir,LockingThePc.mp3"),
    "shutdown": os.path.join(SCRIPT_DIR, "shutdown.mp3"),
    "exit":     os.path.join(SCRIPT_DIR, "ZeaExit.mp3"),
}

# Thread khusus untuk memutar suara MP3 agar tidak bikin GUI ngelag/freeze
def audio_worker():
    while True:
        sound_key = audio_queue.get()
        if sound_key is None:
            break
        filepath = SOUND_FILES.get(sound_key)
        if filepath and os.path.exists(filepath):
            print(f"ZEA: [Memutar {os.path.basename(filepath)}]")
            try:
                playsound(filepath)
            except Exception as e:
                print(f"[Audio Error] {e}")
        else:
            print(f"ZEA: [File suara '{sound_key}' tidak ditemukan: {filepath}]")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/command', methods=['POST'])
def receive_command():
    data = request.json
    command = data.get("command", "").lower()
    for p in "!?,.":
        command = command.replace(p, "")
    print(f"\n[Remote HP] Anda berkata: {command}")
    cmd_queue.put(command)
    return jsonify({"status": "success"})

def run_flask():
    # Menjalankan flask dengan SSL Adhoc agar fitur Mic di HP (Chrome/Safari) bisa berjalan.
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, ssl_context='adhoc')


# ---- Sistem ZEA (GUI & Logika) ----

class ZeaAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("ZEA System")
        self.root.geometry("400x300")
        self.root.configure(bg="#1e1e1e")
        self.root.protocol("WM_DELETE_WINDOW", self.emergency_stop)
        
        # Mendapatkan IP lokal agar bisa diakses dari HP
        hostname = socket.gethostname()
        try:
            ip_address = socket.gethostbyname(hostname)
        except:
            ip_address = "127.0.0.1"
            
        # GUI Elements
        self.lbl_title = tk.Label(root, text="ZEA is Standby", font=("Arial", 20, "bold"), bg="#1e1e1e", fg="#00ffcc")
        self.lbl_title.pack(pady=30)
        
        self.lbl_ip = tk.Label(root, text=f"Buka ini di Browser HP Anda:\nhttps://{ip_address}:5000", font=("Arial", 12), bg="#1e1e1e", fg="white")
        self.lbl_ip.pack(pady=5)

        self.btn_stop = tk.Button(root, text="EMERGENCY STOP", font=("Arial", 14, "bold"), bg="#ff4c4c", fg="white", 
                                  activebackground="#ff0000", command=self.emergency_stop, width=20, height=2)
        self.btn_stop.pack(pady=20)

        self.waiting_for_command = False
        self.is_running = True
        
        # Mulai worker Audio di background
        threading.Thread(target=audio_worker, daemon=True).start()
        
        # Thread Flask untuk Remote HP
        threading.Thread(target=run_flask, daemon=True).start()
        
        # Thread Mic Lokal untuk mendengar terus-menerus
        threading.Thread(target=self.local_listener, daemon=True).start()
        
        # Main loop timer untuk mengecek antrean suara (Queue)
        self.root.after(100, self.process_queue)
        
        print("\n===========================================")
        print("Sistem ZEA Berhasil Dimulai!")
        print(f"Akses Remote HP: https://{ip_address}:5000")
        print("CATATAN: Pastikan menggunakan HTTPS. Jika browser HP memberi")
        print("peringatan 'Not Secure/Tidak Aman', klik 'Advanced/Lanjutkan' saja.")
        print("Jika HP tidak bisa konek, jalankan 'open_firewall.bat' sebagai Admin.")
        print("===========================================\n")
        self.play_sound("wake")

    def play_sound(self, sound_key):
        # Memasukkan kunci suara ke antrean Audio agar tidak mem-freeze GUI
        audio_queue.put(sound_key)

    def emergency_stop(self):
        self.play_sound("exit")
        import time
        time.sleep(2)
        self.is_running = False
        self.root.destroy()
        os._exit(0)

    def execute_command(self, cmd):
        # --- Kata kunci SHUTDOWN (mati total) ---
        shutdown_verbs = ["shutdown", "shut down", "matikan", "mati", "turn off",
                          "power off", "shut", "shat down", "setdown", "shatdown",
                          "saddown", "sutdown", "shutdaun", "setdaun"]
        
        # --- Kata kunci LOCK (kunci layar) ---
        lock_verbs = ["lock", "look", "log", "blok", "kunci", "lok",
                      "luk", "loc", "locked", "block", "blokkir",
                      "blokir", "gembok", "tutup", "close"]
        
        # --- Kata kunci target PC ---
        pc_targets = ["pc", "computer", "komputer", "laptop", "leptop",
                      "visi", "this", "the pc", "dpc", "pisi", "pci",
                      "screen", "layar", "monitor"]
        
        # Cek apakah ada kata shutdown di command
        has_shutdown = any(verb in cmd for verb in shutdown_verbs)
        # Cek apakah ada kata lock di command
        has_lock = any(verb in cmd for verb in lock_verbs)
        # Cek apakah ada kata target PC di command
        has_target = any(target in cmd for target in pc_targets)
        # Cek apakah command hanya berisi kata kerja saja (tanpa target)
        is_bare_shutdown = cmd.strip() in shutdown_verbs
        is_bare_lock = cmd.strip() in lock_verbs
        
        # --- Kata kunci STOP/EXIT ---
        stop_words = ["keluar", "exit", "stop", "quit", "berhenti", 
                      "close zea", "tutup zea", "matikan zea"]
        has_stop = any(word in cmd for word in stop_words)
        
        if has_shutdown and (has_target or is_bare_shutdown):
            self.play_sound("shutdown")
            import time
            time.sleep(2)
            os.system("shutdown /s /t 3")
                
        elif has_lock and (has_target or is_bare_lock):
            self.play_sound("lock")
            import time
            time.sleep(2)
            os.system("rundll32.exe user32.dll,LockWorkStation")
                
        elif has_stop:
            self.emergency_stop()
            
        else:
            print(f"ZEA: Perintah tidak dikenali -> '{cmd}'")

    def process_queue(self):
        try:
            while not cmd_queue.empty():
                cmd = cmd_queue.get_nowait()
                
                if self.waiting_for_command:
                    self.execute_command(cmd)
                    self.waiting_for_command = False
                    self.lbl_title.config(text="ZEA is Standby", fg="#00ffcc")
                else:
                    aliases = ["zea", "sea", "zia", "dea", "dia", "jea", "z"]
                    is_called = False
                    
                    for alias in aliases:
                        if alias in cmd.split() or alias == cmd:
                            is_called = True
                            cmd = cmd.replace(alias, "").strip()
                            for a in aliases:
                                cmd = cmd.replace(a, "").strip()
                            break
                            
                    if is_called:
                        if cmd == "":
                            self.play_sound("wake")
                            self.waiting_for_command = True
                            self.lbl_title.config(text="ZEA is Listening...", fg="#ffcc00")
                        else:
                            self.execute_command(cmd)
                            self.lbl_title.config(text="ZEA is Standby", fg="#00ffcc")

        except queue.Empty:
            pass
        
        if self.is_running:
            self.root.after(100, self.process_queue)

    def local_listener(self):
        r = sr.Recognizer()
        fs = 44100
        duration = 5
        while self.is_running:
            try:
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()
                temp_wav = "temp_audio.wav"
                wav.write(temp_wav, fs, recording)
                
                with sr.AudioFile(temp_wav) as source:
                    audio = r.record(source)
                    
                command = r.recognize_google(audio, language="id-ID").lower()
                
                if command.strip() != "":
                    print(f"[Mic Lokal] Anda berkata: {command}")
                    cmd_queue.put(command)
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                pass
            except Exception:
                pass
            finally:
                if os.path.exists("temp_audio.wav"):
                    try:
                        os.remove("temp_audio.wav")
                    except:
                        pass

if __name__ == "__main__":
    root = tk.Tk()
    app_gui = ZeaAssistant(root)
    root.mainloop()
