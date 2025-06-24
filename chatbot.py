import os
from time import strftime
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pygame import mixer
import speech_recognition
import pyttsx3
from openai import OpenAI
import threading
client = OpenAI(
base_url="https://openrouter.ai/api/v1",
api_key="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",
)


class ChatBot:
    
    def __init__(self, root):
        self.root = root
        self.root.title('HelpBot')
        self.root.geometry('730x620+0+0')
        self.root.resizable(False, False)
        self.root.wm_iconbitmap('college_images/bg1.ico')
        self.root.bind('<Return>', self.enter_func)
        messagebox.showinfo('Note','It can only read english text',parent=self.root)
        

        main_frame = Frame(self.root, bd=4, bg='powder blue', width=610)
        main_frame.pack()

        img = Image.open('college_images/chat.jpg')
        img = img.resize((200, 70), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)

        self.title_label = Label(main_frame, bd=3, relief=RAISED, anchor='nw', width=730,
                                 image=self.photoimg, text='Chat Me', font=('arial', 30, 'bold'),
                                 bg='white', fg='green', compound=LEFT)
        self.title_label.pack(side=TOP)

        self.time_lbl = Label(self.title_label, font=('times new roman', 15, 'bold'),
                              bg='white', fg='gold', borderwidth=0, highlightthickness=0)
        self.time_lbl.place(x=390, y=15, width=120, height=45)
        self.update_time()

        back_btn = Button(self.title_label, text="Back", width=20, cursor='hand2',
                          font=('times new roman', 10, 'bold'), bg='red', fg='white',
                          activebackground="green", command=self.back)
        back_btn.place(x=550, y=25, height=25)

        self.scroll_y = ttk.Scrollbar(main_frame, orient='vertical')
        self.scroll_y.pack(side=RIGHT, fill=Y)

        self.text = Text(main_frame, width=65, height=20, bd=3, relief=RAISED,
                        font=('arial', 14), wrap=WORD, yscrollcommand=self.scroll_y.set,state='disabled')
        self.text.pack(side=LEFT, fill=BOTH, expand=True)

        self.scroll_y.config(command=self.text.yview)


        btn_frame = Frame(self.root, bd=4, bg='white', width=730)
        btn_frame.pack()

        type_label = Label(btn_frame, text='Type Something:', font=('arial', 14, 'bold'),
                           bg='white', fg='green', compound=LEFT)
        type_label.grid(row=0, column=0, padx=5, sticky=W)

        self.entry = ttk.Entry(btn_frame, width=40, font=('times new roman', 16, 'bold'))
        self.entry.grid(row=0, column=1, sticky=W, padx=5)

        self.send_btn = Button(btn_frame, text='Send>>', font=('arial', 13, 'bold'), width=8,
                               bg='green', fg='red', activebackground='yellow', activeforeground='blue',
                               cursor='hand2', command=self.send)
        self.send_btn.grid(row=0, column=2, padx=5)

        self.photoimg2 = ImageTk.PhotoImage(Image.open("assets/Clear.png").resize((48, 48), Image.Resampling.LANCZOS))
        self.clear_btn = Button(btn_frame, text='Clear', image=self.photoimg2, compound=LEFT,
                                font=('arial', 12, 'bold'), cursor='hand2', bd=0, bg='white',
                                activebackground='white', fg='yellow', activeforeground='green', command=self.clear)
        self.clear_btn.grid(row=1, column=0)

        self.photoimg3 = ImageTk.PhotoImage(Image.open("assets/mic.png").resize((48, 48), Image.Resampling.LANCZOS))
        self.speak_btn = Button(btn_frame, text='Speak', image=self.photoimg3, compound=LEFT,
                                font=('arial', 12, 'bold'), cursor='hand2', bd=0, bg='white',
                                activebackground='white', fg='cyan2', activeforeground='orange red', command=self.speak)
        self.speak_btn.grid(row=1, column=1)

        self.photoimg4 = ImageTk.PhotoImage(Image.open("assets/speaker.png").resize((40, 40), Image.Resampling.LANCZOS))
        self.read_btn = Button(btn_frame, text='Read All', image=self.photoimg4, compound=LEFT,
                               font=('arial', 12, 'bold'), cursor='hand2', bd=0, bg='white',
                               activebackground='white', fg='purple', activeforeground='pink',command=self.read)
        self.read_btn.place(x=600,y=35)

    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time)

    def back(self):
            self.root.destroy()

    def enter_func(self, event):
        self.send_btn.invoke()
        self.entry.delete(0, END)
       

    def send(self):
        user_input = self.entry.get().strip().lower()
        if user_input == '':
            messagebox.showerror('Error', 'Message must contain some content',parent=self.root)
            return
        # Disable send button and entry field
        self.send_btn.config(state=DISABLED, text="Loading...")
        self.entry.config(state=DISABLED)

        def process():
            self.text.config(state='normal')
            self.text.yview(END)
            self.text.insert(END, f"\n\t\tYou Typed: {self.entry.get()}")

            responses = {
                'hi': 'Hi',
                'how are you': 'I am fine. What about you?',
                'who made you?': 'I am a bot made by Dev, trained by Dev and LAMA.',
                'who created you?': 'I am a bot made by Dev, trained by Dev and LAMA.',
                "what's your name": 'My name is HelpBot. I always assist you.',
                'what is your name?': 'My name is HelpBot. I always assist you.',
                'what is your name': 'My name is HelpBot. I always assist you.'
            }

            if user_input in responses:
                response = responses[user_input]
            else:
                res = 'Sorry I didn\'t get it. It\'s out of my content, but I got your answer from server.\n'
                response = self.ask_openai(user_input)
                response = res + response


            engine = pyttsx3.init()
            engine.setProperty('rate', 200)
            engine.setProperty('volume', 1.0)

            # Get voices and try to select Hindi if needed
            voices = engine.getProperty('voices')
            engine.say(response)
            engine.runAndWait()

            self.entry.config(state=NORMAL)
            self.entry.delete(0, END)
            self.text.insert(END, f'\n\n Bot : {response}')
            self.text.config(state='disabled')

            # Re-enable button and reset text
            self.send_btn.config(state=NORMAL, text="Send>>")
            # Start the thread to process in background
        threading.Thread(target=process).start()




    def clear(self):
        self.text.config(state='normal')
        self.entry.delete(0, END)
        self.text.delete(1.0, END)
        self.text.config(state='disabled')

    def speak(self):
        mixer.init()
        mixer.music.load('assets/beep.mp3')
        mixer.music.play()
        sr = speech_recognition.Recognizer()
        with speech_recognition.Microphone() as m:
            try:
                sr.adjust_for_ambient_noise(m, duration=0.2)
                audio = sr.listen(m)
                text = sr.recognize_google(audio)
                self.entry.insert(0, text)
            except Exception as e:
                messagebox.showerror('Speech Recognition Error', f'Sorry, your speech was not recognized: {str(e)}', parent=self.root)

    def read(self):
        engine = pyttsx3.init()
        engine.setProperty('rate',180)  # Increase speech rate (default ~200)
        engine.setProperty('volume', 1.0)  # Max volume (range: 0.0 to 1.0)
        voices = engine.getProperty('voices')
        engine.setProperty('voice',voices[0].id)
        engine.say('So far we have talked about:')
        engine.say(self.text.get(1.0, END))

        engine.runAndWait()

    def ask_openai(self, prompt):
        try:
            completion = client.chat.completions.create(
                extra_headers={
                    
                    "X-Title": "HelpBot"
                },
                model="meta-llama/llama-3.3-70b-instruct:free",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenRouter error: {str(e)}"


if __name__ == '__main__':
    root = Tk()
    obj = ChatBot(root)
    root.mainloop()
