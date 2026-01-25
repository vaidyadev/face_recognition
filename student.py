from time import strftime
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import mysql.connector
import cv2
from datetime import datetime
from tkcalendar import DateEntry
from tkcalendar import Calendar
import calendar
import datetime
import tkinter as tk
from tkinter import ttk
import numpy as np
import os

class DatePickerDialog:
    def __init__(self, parent, initial_date, callback):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Date")
        self.dialog.transient(parent)
        try:
            self.dialog.iconbitmap('college_images\\bg1.ico')
        except:
            pass
        self.dialog.grab_set()
        
        self.initial_date = initial_date
        self.callback = callback
        self.selected_date = initial_date
        self.current_display_date = initial_date 
        
        self.setup_ui()
        
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        

    def setup_ui(self):
        nav_frame = ttk.Frame(self.dialog)
        nav_frame.pack(pady=5)
        months = list(calendar.month_name)[1:]
        self.month_var = tk.StringVar()
        self.month_combobox = ttk.Combobox(nav_frame, textvariable=self.month_var, values=months, state='readonly', width=10)
        self.month_combobox.pack(side=tk.LEFT, padx=5)
        self.month_combobox.bind("<<ComboboxSelected>>", self.change_month)
        current_year = datetime.date.today().year
        years = list(range(1990, current_year + 1))
        self.year_var = tk.StringVar()
        self.year_combobox = ttk.Combobox(nav_frame, textvariable=self.year_var, values=years, state='readonly', width=6)
        self.year_combobox.pack(side=tk.LEFT, padx=5)
        self.year_combobox.bind("<<ComboboxSelected>>", self.change_year)
        ttk.Button(nav_frame, text="◀", command=self.prev_month).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="▶", command=self.next_month).pack(side=tk.LEFT, padx=5)
        self.calendar_frame = ttk.Frame(self.dialog)
        self.calendar_frame.pack(padx=10, pady=5)
        self.update_calendar()
        ttk.Button(self.dialog, text="Select", command=self.on_select, style='DialogButton.TButton').pack(pady=10)
    
    def change_month(self, event):
        selected_month = list(calendar.month_name).index(self.month_var.get())
        self.current_display_date = self.current_display_date.replace(month=selected_month)
        self.update_calendar()

    def change_year(self, event):
        selected_year = int(self.year_var.get())
        self.current_display_date = self.current_display_date.replace(year=selected_year)
        self.update_calendar()

    def update_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            label = ttk.Label(self.calendar_frame, text=day, font=('Segoe UI', 9, 'bold'),
                              background='#dddddd', foreground='black')
            label.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
        cal = calendar.monthcalendar(self.current_display_date.year, self.current_display_date.month)
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0: continue
                date_obj = datetime.date(self.current_display_date.year, self.current_display_date.month, day)
                today = datetime.date.today()
                is_future = date_obj > today
                bg_color = 'white'
                fg_color = 'black'
                if date_obj == datetime.date.today():
                    bg_color = '#e74c3c'
                    fg_color = 'white'
                elif date_obj == self.selected_date:
                    bg_color = '#3498db'
                    fg_color = 'white'
                btn = tk.Button(self.calendar_frame, text=str(day), bg=bg_color, fg=fg_color, font=('Segoe UI', 9),
                relief=tk.FLAT, state=tk.DISABLED if is_future else tk.NORMAL, command=lambda d=date_obj: self.set_selected_date(d))
                btn.grid(row=week_num, column=day_num, sticky='nsew', padx=1, pady=1)
        for i in range(7): self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(len(cal) + 1): self.calendar_frame.rowconfigure(i, weight=1)
        self.month_var.set(self.current_display_date.strftime('%B'))
        self.year_var.set(str(self.current_display_date.year))

    def set_selected_date(self, date_obj):
        self.selected_date = date_obj
        self.update_calendar()

    def prev_month(self):
        if self.current_display_date.month == 1:
            self.current_display_date = self.current_display_date.replace(year=self.current_display_date.year - 1, month=12)
        else:
            self.current_display_date = self.current_display_date.replace(month=self.current_display_date.month - 1)
        self.update_calendar()

    def next_month(self):
        today = datetime.date.today()
        next_year = self.current_display_date.year
        next_month = self.current_display_date.month + 1
        if next_month == 13:
            next_month = 1
            next_year += 1
        if datetime.date(next_year, next_month, 1) <= today:
            self.current_display_date = self.current_display_date.replace(year=next_year, month=next_month)
            self.update_calendar()

    def on_select(self):
        self.callback(self.selected_date)
        self.dialog.destroy()

