import speech_recognition as sr
import os
import pyttsx3
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import threading
import queue
import tkinter as tk
from flask import Flask, request, jsonify, render_template_string
import logging
import socket

# Matikan log Flask agar terminal lebih bersih
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
cmd_queue = queue.Queue()
tts_queue = queue.Queue()

# Thread khusus untuk Text-to-Speech agar tidak bikin GUI ngelag/freeze
def tts_worker():
    # CoInitialize diperlukan di Windows saat menggunakan pyttsx3 di thread terpisah
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except ImportError:
        pass
        
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if "Zira" in voice.name or "female" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
            
    while True:
        text = tts_queue.get()
        if text is None:
            break
        print(f"ZEA: {text}")
        engine.say(text)
        engine.runAndWait()

# Template HTML untuk Web Remote via HP
WEB_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ZEA Remote</title>
    <style>
        body { background-color: #121212; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding-top: 50px; }
        button { background-color: #bb86fc; color: #000; border: none; padding: 25px 50px; font-size: 24px; border-radius: 50px; margin-top: 50px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(187, 134, 252, 0.4); transition: 0.3s; }
        button:active { transform: scale(0.95); }
        #status { margin-top: 40px; font-size: 20px; color: #aaa; }
        .header { font-size: 28px; font-weight: bold; margin-bottom: 10px; color: #bb86fc; }
        .warning { font-size: 14px; color: #ff5252; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="header">ZEA Remote Control</div>
    <p>Gunakan HP Anda sebagai Mikrofon</p>
    <button id="micBtn">TAP TO SPEAK</button>
    <div id="status">Status: Standby</div>
    <div class="warning">Catatan: Jika tombol tidak merespon, pastikan Anda menggunakan HTTPS dan telah mengizinkan akses mikrofon di browser.</div>
    <script>
        const btn = document.getElementById('micBtn');
        const status = document.getElementById('status');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            status.innerText = "Browser tidak mendukung Speech Recognition.";
        } else {
            const recognition = new SpeechRecognition();
            recognition.lang = 'id-ID'; // Menggunakan basis bahasa indonesia
            recognition.interimResults = false;
            
            btn.addEventListener('click', () => {
                try {
                    recognition.start();
                    status.innerText = "Mendengarkan...";
                    btn.style.backgroundColor = "#ff5252";
                    btn.innerText = "LISTENING...";
                } catch(e) {
                    status.innerText = "Error: " + e.message;
                }
            });
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                status.innerText = "Anda berkata: " + transcript;
                btn.style.backgroundColor = "#bb86fc";
                btn.innerText = "TAP TO SPEAK";
                
                fetch('/api/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: transcript})
                }).catch(e => {
                    status.innerText = "Gagal mengirim: " + e.message;
                });
            };
            
            recognition.onerror = (e) => {
                status.innerText = "Error: " + e.error;
                btn.style.backgroundColor = "#bb86fc";
                btn.innerText = "TAP TO SPEAK";
            };
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(WEB_HTML)

@app.route('/api/command', methods=['POST'])
def receive_command():
    data = request.json
    command = data.get("command", "").lower()
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
        
        # Mulai worker TTS di background
        threading.Thread(target=tts_worker, daemon=True).start()
        
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
        print("===========================================\n")
        self.speak("Sistem ZEA sudah aktif. Siap menerima perintah.")

    def speak(self, text):
        # Memasukkan teks ke antrean TTS agar tidak mem-freeze GUI
        tts_queue.put(text)

    def emergency_stop(self):
        self.speak("Emergency stop diaktifkan. Mematikan sistem ZEA.")
        self.is_running = False
        self.root.destroy()
        os._exit(0)

    def execute_command(self, cmd):
        if "lock" in cmd or "look" in cmd or "log" in cmd or "blok" in cmd:
            if "pc" in cmd or "visi" in cmd or "this" in cmd or "the pc" in cmd or "dpc" in cmd:
                self.speak("As your command sir")
                # shutdown /s (mati total), /t 3 (dalam 3 detik)
                os.system("shutdown /s /t 3")
                
        elif "keluar" in cmd or "exit" in cmd or "stop" in cmd:
            self.emergency_stop()
            
        else:
            self.speak("ZEA tidak mengenali perintah tersebut sir.")

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
                            self.speak("What's your command sir?")
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
