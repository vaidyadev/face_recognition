import os
import tempfile
import threading
import time
from gtts import gTTS
from pygame import mixer
import speech_recognition

_speech_request_id = 0
_speech_lock = threading.Lock()

def stop_speech():
    global _speech_request_id
    try:
        with _speech_lock:
            _speech_request_id += 1
        mixer.init()
        if mixer.music.get_busy():
            mixer.music.stop()
            # Unload happens in the monitoring thread usually, but stopping triggers it
    except Exception as e:
        print(f"Stop Error: {e}")

def speak_text_gtts(text, lang_code, root, on_finish=None):
    global _speech_request_id
    with _speech_lock:
        req_id = _speech_request_id

    def run_thread():
        try:
            # High latency operation (Network)
            tts = gTTS(text=text, lang=lang_code)
            
            with _speech_lock:
                if req_id != _speech_request_id:
                    return

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                tts.save(temp_audio.name)
                temp_path = temp_audio.name

            with _speech_lock:
                if req_id != _speech_request_id:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return

            # Playback
            mixer.init()
            mixer.music.load(temp_path)
            mixer.music.play()

            # Wait loop
            while mixer.music.get_busy():
                 with _speech_lock:
                     if req_id != _speech_request_id:
                         mixer.music.stop()
                         break
                 time.sleep(0.1)
            
            mixer.music.unload()
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if on_finish:
                with _speech_lock:
                    if req_id == _speech_request_id:
                        root.after(0, on_finish)
                
        except Exception as e:
            print(f"Speech Thread Error: {e}")
            # We can show error, but on main thread
            with _speech_lock:
                if req_id == _speech_request_id:
                    root.after(0, lambda: show_error(root, lang_code, e))
                    if on_finish:
                         root.after(0, on_finish)

    threading.Thread(target=run_thread, daemon=True).start()

def show_error(root, lang_code, e):
    from tkinter import messagebox
    messagebox.showerror("Speech Error", f"Could not play audio for '{lang_code}':\n{e}", parent=root)


def listen_speech():
    mixer.init()
    if os.path.exists('assets/beep.mp3'):
        mixer.music.load('assets/beep.mp3')
        mixer.music.play()
    
    sr = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as m:
        sr.adjust_for_ambient_noise(m, duration=0.2)
        audio = sr.listen(m)
        text = sr.recognize_google(audio)
        return text