class students:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(False, False)
        try:
            self.root.wm_iconbitmap('college_images\\bg1.ico')
        except:
            pass

        self.var_dep=StringVar()
        self.var_course=StringVar()
        self.var_year=StringVar()
        self.var_semester=StringVar()
        self.va_std_id=StringVar()
        self.var_std_name=StringVar()
        self.var_div=StringVar()
        self.var_roll=StringVar()
        self.var_gender=StringVar()
        self.var_dob=StringVar()
        self.var_email=StringVar()
        self.var_phone=StringVar()
        self.var_address=StringVar()
        self.var_teacher=StringVar()
        self.var_search_combo=StringVar()
        self.var_search_entry=StringVar()
        self.var_telegram_id = StringVar()
        self.active_filters = {
            "Gender": [],
            "Department": [],
            "Year": []
        }


        self.dep_course_map = {
        "Computer": ["BCA", "B.Tech", "MCA", "M.Tech"],
        "IT": ["B.Sc IT", "M.Sc IT",],
        "Civil": ["Diploma", "B.E", "M.E"],
        "Mechenical": ["Diploma", "B.E", "M.E"]
        }
        self.course_sem_map = {
        "BCA": 8, "B.Sc IT": 6, "Diploma": 6, "B.Tech": 8, "B.E": 8,
        "MCA": 2, "M.Sc IT": 4, "M.Tech": 4, "M.E": 4
        }

        try:
            img = Image.open("college_images\\face-recognition.png")
            img = img.resize((450, 130), Image.Resampling.LANCZOS)
            self.photoimg = ImageTk.PhotoImage(img)
            f_lbl = Label(self.root, image=self.photoimg)
            f_lbl.place(x=0, y=0, width=450, height=130)

            img1 = Image.open("college_images\\smart-attendance.jpg")
            img1 = img1.resize((450, 130), Image.Resampling.LANCZOS)
            self.photoimg1 = ImageTk.PhotoImage(img1)
            f_lbl1 = Label(self.root, image=self.photoimg1)
            f_lbl1.place(x=450, y=0, width=450, height=130)

            img2 = Image.open("college_images\\12.jpg")
            img2 = img2.resize((460, 130), Image.Resampling.LANCZOS)
            self.photoimg2 = ImageTk.PhotoImage(img2)
            f_lbl2 = Label(self.root, image=self.photoimg2)
            f_lbl2.place(x=900, y=0, width=460, height=130)

            img3 = Image.open("college_images\\wp2551980.jpg")
            img3 = img3.resize((1360, 560), Image.Resampling.LANCZOS)
            self.photoimg3 = ImageTk.PhotoImage(img3)
            bg_img = Label(self.root, image=self.photoimg3)
            bg_img.place(x=0, y=131, width=1360, height=560)
        except Exception as e:
            bg_img = Frame(self.root, bg='white')
            bg_img.place(x=0, y=131, width=1360, height=560)

        self.title_lbl = Label(bg_img, text='STUDENT MANAGEMENT SYSTEM', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(x=0, y=0, width=1360, height=45)

        back_btn=Button(self.title_lbl,text="Back",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), bg='red', fg='white',activebackground="green",command=self.back)
        back_btn.place(x=1150,y=10,height=25)

        self.time_lbl = Label(bg_img, font=('times new roman', 15, 'bold'), bg='white', fg='red',borderwidth=0,highlightthickness=0)
        self.time_lbl.place(x=0, y=0, width=120, height=45)
        self.update_time() 

        main_frame=Frame(bg_img,bd=2)
        main_frame.place(x=10,y=50,width=1330,height=500)

        left_frame=LabelFrame(main_frame,bd=2,bg='white',relief=RIDGE,text='Students Details',font=('times new roman', 12, 'bold'))
        left_frame.place(x=10,y=10,width=645,height=480)
        
        try:
            img_left = Image.open("college_images\\AdobeStock_303989091.jpeg")
            img_left = img_left.resize((635, 130), Image.Resampling.LANCZOS)
            self.left_photoimg = ImageTk.PhotoImage(img_left)
            f_lbl = Label(left_frame, image=self.left_photoimg)
            f_lbl.place(x=5, y=0, width=635, height=80)
        except:
            pass

        current_course_frame=LabelFrame(left_frame,bd=2,bg='white',relief=RIDGE,text='Current Course Information',font=('times new roman', 12, 'bold'))
        current_course_frame.place(x=5,y=85,width=635,height=90)
        dep_label=Label(current_course_frame,text='Department',font=('times new roman', 12, 'bold'),bg='white')
        dep_label.grid(row=0,column=0,padx=5,sticky=W)
        dep_combo = ttk.Combobox(current_course_frame,font=('times new roman', 12, 'bold'),width=17,textvariable=self.var_dep,state='readonly')
        dep_combo['values'] = list(self.dep_course_map.keys())
        dep_combo.set("Select Department")
        dep_combo.grid(row=0, column=1, padx=2, pady=5, sticky=W)
        dep_combo.bind("<<ComboboxSelected>>", self.update_course)

        course_label=Label(current_course_frame,text='          Course',font=('times new roman', 12, 'bold'),bg='white')
        course_label.grid(row=0,column=2,padx=5,sticky=W)
        self.course_combo = ttk.Combobox(current_course_frame,font=('times new roman', 12, 'bold'),textvariable=self.var_course,width=17,state='readonly')
        self.course_combo.set("Select Course")
        self.course_combo.grid(row=0, column=3, padx=5, pady=5, sticky=W)
        self.course_combo.bind("<<ComboboxSelected>>", self.update_semester)

        year_label=Label(current_course_frame,text='Year',font=('times new roman', 12, 'bold'),bg='white')
        year_label.grid(row=1,column=0,padx=5,sticky=W)
        current_year = datetime.datetime.now().year
        years = [f"{y}-{y+1}" for y in range(current_year-1, current_year+4)]
        year_combo = ttk.Combobox(current_course_frame,font=('times new roman', 12, 'bold'),textvariable=self.var_year,width=17,state='readonly')
        year_combo['values'] = years
        year_combo.set("Select Year")
        year_combo.grid(row=1, column=1, padx=2, pady=5, sticky=W)

        semester_label=Label(current_course_frame,text='           Semester',font=('times new roman', 12, 'bold'),bg='white')
        semester_label.grid(row=1,column=2,padx=2,sticky=W)
        self.semester_combo = ttk.Combobox(current_course_frame,font=('times new roman', 12, 'bold'),textvariable=self.var_semester,width=17,state='readonly')
        self.semester_combo.set("Select Semester")
        self.semester_combo.grid(row=1, column=3, padx=5, pady=5, sticky=W)

        class_student_frame=LabelFrame(left_frame,bd=2,bg='white',relief=RIDGE,text='Class Student Information',font=('times new roman', 12, 'bold'))
        class_student_frame.place(x=5,y=180,width=635,height=275)
        
        student_id_label=Label(class_student_frame,text='StudentId :',font=('times new roman', 12, 'bold'),bg='white')
        student_id_label.grid(row=0,column=0,padx=5,sticky=W)
        studentid_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.va_std_id)
        studentid_entry.grid(row=0,column=1,padx=5,pady=3,sticky=W)
        
        studentname_label=Label(class_student_frame,text='StudentName :',font=('times new roman', 12, 'bold'),bg='white')
        studentname_label.grid(row=0,column=2,padx=5,sticky=W)
        studentname_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_std_name)
        studentname_entry.grid(row=0,column=3,padx=5,pady=3,sticky=W)
        
        class_div_label=Label(class_student_frame,text='Class Division :',font=('times new roman', 12, 'bold'),bg='white')
        class_div_label.grid(row=1,column=0,padx=5,sticky=W)
        div_combo=ttk.Combobox(class_student_frame,font=('times new roman', 12, 'bold'),textvariable=self.var_div,width=18,state='read')
        div_combo['values']=('A','B','C','D')
        div_combo.set('Select Division')
        div_combo.grid(row=1,column=1,padx=5,pady=5,sticky=W)
        
        rollno_label=Label(class_student_frame,text='Roll NO :',font=('times new roman', 12, 'bold'),bg='white')
        rollno_label.grid(row=1,column=2,padx=5,sticky=W)
        rollno_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_roll)
        rollno_entry.grid(row=1,column=3,padx=5,pady=3,sticky=W)
        
        gender_label=Label(class_student_frame,text='Gender :',font=('times new roman', 12, 'bold'),bg='white')
        gender_label.grid(row=2,column=0,padx=5,sticky=W)
        gender_combo=ttk.Combobox(class_student_frame,font=('times new roman', 12, 'bold'),textvariable=self.var_gender,width=18,state='read')
        gender_combo['values']=("Male",'Female','Other')
        gender_combo.set('Select Gender')
        gender_combo.grid(row=2,column=1,padx=5,pady=5,sticky=W)

        dob_label = Label(class_student_frame,text='DOB (DD/MM/YYYY):',font=('times new roman', 10, 'bold'),bg='white',)
        dob_label.place(x=310, y=70) 
        dob_entry = ttk.Entry(class_student_frame,width=18,font=('times new roman', 12, 'bold'),textvariable=self.var_dob,)
        dob_entry.place(x=437, y=70)
        dob_btn = Button(class_student_frame,text="📅",font=("Segoe UI Emoji", 10),width=3,bg='red',fg='blue',activebackground='green',activeforeground='yellow',cursor="hand2",command=self.open_dob_calendar)
        dob_btn.place(x=595, y=65)

        email_label=Label(class_student_frame,text='Email :',font=('times new roman', 12, 'bold'),bg='white')
        email_label.grid(row=3,column=0,padx=5,sticky=W)
        email_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_email)
        email_entry.grid(row=3,column=1,padx=5,pady=3,sticky=W)
        
        phono_label=Label(class_student_frame,text='Phone NO :',font=('times new roman', 12, 'bold'),bg='white')
        phono_label.grid(row=3,column=2,padx=5,sticky=W)
        phono_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_phone)
        phono_entry.grid(row=3,column=3,padx=5,pady=3,sticky=W)

        telegram_label = Label(
            class_student_frame,
            text='Telegram ID/Username :',
            font=('times new roman', 10, 'bold'),
            bg='white'
        )
        telegram_label.grid(row=6, column=2, padx=5, sticky=W)

        telegram_entry = ttk.Entry(
            class_student_frame,
            width=20,
            font=('times new roman', 12, 'bold'),
            textvariable=self.var_telegram_id
        )
        telegram_entry.grid(row=6, column=3, padx=5, pady=0, sticky=W)

        
        address_label=Label(class_student_frame,text='Address(City) :',font=('times new roman', 12, 'bold'),bg='white')
        address_label.grid(row=4,column=0,padx=5,sticky=W)
        address_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_address)
        address_entry.grid(row=4,column=1,padx=5,pady=3,sticky=W)
        
        teacher_label=Label(class_student_frame,text='Teacher Name :',font=('times new roman', 12, 'bold'),bg='white')
        teacher_label.grid(row=4,column=2,padx=5,sticky=W)
        teacher_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_teacher)
        teacher_entry.grid(row=4,column=3,padx=5,pady=3,sticky=W)
        
        self.var_radio1=StringVar()
        radiobutton1=ttk.Radiobutton(class_student_frame,variable=self.var_radio1,text='Have Photo Sample',value='yes')
        radiobutton1.grid(row=6,column=0,pady=(0,7))
        radiobutton2=ttk.Radiobutton(class_student_frame,variable=self.var_radio1,text='No Photo Sample',value='no')
        radiobutton2.grid(row=6,column=1,pady=(0,7))

        btn_frame=Frame(class_student_frame,bd=2,relief=RIDGE,bg='white')
        btn_frame.place(x=0,y=190,width=635,height=32)

        save_btn=Button(btn_frame,text="Save",width=22,cursor='hand2',height=2,font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.add_data)
        save_btn.grid(row=0,column=0)
        update_btn=Button(btn_frame,text="Update",width=22,cursor='hand2',height=2,font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.update_data)
        update_btn.grid(row=0,column=1)
        delete_btn=Button(btn_frame,text="Delete",width=22,cursor='hand2',height=2,font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.delete_data)
        delete_btn.grid(row=0,column=2)
        reset_btn=Button(btn_frame,text="Reset",width=20,cursor='hand2',height=2,font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.reset_data)
        reset_btn.grid(row=0,column=3)

        btn_frame1=Frame(class_student_frame,bd=2,relief=RIDGE,bg='white')
        btn_frame1.place(x=0,y=225,width=635,height=35)

        take_photo_btn=Button(btn_frame1,text="Take Photo Sample",width=45,height=2,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.photo_sample,padx=(1.9))
        take_photo_btn.grid(row=1,column=0)

        update_photo_btn=Button(btn_frame1,text="Update Photo Sample",height=2,width=45,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.update_photosample)
        update_photo_btn.grid(row=1,column=1)

        right_frame=LabelFrame(main_frame,bd=2,bg='white',relief=RIDGE,text='Students Details',font=('times new roman', 12, 'bold'))
        right_frame.place(x=665,y=10,width=645,height=480)
        
        try:
            img_right = Image.open("college_images\\student.jpg")
            img_right = img_right.resize((635, 130), Image.Resampling.LANCZOS)
            self.right_photoimg = ImageTk.PhotoImage(img_right)
            f_lbl3 = Label(right_frame, image=self.right_photoimg)
            f_lbl3.place(x=5, y=0, width=635, height=80)
        except:
            pass

        search_frame=LabelFrame(right_frame,bd=2,bg='white',relief=RIDGE,text='Search System',font=('times new roman', 12, 'bold'))
        search_frame.place(x=5,y=85,width=635,height=55)
        search_label=Label(search_frame,text='Search By :',font=('times new roman', 12, 'bold'),bg='red',fg='white')
        search_label.grid(row=0,column=0,padx=5,sticky=W)

        search_combo=ttk.Combobox(search_frame,font=('times new roman', 12, 'bold'),width=12,state='read',textvariable=self.var_search_combo)
        search_combo['values'] = ('Student ID','Roll No','Student Name','Department','Phone No','Telegram ID','Gender','Year')
        search_combo.current(0)
        search_combo.set("Select Option")
        search_combo.grid(row=0,column=1,padx=2,sticky=W)

        search_entry = ttk.Entry(search_frame,width=18,font=('times new roman', 12, 'bold'),textvariable=self.var_search_entry)
        search_entry.grid(row=0, column=2, padx=2, pady=3, sticky=W)
        search_entry.bind("<KeyRelease>", self.live_search)

        reset_btn = Button(search_frame,text="Reset",width=10,cursor='hand2',font=('times new roman', 10, 'bold'),bg='green',fg='white',activebackground="red",activeforeground='green',command=self.reset_search)
        reset_btn.grid(row=0, column=3, padx=2)
        showall_btn=Button(search_frame,text="Refresh",width=10,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=lambda: self.refresh_animation(self.fetch_data))
        showall_btn.grid(row=0,column=4,padx=2)
        Button(search_frame,text="Filter",font=("times new roman", 10, "bold"),bg="purple",fg="white",cursor='hand2',activebackground="#5d57b4",activeforeground='black',width=10,command=self.open_student_filter).grid(row=0,column=5,padx=2)

        table_frame=Frame(right_frame,bd=2,bg='white',relief=RIDGE)
        table_frame.place(x=5,y=140,width=635,height=310)

        scroll_x=ttk.Scrollbar(table_frame,orient=HORIZONTAL)
        scroll_y=ttk.Scrollbar(table_frame,orient=VERTICAL)
        
        self.student_table=ttk.Treeview(table_frame,column=('dep','course','year','sem','id','name','div','roll','gender','dob','email','phone','address','teacher','photo','telegram'),xscrollcommand=scroll_x.set,yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM,fill=X)
        scroll_y.pack(side=RIGHT,fill=Y)
        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        self.student_table.heading('dep',text='Department')
        self.student_table.heading('course',text='Course')
        self.student_table.heading('year',text='Year')
        self.student_table.heading('sem',text='Semester')
        self.student_table.heading('id',text='StudentId')
        self.student_table.heading('name',text='StudentName')
        self.student_table.heading('div',text='Division')
        self.student_table.heading('roll',text='Roll No')
        self.student_table.heading('gender',text='Gender')   
        self.student_table.heading('dob',text='DOB')
        self.student_table.heading('email',text='Email')
        self.student_table.heading('phone',text='Phone NO')
        self.student_table.heading('address',text='Address')
        self.student_table.heading('teacher',text='Teacher')
        self.student_table.heading('photo',text='PhotoSampleStatus')
        self.student_table.heading('telegram', text='Telegram ID')

        self.student_table['show']='headings'
        self.student_table.column('course',width=100)
        self.student_table.column('year',width=100)
        self.student_table.column('sem',width=100)
        self.student_table.column('id',width=100)
        self.student_table.column('name',width=100)
        self.student_table.column('div',width=100)
        self.student_table.column('roll',width=100)
        self.student_table.column('gender',width=100)
        self.student_table.column('dob',width=100)
        self.student_table.column('email',width=150)
        self.student_table.column('phone',width=100)
        self.student_table.column('address',width=100)
        self.student_table.column('teacher',width=100)
        self.student_table.column('photo',width=150)
        self.student_table.column('dep',width=100)
        self.student_table.column('telegram', width=120)
        
        self.student_table.pack(fill=BOTH, expand=1)

        self.student_columns = {
            'dep': str, 'course': str, 'year': str, 'sem': str,
            'id': int, 'name': str, 'div': str, 'roll': int,
            'gender': str, 'dob': 'date', 'email': str,
            'phone': int, 'telegram': int,   # 👈 ADD
            'address': str, 'teacher': str, 'photo': str
        }


        for col in self.student_columns:
            self.student_table.heading(col,text=col.title(),command=lambda c=col: self.student_sort(c, False))
        self.student_table.bind('<ButtonRelease>', self.get_cursor)
        self.fetch_data()
        self.root.bind("<F5>", lambda e: self.fetch_data()) 
        self.root.after(60000, self.fetch_data)

    def add_data(self):
        email = self.var_email.get()
        if self.var_dep.get()=='Select Department' or self.var_std_name.get()=='' or self.va_std_id.get()=='' or self.var_course.get()=='Select Course' or self.var_year.get()=='Select Year' or self.var_semester.get()=='Select Semester' or self.var_div.get()=='Select Division' or self.var_gender.get()=='Select Gender' or self.var_roll.get()==''or self.var_email.get()=='' or self.var_dob.get()==''or self.var_phone.get()=='' or self.var_address.get()=='' or self.var_teacher.get()=='' or self.var_radio1.get()=='' or self.var_telegram_id.get()=='':
            messagebox.showerror("Error","All Fields are required",parent=self.root)
        elif not email.endswith("@gmail.com") or not any(char.isdigit() for char in email):
            messagebox.showerror("Error", "Please enter a valid Gmail address with at least one digit.",parent=self.root)
        elif len(self.var_phone.get())!=10 or not self.var_phone.get().isdigit():
            messagebox.showerror("Error","Please enter a valid Phone No with 10 digits",parent=self.root)
        elif self.var_roll.get().isdigit()==False:
            messagebox.showerror("Error","Please enter a valid Roll Number only digits are allowed",parent=self.root)
        elif not self.va_std_id.get().isdigit:
            messagebox.showerror("Error","Please enter a valid Student Id only digits are allowed",parent=self.root)

        else:
            try:
                conn=mysql.connector.connect(host='localhost',port=3307,username='root',password='1582',database='face_recognizer')
                my_cursor=conn.cursor()
                my_cursor.execute(
                'insert into student values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(
                self.var_dep.get(),
                self.var_course.get(),
                self.var_year.get(),
                self.var_semester.get(),
                self.va_std_id.get(),
                self.var_std_name.get(),
                self.var_div.get(),
                self.var_roll.get(),
                self.var_gender.get(),
                self.var_dob.get(),
                self.var_email.get(),
                self.var_phone.get(),
                self.var_telegram_id.get(),   
                self.var_address.get(),
                self.var_teacher.get(),
                self.var_radio1.get()
            ))

                conn.commit()
                self.fetch_data()
                conn.close()
                messagebox.showinfo("Succes",'Student details has been added Succesfully',parent=self.root)
            except Exception as e:
                messagebox.showerror('Error',f'Student details failed to be added due to {str(e)}',parent=self.root)

    def refresh_animation(self, reload_callback):
        # Disable UI briefly (optional visual effect)
        self.root.config(cursor="watch")
        self.root.update_idletasks()

        # Clear table instantly (Chrome-like disappear)
        if hasattr(self, 'attendence_table'):
            self.attendence_table.delete(*self.attendence_table.get_children())
        if hasattr(self, 'student_table'):
            self.student_table.delete(*self.student_table.get_children())

        # Small delay then reload
        self.root.after(400, lambda: self._finish_refresh(reload_callback))

    def _finish_refresh(self, reload_callback):
        reload_callback()
        self.root.config(cursor="")

    def fetch_data(self):
        conn = mysql.connector.connect(host='localhost',port=3307, username='root', password='1582', database='face_recognizer')
        my_cursor = conn.cursor()  
        my_cursor.execute('select * from student')
        data = my_cursor.fetchall()
        if(len(data) != 0):
            self.student_table.delete(*self.student_table.get_children())
            for i in data:
                self.student_table.insert('', END, values=i)
            conn.commit()  
        conn.close() 

    def update_course(self, event=None):
        dep = self.var_dep.get()
        courses = self.dep_course_map.get(dep, [])
        self.course_combo['values'] = courses
        self.course_combo.set("Select Course")
        self.semester_combo.set("Select Semester")

    def update_semester(self, event=None):
        course = self.var_course.get()
        max_sem = self.course_sem_map.get(course)
        if max_sem:
            sem_list = [f"Semester-{i}" for i in range(1, max_sem + 1)]
            self.semester_combo['values'] = sem_list
            self.semester_combo.set("Semester-1")

    def open_dob_calendar(self):
        try:
            initial_date = datetime.datetime.strptime(self.var_dob.get(), "%d/%m/%Y").date()
        except:
            initial_date = datetime.date.today()
        def set_dob(selected_date):
            self.var_dob.set(selected_date.strftime("%d/%m/%Y"))
        DatePickerDialog(self.root, initial_date, set_dob)

    def get_cursor(self, event=None):
        selected = self.student_table.focus()
        if not selected: return
        data = self.student_table.item(selected).get('values', [])
        if not data or len(data) < 15: return
        self.var_dep.set(data[0])
        self.var_course.set(data[1])
        self.var_year.set(data[2])
        self.var_semester.set(data[3])
        self.va_std_id.set(data[4])
        self.var_std_name.set(data[5])
        self.var_div.set(data[6])
        self.var_roll.set(data[7])
        self.var_gender.set(data[8])
        self.var_dob.set(data[9])
        self.var_email.set(data[10])
        self.var_phone.set(data[11])
        self.var_address.set(data[12])
        self.var_teacher.set(data[13])
        self.var_radio1.set(data[14])
        self.var_telegram_id.set(data[15])

    def update_data(self):
        email = self.var_email.get()
        if self.var_dep.get()=='Select Department' or self.var_std_name.get()=='' or self.va_std_id.get()=='' or self.var_course.get()=='Select Course' or self.var_year.get()=='Select Year' or self.var_semester.get()=='Select Semester' or self.var_div.get()=='Select Division' or self.var_gender.get()=='Select Gender' or self.var_roll.get()==''or self.var_email.get()=='' or self.var_dob.get()==''or self.var_phone.get()=='' or self.var_address.get()=='' or self.var_teacher.get()=='' or self.var_radio1.get()=='' or self.var_telegram_id.get()=='':
            messagebox.showerror("Error","All Fields are required",parent=self.root)
        elif not email.endswith("@gmail.com") or not any(char.isdigit() for char in email):
            messagebox.showerror("Error", "Please enter a valid Gmail address with at least one digit.")
        elif len(self.var_phone.get())!=10 or not self.var_phone.get().isdigit:
            messagebox.showerror("Error","Please enter a valid Phone No with 10 digits",parent=self.root)
        elif self.var_roll.get().isdigit()==False:
            messagebox.showerror("Error","Please enter a valid Roll Number only digits are allowed",parent=self.root)
        elif not self.va_std_id.get().isdigit:
            messagebox.showerror("Error","Please enter a valid Student Id only digits are allowed",parent=self.root)
        
        else:
            try:
                update=messagebox.askyesno("Update",'Do you want to update data',parent=self.root)
                if update>0:
                    conn=mysql.connector.connect(host='localhost',port=3307,username='root',password='1582',database='face_recognizer')
                    my_cursor=conn.cursor()
                    my_cursor.execute('update student set Dep=%s,Course=%s,Year=%s,Semester=%s,Student_name=%s,Division=%s,Roll=%s,Gender=%s,Dob=%s,Email=%s,Phone=%s,Address=%s,Teacher=%s,PhotoSample=%s,TelegramID=%s where Student_id=%s',(
                                self.var_dep.get(),self.var_course.get(),self.var_year.get(),self.var_semester.get(),
                                self.var_std_name.get(),self.var_div.get(),self.var_roll.get(),self.var_gender.get(),
                                self.var_dob.get(),self.var_email.get(),self.var_phone.get(),self.var_address.get(),
                                self.var_teacher.get(),self.var_radio1.get(),self.var_telegram_id.get(),self.va_std_id.get()),
)
                else:
                    if not update: return
                messagebox.showinfo("Succes",'Student details has been Updated Succesfully',parent=self.root)
                conn.commit()
                self.refresh_animation(self.fetch_data)
                conn.close()
            except Exception as e:
                messagebox.showerror('Error',f'Student details failed to be Updated due to {str(e)}',parent=self.root)

    def delete_data(self):
        if self.va_std_id.get()=='':
             messagebox.showerror("Error","Student id must be required",parent=self.root)
        else:
            try:
                delete=messagebox.askyesno("Delete",'Do you want to delete data',parent=self.root)
                if delete>0:
                    conn=mysql.connector.connect(host='localhost',port=3307,username='root',password='1582',database='face_recognizer')
                    my_cursor=conn.cursor()
                    sql='delete from student where Student_id=%s'
                    val=(self.va_std_id.get(),)
                    my_cursor.execute(sql,val)
                else:
                    if not delete: return
                conn.commit()
                messagebox.showinfo("Succes",'Student details has been Deleted Succesfully',parent=self.root)
                self.refresh_animation(self.fetch_data)
                conn.close()
            except Exception as e:
                messagebox.showerror('Error',f'Student details failed to be Deleted due to {str(e)}',parent=self.root)

    def live_search(self, event=None):
        search_by = self.var_search_combo.get()
        keyword = self.var_search_entry.get().strip()
        if search_by == "Select Option" or not keyword:
            self.fetch_data()
            return
        column_map = {
            "Student ID": "Student_id",
            "Roll No": "Roll",
            "Student Name": "Student_name",
            "Department": "Dep",
            "Phone No": "Phone",
            "Telegram ID": "TelegramID",   # 👈 ADD
            "Gender": "Gender",
            "Year": "Year"
        }

        column = column_map.get(search_by)
        if not column: return
        try:
            conn = mysql.connector.connect(host="localhost", port=3307,username="root", password="1582",database="face_recognizer")
            cursor = conn.cursor()
            query = f"SELECT * FROM student WHERE {column} LIKE %s"
            cursor.execute(query, (f"%{keyword}%",))
            rows = cursor.fetchall()
            self.student_table.delete(*self.student_table.get_children())
            for row in rows:
                self.student_table.insert("", END, values=row)
            conn.close()
        except Exception as e:
            print("Live search error:", e)

    def reset_search(self):
        self.var_search_entry.set("")
        self.var_search_combo.set("Select Option")
        self.fetch_data()

    def open_student_filter(self):
        win = Toplevel(self.root)
        win.title("Advanced Filters")
        win.geometry("360x440")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        try:
            win.iconbitmap('college_images\\bg1.ico')
        except:
            pass

        # ================= GENDER =================
        Label(win, text="Gender", font=("times new roman", 11, "bold")).pack(anchor=W, padx=10)

        gender_vars = {}
        for g in ("Male", "Female", "Other"):
            v = BooleanVar(value=g in self.active_filters["Gender"])
            gender_vars[g] = v
            Checkbutton(win, text=g, variable=v).pack(anchor=W, padx=25)

        # ================= DEPARTMENT =================
        Label(win, text="Department", font=("times new roman", 11, "bold")).pack(anchor=W, padx=10, pady=5)

        dept_vars = {}
        for d in ("Computer", "IT", "Civil", "Mechenical"):
            v = BooleanVar(value=d in self.active_filters["Department"])
            dept_vars[d] = v
            Checkbutton(win, text=d, variable=v).pack(anchor=W, padx=25)

        # ================= YEAR =================
        Label(win, text="Year", font=("times new roman", 11, "bold")).pack(anchor=W, padx=10, pady=5)

        year_vars = {}
        for y in ("2023-24", "2024-25", "2025-26"):
            v = BooleanVar(value=y in self.active_filters["Year"])
            year_vars[y] = v
            Checkbutton(win, text=y, variable=v).pack(anchor=W, padx=25)

        # ================= APPLY FILTER =================
        def apply_filter():
            clauses = []
            values = []

            def build_in(col, data):
                return f"{col} IN ({','.join(['%s'] * len(data))})"

            genders = [k for k, v in gender_vars.items() if v.get()]
            if genders:
                clauses.append(build_in("Gender", genders))
                values.extend(genders)

            depts = [k for k, v in dept_vars.items() if v.get()]
            if depts:
                clauses.append(build_in("Dep", depts))
                values.extend(depts)

            years = [k for k, v in year_vars.items() if v.get()]
            if years:
                clauses.append(build_in("Year", years))
                values.extend(years)

            # Save active filters
            self.active_filters["Gender"] = genders
            self.active_filters["Department"] = depts
            self.active_filters["Year"] = years

            query = "SELECT * FROM student"
            if clauses:
                query += " WHERE " + " AND ".join(clauses)

            try:
                conn = mysql.connector.connect(
                    host="localhost", port=3307,
                    username="root", password="1582",
                    database="face_recognizer"
                )
                cur = conn.cursor()
                cur.execute(query, tuple(values))
                rows = cur.fetchall()

                self.student_table.delete(*self.student_table.get_children())
                for r in rows:
                    self.student_table.insert("", END, values=r)

                conn.close()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self.root)

            win.destroy()

        # ================= CLEAR FILTER =================
        def clear_filter():
            self.active_filters = {
                "Gender": [],
                "Department": [],
                "Year": []
            }
            self.fetch_data()
            win.destroy()

        Button(win, text="Apply Filters", bg="green", fg="white", width=18,
            font=("times new roman", 10, "bold"),cursor='hand2', command=apply_filter).pack(pady=12)

        Button(win, text="Clear Filters", bg="red", fg="white", width=18,
            font=("times new roman", 10, "bold"),cursor='hand2', command=clear_filter).pack()

    def student_sort(self, col, reverse):
        col_type = self.student_columns[col]
        data = [(self.student_table.set(k, col), k) for k in self.student_table.get_children('')]
        def sort_key(item):
            value = item[0].strip()
            if col_type == int: return int(value) if value.isdigit() else 0
            elif col_type == 'date': return datetime.datetime.strptime(value, "%d/%m/%Y")
            else: return value.lower()
        data.sort(key=sort_key, reverse=reverse)
        for index, (_, k) in enumerate(data): self.student_table.move(k, '', index)
        self.student_table.heading(col, command=lambda: self.student_sort(col, not reverse))

    def reset_data(self):
        self.var_dep.set("Select Department")
        self.var_course.set('Select Course')
        self.var_year.set('Select Year')
        self.var_semester.set('Select Semester')
        self.va_std_id.set('')
        self.var_std_name.set('')
        self.var_div.set('Select Division')
        self.var_roll.set('')
        self.var_gender.set('Select Gender')
        self.var_dob.set('')
        self.var_email.set('')
        self.var_phone.set('')
        self.var_address.set('')
        self.var_teacher.set('')
        self.var_radio1.set('')
        self.var_telegram_id.set("")


    def photo_sample(self):
        email = self.var_email.get()
        if self.var_dep.get()=='Select Department' or self.var_std_name.get()=='' or self.va_std_id.get()=='' or self.var_course.get()=='Select Course' or self.var_year.get()=='Select Year' or self.var_semester.get()=='Select Semester' or self.var_div.get()=='Select Division' or self.var_gender.get()=='Select Gender' or self.var_roll.get()==''or self.var_email.get()=='' or self.var_dob.get()==''or self.var_phone.get()=='' or self.var_address.get()=='' or self.var_teacher.get()=='' or self.var_radio1.get()=='':
            messagebox.showerror("Error","All Fields are required",parent=self.root)
        elif not email.endswith("@gmail.com") or not any(char.isdigit() for char in email):
            messagebox.showerror("Error", "Please enter a valid Gmail address with at least one digit.")
        elif len(self.var_phone.get())!=10 or not self.var_phone.get().isdigit:
            messagebox.showerror("Error","Please enter a valid Phone No with 10 digits",parent=self.root)
        elif self.var_roll.get().isdigit()==False:
            messagebox.showerror("Error","Please enter a valid Roll Number only digits are allowed",parent=self.root)
        elif not self.va_std_id.get().isdigit:
            messagebox.showerror("Error","Please enter a valid Student Id only digits are allowed",parent=self.root)
        else:
            try:
                 conn=mysql.connector.connect(host='localhost',port=3307,username='root',password='1582',database='face_recognizer')
                 my_cursor=conn.cursor()
                 my_cursor.execute('select * from student')
                 myresult=my_cursor.fetchall()
                 id=0
                 for x in myresult: id+=1
                 my_cursor.execute('update student set Dep=%s,Course=%s,Year=%s,Semester=%s,Student_name=%s,Division=%s,Roll=%s,Gender=%s,Dob=%s,Email=%s,Phone=%s,Address=%s,Teacher=%s,PhotoSample=%s where Student_id=%s',(
                                self.var_dep.get(),self.var_course.get(),self.var_year.get(),self.var_semester.get(),
                                self.var_std_name.get(),self.var_div.get(),self.var_roll.get(),self.var_gender.get(),
                                self.var_dob.get(),self.var_email.get(),self.var_phone.get(),self.var_address.get(),
                                self.var_teacher.get(),self.var_radio1.get(),self.va_std_id.get()))
                 conn.commit()
                 self.fetch_data()
                 self.reset_data()
                 conn.close()

                 face_classifier=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
                 
                 def face_cropped(img):
                     gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                     faces=face_classifier.detectMultiScale(gray,1.3,5)
                     for (x,y,w,h) in faces:
                         face_cropped=img[y:y+h,x:x+w]
                         return face_cropped
                 
                 cap=cv2.VideoCapture(1)
                 img_id=0
                 while True:
                         ret,my_frame=cap.read()
                         if face_cropped(my_frame) is not None:
                             img_id+=1
                             face_raw=cv2.resize(face_cropped(my_frame),(450,450))
                             
                             # SAVE 5th IMAGE AS COLOR, REST AS GRAY
                             if img_id == 5:
                                 face = face_raw
                             else:
                                 face = cv2.cvtColor(face_raw, cv2.COLOR_BGR2GRAY)

                             file_name_path='data/user.'+str(id)+"."+str(img_id)+'.jpg'
                             cv2.imwrite(file_name_path,face)
                             cv2.putText(face,str(img_id),(50,50),cv2.FONT_HERSHEY_COMPLEX,2,(0,255,0),2)
                             cv2.imshow('Cropped Face',face)
                         if cv2.waitKey(1)==13 or int(img_id)==100:
                             break
                 cap.release()
                 cv2.destroyAllWindows()
                 messagebox.showinfo('Result','Generating data sets completed succesfully',parent=self.root)
            except Exception as e:
                messagebox.showerror('Error',f' Generating dataset is failed due to {str(e)}',parent=self.root)

    def update_photosample(self):
        if self.var_dep.get() == "" or self.va_std_id.get() == "":
            messagebox.showerror("Error", "All Fields are required", parent=self.root)
            return
        try:
            conn = mysql.connector.connect(host="localhost",port=3307, username="root", password="1582", database="face_recognizer")
            my_cursor = conn.cursor()
            student_id = self.va_std_id.get()
            my_cursor.execute("SELECT * FROM student WHERE Student_id=%s", (student_id,))
            result = my_cursor.fetchone()
            conn.close()

            if result is None:
                messagebox.showerror("Error", "Student ID not found", parent=self.root)
                return

            face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            def face_cropped(img):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    return img[y:y+h, x:x+w]

            cap = cv2.VideoCapture(1)
            img_id = 0
            while True:
                ret, frame = cap.read()
                if face_cropped(frame) is not None:
                    img_id += 1
                    face_raw = cv2.resize(face_cropped(frame), (450, 450))
                    
                    # SAVE 5th IMAGE AS COLOR, REST AS GRAY
                    if img_id == 5:
                        face = face_raw
                    else:
                        face = cv2.cvtColor(face_raw, cv2.COLOR_BGR2GRAY)
                    
                    file_path = f"data/user.{student_id}.{img_id}.jpg"
                    cv2.imwrite(file_path, face)
                    cv2.putText(face, str(img_id), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
                    cv2.imshow("Cropped Face", face)

                if cv2.waitKey(1) == 13 or img_id == 100:
                    break
            cap.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Result", "Photo samples updated successfully", parent=self.root)

        except Exception as es:
            messagebox.showerror("Error", f"Photo samples failed to be Updated due to: {str(es)}", parent=self.root)

    def back(self):
        self.root.destroy()

    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time) 

if __name__ == '__main__':
    root=Tk()
    obj=students(root)
    root.mainloop()