import os
import tempfile
import threading
from gtts import gTTS
from pygame import mixer
import speech_recognition

def stop_speech():
    try:
        mixer.init()
        if mixer.music.get_busy():
            mixer.music.stop()
            # Unload happens in the monitoring thread usually, but stopping triggers it
    except Exception as e:
        print(f"Stop Error: {e}")

def speak_text_gtts(text, lang_code, root, on_finish=None):
    def run_thread():
        try:
            # High latency operation (Network)
            tts = gTTS(text=text, lang=lang_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                tts.save(temp_audio.name)
                temp_path = temp_audio.name

            # Playback
            mixer.init()
            mixer.music.load(temp_path)
            mixer.music.play()

            # Wait loop
            while mixer.music.get_busy():
                 # Check if we should stop? logic is handled by mixer.stop() called externally
                 # which causes get_busy to return False
                 pass 
            
            mixer.music.unload()
            os.remove(temp_path)
            
            if on_finish:
                root.after(0, on_finish)
                
        except Exception as e:
            print(f"Speech Thread Error: {e}")
            # We can show error, but on main thread
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
