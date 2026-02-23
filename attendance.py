from time import strftime
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
from config import get_db_connection
import cv2
import calendar
import datetime
import tkinter as tk
import matplotlib
import csv
import json
from tkinter import filedialog
from openpyxl import Workbook
from informing import Inform
from attendancereport import DetailedAttendanceReport
matplotlib.use('TkAgg')
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from utils import resource_path
# Global list to hold data for filtering/sorting in memory
mydata = []

class DatePickerDialog:
    def __init__(self, parent, initial_date, callback):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Date")
        self.dialog.transient(parent)
        try:
            self.dialog.iconbitmap(resource_path('college_images\\bg1.ico'))
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
        # Header Frame with Color
        header_frame = tk.Frame(self.dialog, bg="#4a90e2", pady=10)
        header_frame.pack(fill=tk.X)
        
        # Navigation
        nav_frame = ttk.Frame(self.dialog)
        nav_frame.pack(pady=10)
        
        months = list(calendar.month_name)[1:]
        self.month_var = tk.StringVar()
        self.month_combobox = ttk.Combobox(nav_frame, textvariable=self.month_var, values=months, state='readonly', width=12, font=('Segoe UI', 10))
        self.month_combobox.pack(side=tk.LEFT, padx=5)
        self.month_combobox.bind("<<ComboboxSelected>>", self.change_month)
        
        current_year = datetime.date.today().year
        years = list(range(1990, current_year + 5))
        self.year_var = tk.StringVar()
        self.year_combobox = ttk.Combobox(nav_frame, textvariable=self.year_var, values=years, state='readonly', width=8, font=('Segoe UI', 10))
        self.year_combobox.pack(side=tk.LEFT, padx=5)
        self.year_combobox.bind("<<ComboboxSelected>>", self.change_year)
        
        # Colorful Navigation Buttons
        tk.Button(nav_frame, text="◀", bg="#f39c12", fg="white", font=('bold'), command=self.prev_month, cursor="hand2", relief=FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="▶", bg="#f39c12", fg="white", font=('bold'), command=self.next_month, cursor="hand2", relief=FLAT).pack(side=tk.LEFT, padx=5)
        
        self.calendar_frame = ttk.Frame(self.dialog)
        self.calendar_frame.pack(padx=10, pady=5)
        self.update_calendar()
        
        # Select Button
        tk.Button(self.dialog, text="Select Date", command=self.on_select, bg="#27ae60", fg="white", font=('Segoe UI', 10, 'bold'), cursor="hand2", relief=FLAT, padx=20, pady=5).pack(pady=10)
    
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
            # Colorful Header for Days
            label = tk.Label(self.calendar_frame, text=day, font=('Segoe UI', 9, 'bold'),
                              bg='#34495e', fg='white', width=5)
            label.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            
        cal = calendar.monthcalendar(self.current_display_date.year, self.current_display_date.month)
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0: continue
                date_obj = datetime.date(self.current_display_date.year, self.current_display_date.month, day)
                today = datetime.date.today()
                is_future = date_obj > today
                
                # Default Colors
                bg_color = 'white'
                fg_color = 'black'
                
                # Highlight Logic
                if date_obj == datetime.date.today():
                    bg_color = '#e74c3c' # Red for today
                    fg_color = 'white'
                elif date_obj == self.selected_date:
                    bg_color = '#3498db' # Blue for selected
                    fg_color = 'white'
                elif day_num >= 5: # Weekends (Sat=5, Sun=6)
                    bg_color = '#fce4ec' # Light Pink
                    
                btn = tk.Button(self.calendar_frame, text=str(day), bg=bg_color, fg=fg_color, font=('Segoe UI', 9),
                relief=tk.FLAT, state=tk.DISABLED if is_future else tk.NORMAL, cursor="hand2", command=lambda d=date_obj: self.set_selected_date(d))
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

class TimePickerDialog:
    def __init__(self, parent, initial_time, callback):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Time")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        try:
            self.dialog.iconbitmap(resource_path('college_images\\bg1.ico'))
        except:
            pass

        self.callback = callback

        # Parse initial time
        try:
            t = datetime.datetime.strptime(initial_time, "%I:%M:%S %p")
            h, m, s, ap = t.hour, t.minute, t.second, "AM" if t.hour < 12 else "PM"
        except:
            now = datetime.datetime.now()
            h, m, s, ap = now.hour, now.minute, now.second, "AM" if now.hour < 12 else "PM"

        self.hour = tk.IntVar(value=h if h <= 12 else h - 12)
        self.minute = tk.IntVar(value=m)
        self.second = tk.IntVar(value=s)
        self.ampm = tk.StringVar(value=ap)

        self.build_ui()

    def build_ui(self):
        frame = Frame(self.dialog, padx=20, pady=20)
        frame.pack(expand=True)

        Spinbox(frame, from_=1, to=12, width=5,
                font=('times new roman', 14),
                textvariable=self.hour).grid(row=0, column=0)

        Label(frame, text=":", font=('times new roman', 14)).grid(row=0, column=1)

        Spinbox(frame, from_=0, to=59, width=5, format="%02.0f",
                font=('times new roman', 14),
                textvariable=self.minute).grid(row=0, column=2)

        Label(frame, text=":", font=('times new roman', 14)).grid(row=0, column=3)

        Spinbox(frame, from_=0, to=59, width=5, format="%02.0f",
                font=('times new roman', 14),
                textvariable=self.second).grid(row=0, column=4)

        ttk.Combobox(
            frame,
            values=("AM", "PM"),
            width=5,
            font=('times new roman', 13),
            state="readonly",
            textvariable=self.ampm
        ).grid(row=0, column=5, padx=10)

        Button(
            self.dialog,
            text="Select Time",
            bg="#27ae60",
            fg="white",
            font=('times new roman', 12, 'bold'),
            width=15,
            cursor="hand2",
            command=self.on_select
        ).pack(pady=15)

    def on_select(self):
        h = self.hour.get()
        m = self.minute.get()
        s = self.second.get()

        # Convert to 24-hour
        if self.ampm.get() == "PM" and h != 12:
            h += 12
        if self.ampm.get() == "AM" and h == 12:
            h = 0

        selected_time = datetime.datetime.now().replace(
            hour=h, minute=m, second=s, microsecond=0
        )

        current_time = datetime.datetime.now().replace(microsecond=0)

        # 🚫 Future time check
        if selected_time > current_time:
            messagebox.showerror(
                "Invalid Time",
                "Selected time cannot be greater than current time.",
                parent=self.dialog
            )
            return

        final_time = selected_time.strftime("%H:%M:%S")  # 24-hour format
        self.callback(final_time)
        self.dialog.destroy()

class attendance:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Attendance Management System")
        self.root.resizable(True, True)
        self.root.minsize(1024, 600)
        try:
            self.root.wm_iconbitmap(resource_path('college_images\\bg1.ico'))
        except:
            pass

        # --- Variables ---
        self.var_atten_id = StringVar()
        self.var_atten_name = StringVar()
        self.var_atten_roll = StringVar()
        self.var_atten_dept = StringVar()
        self.var_atten_time = StringVar()
        self.var_atten_date = StringVar()
        self.var_atten_status = StringVar()
        self.attendance_id = None # Store the database primary key for updates
        
        # Filter Variables
        self.filter_from_date = StringVar()
        self.filter_to_date = StringVar()
        self.active_filters = {
            "Status": [],
            "Department": [],
            "DateRange": []
        }

        # Search variables
        self.var_search_combo = StringVar()
        self.var_search_entry = StringVar()

        # --- Database Setup ---
        self.setup_database()

        # --- UI Header & Layout ---
        try:
            # Header Image 1
            self.org_img_h1 = Image.open(resource_path("college_images\\smart-attendance.jpg"))
            self.h_lbl1 = Label(self.root, bg='white')
            self.h_lbl1.place(relx=0, rely=0, relwidth=0.46, relheight=0.25)
            
            # Header Image 2
            self.org_img_h2 = Image.open(resource_path("college_images\\12.jpg"))
            self.h_lbl2 = Label(self.root, bg='white')
            self.h_lbl2.place(relx=0.46, rely=0, relwidth=0.54, relheight=0.25)

            # Background Image
            self.org_img_bg = Image.open(resource_path("college_images\\wp2551980.jpg"))
            self.bg_lbl = Label(self.root, bg='white')
            # Y=170/680 = 0.25. Height=510/680=0.75
            self.bg_lbl.place(relx=0, rely=0.25, relwidth=1.0, relheight=0.75)
            
        except Exception as e:
            print(f"Error loading images: {e}")
            self.bg_lbl = Frame(self.root, bg='white')
            self.bg_lbl.place(relx=0, rely=0.25, relwidth=1.0, relheight=0.75)

        # Overlays - Parent to Root
        self.title_lbl = Label(self.root, text='ATTENDANCE MANAGEMENT SYSTEM', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(relx=0, rely=0.25, relwidth=1.0, relheight=0.065)

        self.time_lbl = Label(self.root, font=('times new roman', 15, 'bold'), bg='white', fg='red', borderwidth=0, highlightthickness=0)
        self.time_lbl.place(relx=0, rely=0.25, relwidth=0.09, relheight=0.065)
        self.update_time()

        self.back_btn_frame = Frame(self.root, bg='white')
        self.back_btn_frame.place(relx=0.85, rely=0.25, relwidth=0.15, relheight=0.065)
        
        back_btn = Button(self.back_btn_frame, text="Back", width=22, cursor='hand2', font=('times new roman', 10, 'bold'), bg='red', fg='white', activebackground="green", command=self.back)
        back_btn.pack(pady=5, padx=10)

        # --- Main Frame ---
        # Original: y=170 + 50 = 220? No, code said 50 inside bg. 
        # Bg starts at 170. So 220 absolute. 220/680 = 0.323.
        # Let's say rely=0.32.
        main_frame = Frame(self.root, bd=2)
        main_frame.place(relx=0.007, rely=0.32, relwidth=0.986, relheight=0.67)
        
        # Resize Binding
        self.resize_timer = None
        self.root.bind("<Configure>", self.on_resize)

        # --- Left Frame (Controls) ---
        left_frame = LabelFrame(main_frame, bd=2, bg='white', relief=RIDGE, text='Students Attendance Details', font=('times new roman', 12, 'bold'))
        left_frame.place(relx=0.005, rely=0.02, relwidth=0.48, relheight=0.96)

        try:
            self.org_img_left = Image.open(resource_path("college_images\\face-recognition.png"))
            img_left = self.org_img_left.resize((635, 90), Image.Resampling.LANCZOS)
            self.left_photoimg = ImageTk.PhotoImage(img_left)
            self.f_lbl_left = Label(left_frame, image=self.left_photoimg)
            self.f_lbl_left.place(relx=0.01, rely=0, relwidth=0.98, relheight=0.18)
        except:
            pass

        left_inside_frame = Frame(left_frame, bd=2, relief=RIDGE, bg='white')
        left_inside_frame.place(relx=0, rely=0.2, relwidth=1.0, relheight=0.78)
        for i in range(4): left_inside_frame.columnconfigure(i, weight=1)

        # Inputs
        # Attendance ID
        Label(left_inside_frame, text='AttendanceID:', font=('times new roman', 12, 'bold'), bg='white').grid(row=0, column=0, padx=5, sticky=W)
        ttk.Entry(left_inside_frame, width=15, font=('times new roman', 12), textvariable=self.var_atten_id).grid(row=0, column=1, padx=5, pady=3, sticky='EW')
        
        # Name
        Label(left_inside_frame, text='Name:', font=('times new roman', 12, 'bold'), bg='white').grid(row=0, column=2, padx=5, sticky=W)
        ttk.Entry(left_inside_frame, width=15, font=('times new roman', 12), textvariable=self.var_atten_name).grid(row=0, column=3, padx=5, pady=3, sticky='EW')
        
        # Roll
        Label(left_inside_frame, text='Roll No:', font=('times new roman', 12, 'bold'), bg='white').grid(row=1, column=0, padx=5, sticky=W)
        ttk.Entry(left_inside_frame, width=15, font=('times new roman', 12), textvariable=self.var_atten_roll).grid(row=1, column=1, padx=5, pady=3, sticky='EW')
        
        # Dept
        Label(left_inside_frame, text='Department:', font=('times new roman', 12, 'bold'), bg='white')\
            .grid(row=1, column=2, padx=5, sticky=W)

        dept_combo = ttk.Combobox(
            left_inside_frame,
            font=('times new roman', 12, 'bold'),
            width=17,
            state='readonly',
            textvariable=self.var_atten_dept
        )
        dept_combo['values'] = ("Computer", "IT", "Civil", "Mechenical")
        dept_combo.set("Select Department")
        dept_combo.grid(row=1, column=3, padx=5, pady=3, sticky='EW')

        
        # Time
        Label(left_inside_frame, text='Time:HH:MM:SS(24-hour)', font=('times new roman', 9, 'bold'), bg='white')\
        .grid(row=2, column=0, padx=5, sticky=W)

        time_frame = Frame(left_inside_frame, bg='white')
        time_frame.grid(row=2, column=1, padx=5, pady=3, sticky='EW')

        ttk.Entry(
            time_frame, width=12, font=('times new roman', 12),
            textvariable=self.var_atten_time, state='readonly'
        ).pack(side=LEFT)

        Button(
            time_frame, text="⏰", font=("Segoe UI Emoji", 10), width=3,
            bg='red', fg='blue', cursor="hand2",
            command=self.open_time_picker
        ).pack(side=LEFT, padx=3)

        
        # Date with Date Picker Button
        Label(left_inside_frame, text='Date:DD/MM/YYYY', font=('times new roman', 10, 'bold'), bg='white').grid(row=2, column=2, padx=5, sticky=W)
        
        # Create a frame to hold entry and button together for alignment
        date_frame = Frame(left_inside_frame, bg='white')
        date_frame.grid(row=2, column=3, padx=5, pady=3, sticky='EW')
        
        date_entry = ttk.Entry(date_frame, width=17, font=('times new roman', 12), textvariable=self.var_atten_date)
        date_entry.pack(side=LEFT)
        
        date_btn = Button(date_frame, text="📅", font=("Segoe UI Emoji", 10), width=3, bg='red', fg='blue', activebackground='green', activeforeground='yellow', cursor="hand2", command=self.open_attendance_date_calendar)
        date_btn.pack(side=LEFT, padx=3)
        
        # Status
        Label(left_inside_frame, text='Status:', font=('times new roman', 12, 'bold'), bg='white').grid(row=3, column=0, padx=5, sticky=W)
        status_combo = ttk.Combobox(left_inside_frame, font=('times new roman', 12, 'bold'), width=13, state='readonly', textvariable=self.var_atten_status)
        status_combo['values'] = ('Present', 'Absent')
        status_combo.current(0)
        status_combo.grid(row=3, column=1, padx=5, pady=5, sticky='EW')

        # --- Button Frame 1 (CRUD) ---
        btn_frame = Frame(left_inside_frame, bd=2, relief=RIDGE, bg='white')
        btn_frame.place(relx=0.01, rely=0.54, relwidth=0.98, relheight=0.12)
        for i in range(4): btn_frame.columnconfigure(i, weight=1)
        btn_frame.rowconfigure(0, weight=1)

        Button(btn_frame, text="Save", command=self.add_data, cursor='hand2', font=('times new roman', 11, 'bold'), bg='darkblue', fg='white', activebackground="red", activeforeground='green').grid(row=0, column=0, sticky='NSEW')
        Button(btn_frame, text="Update", command=self.update_data, cursor='hand2', font=('times new roman', 11, 'bold'), bg='darkblue', fg='white', activebackground="red", activeforeground='green').grid(row=0, column=1, sticky='NSEW')
        Button(btn_frame, text="Delete", command=self.delete_data, cursor='hand2', font=('times new roman', 11, 'bold'), bg='darkblue', fg='white', activebackground="red", activeforeground='green').grid(row=0, column=2, sticky='NSEW')
        Button(btn_frame, text="Reset", command=self.reset_data, cursor='hand2', font=('times new roman', 11, 'bold'), bg='darkblue', fg='white', activebackground="red", activeforeground='green').grid(row=0, column=3, sticky='NSEW')

        # --- Button Frame 2 (Report/Inform) ---
        
        btn_frame3 = Frame(left_inside_frame, bd=2, relief=RIDGE, bg='white')
        btn_frame3.place(relx=0.01, rely=0.68, relwidth=0.98, relheight=0.30)
        for i in range(2): btn_frame3.columnconfigure(i, weight=1)
        for i in range(2): btn_frame3.rowconfigure(i, weight=1)
        
        Button(btn_frame3, text="Inform Students", command=self.inform, cursor='hand2', font=('times new roman', 11, 'bold'), bg='purple', fg='white').grid(row=0, column=0, sticky='NSEW')
        Button(btn_frame3, text="Attendance Report", command=self.plot_attendance_graph, cursor='hand2', font=('times new roman', 11, 'bold'), bg='purple', fg='white').grid(row=0, column=1, sticky='NSEW')
        Button(
            btn_frame3,
            text="Export Attendance",
            command=self.export_data,
            cursor='hand2',
            font=('times new roman', 11, 'bold'),
            bg='orange',
            fg='white'
        ).grid(
            row=1,
            column=0,
            columnspan=1,  
            sticky="NSEW",    
            pady=2
        )

        Button(
            btn_frame3,
            text="Check Low Attendance",
            command=self.check_attendance_alert,
            cursor='hand2',
            font=('times new roman', 11, 'bold'),
            bg='red',
            fg='white'
        ).grid(
            row=1,
            column=1,
            columnspan=1, 
            sticky="NSEW",    
            pady=2
        )

        # --- Right Frame (Table) ---
        right_frame = LabelFrame(main_frame, bd=2, bg='white', relief=RIDGE, text='Attendance Details', font=('times new roman', 12, 'bold'))
        right_frame.place(relx=0.51, rely=0.02, relwidth=0.485, relheight=0.96)

        # --- Search Frame (Identical to student.py) ---
        search_frame = LabelFrame(right_frame, bd=2, bg='white', relief=RIDGE, text='Search System', font=('times new roman', 12, 'bold'))
        search_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.14)
        search_frame.columnconfigure(0, weight=0)
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(2, weight=2)
        for i in range(3, 6): search_frame.columnconfigure(i, weight=1)
        search_frame.rowconfigure(0, weight=1)

        search_label = Label(search_frame, text='Search By :', font=('times new roman', 12, 'bold'), bg='red', fg='white')
        search_label.grid(row=0, column=0, padx=5, sticky='NSEW')

        search_combo = ttk.Combobox(search_frame, font=('times new roman', 12, 'bold'), width=12, state='read', textvariable=self.var_search_combo)
        search_combo["values"] = ("Student_id", "Name", "Roll", "Dep", "Date", "Status")
        search_combo.current(0)
        search_combo.set("Select Option")
        search_combo.grid(row=0, column=1, padx=2, sticky='EW')

        # Widened Search Entry
        search_entry = ttk.Entry(search_frame, width=25, font=('times new roman', 12, 'bold'), textvariable=self.var_search_entry)
        search_entry.grid(row=0, column=2, padx=2, pady=3, sticky='EW')
        search_entry.bind("<KeyRelease>", self.advanced_search)

        reset_btn = Button(search_frame, text="Reset", cursor='hand2', font=('times new roman', 10, 'bold'), bg='green', fg='white', activebackground="red", activeforeground='green', command=self.reset_search)
        reset_btn.grid(row=0, column=3, padx=3, sticky='NSEW')
        
        # Added Refresh Button
        refresh_btn = Button(search_frame, text="Refresh", cursor='hand2', font=('times new roman', 10, 'bold'), bg='darkblue', fg='white', activebackground="red", activeforeground='green', command=lambda: self.refresh_animation(self.auto_load_data)
        )
        refresh_btn.grid(row=0, column=4, padx=3, sticky='NSEW')
        
        Button(search_frame, text="Filter", font=("times new roman", 10, "bold"), bg="purple", fg="white", cursor='hand2', activebackground="#5d57b4", activeforeground='black', command=self.open_filter_window).grid(row=0, column=5, padx=3, sticky='NSEW')

        # --- Table Frame ---
        table_frame = Frame(right_frame, bd=2, bg='white', relief=RIDGE)
        table_frame.place(relx=0.01, rely=0.16, relwidth=0.98, relheight=0.82)

        scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL)

        self.attendence_table = ttk.Treeview(table_frame, column=('db_id', 'id', 'name', 'roll', 'department', 'time', 'date', 'attendance'), xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.attendence_table.xview)
        scroll_y.config(command=self.attendence_table.yview)

        self.attendence_table.heading('db_id', text='DB ID')
        self.attendence_table.heading('id', text='ID')
        self.attendence_table.heading('name', text='Name')
        self.attendence_table.heading('roll', text='Roll')
        self.attendence_table.heading('department', text='Dept')
        self.attendence_table.heading('time', text='Time')
        self.attendence_table.heading('date', text='Date')
        self.attendence_table.heading('attendance', text='Status')

        self.attendence_table['show'] = 'headings'
        self.attendence_table.column('db_id', width=0, stretch=NO)
        self.attendence_table.column('id', width=100)
        self.attendence_table.column('name', width=100)
        self.attendence_table.column('roll', width=100)
        self.attendence_table.column('department', width=100)
        self.attendence_table.column('time', width=100)
        self.attendence_table.column('date', width=100)
        self.attendence_table.column('attendance', width=100)

        self.attendence_table.pack(fill=BOTH, expand=1)
        self.attendence_table.bind('<ButtonRelease>', self.get_cursor)
        
        # Sorting setup
        self.attendance_columns = {
            'id': int, 'name': str, 'roll': int, 'department': str,
            'time': str, 'date': 'date', 'attendance': str
        }
        for col in self.attendance_columns:
            self.attendence_table.heading(col, text=col.title(), command=lambda c=col: self.attendance_sort(c, False))

        # Initial Data Load
        self.auto_load_data()
        self.set_current_date_time()

    def export_data(self):
        rows = []
        for item in self.attendence_table.get_children():
            # Slice [1:] to skip the hidden 'db_id' column
            rows.append(self.attendence_table.item(item)['values'][1:])

        if not rows:
            messagebox.showerror("No Data", "No data available to export", parent=self.root)
            return

        filetypes = [
            ("CSV File", "*.csv"),
            ("Excel File", "*.xlsx"),
            ("Text File", "*.txt"),
            ("JSON File", "*.json"),
            ("PDF File", "*.pdf")  # Added PDF option
        ]

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=filetypes,
            title="Export Attendance Data",
            parent=self.root
        )

        if not file_path:
            return

        try:
            headers = ["Student ID", "Name", "Roll", "Department", "Time", "Date", "Status"]

            # CSV Export
            if file_path.endswith(".csv"):
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)

            # Excel Export
            elif file_path.endswith(".xlsx"):
                wb = Workbook()
                ws = wb.active
                ws.title = "Attendance"
                ws.append(headers)
                for r in rows:
                    ws.append(r)
                wb.save(file_path)

            # Text Export
            elif file_path.endswith(".txt"):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\t".join(headers) + "\n")
                    for r in rows:
                        f.write("\t".join(map(str, r)) + "\n")

            # JSON Export
            elif file_path.endswith(".json"):
                data = [dict(zip(headers, r)) for r in rows]
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

            # PDF Export (Formatted properly)
            elif file_path.endswith(".pdf"):
                pdf = SimpleDocTemplate(
                    file_path,
                    pagesize=A4,
                    rightMargin=30,
                    leftMargin=30,
                    topMargin=40,
                    bottomMargin=30
                )

                elements = []
                styles = getSampleStyleSheet()

                # 🔵 Centered & Colored Title
                title_style = styles["Title"]
                title_style.alignment = 1  # Center
                title_style.textColor = colors.HexColor("#1f4bd8")

                elements.append(Paragraph("Attendance Report", title_style))

                elements.append(Paragraph("<br/>", styles["Normal"]))  # spacing

                # Table data (headers + rows)
                table_data = [
                    ["Student ID", "Name", "Roll", "Department", "Time", "Date", "Status"]
                ]

                for r in rows:
                    table_data.append([str(x) for x in r])

                # Create table
                table = Table(
                    table_data,
                    colWidths=[60, 80, 60, 90, 80, 70, 70]
                )

                # 🎨 Table Styling
                table.setStyle(TableStyle([
                    # Header style
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4bd8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),

                    # Body cells
                    ("ALIGN", (0, 1), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),

                    # Grid lines 🔲
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),

                    # Row background
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ]))

                elements.append(table)
                pdf.build(elements)

            messagebox.showinfo(
                "Export Successful",
                f"Attendance data exported successfully!\n\n"
                f"📁 File: {file_path}\n"
                f"📄 Format: PDF",
                parent=self.root
            )

        except Exception as e:
            messagebox.showerror("Export Error", str(e), parent=self.root)

    def open_time_picker(self):
        def set_time(selected_time):
            self.var_atten_time.set(selected_time)

        TimePickerDialog(
            self.root,
            self.var_atten_time.get(),
            set_time
        )

    def set_current_date_time(self):
        today = datetime.date.today().strftime("%d/%m/%Y")
        now = datetime.datetime.now().strftime("%I:%M:%S %p")

        self.var_atten_date.set(today)
        self.var_atten_time.set(now)

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

    def setup_database(self):
        try:
            conn = get_db_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Student_id VARCHAR(50),
                Student_name VARCHAR(100),
                Roll VARCHAR(50),
                Dep VARCHAR(100),
                Time VARCHAR(50),
                Date VARCHAR(50),
                Status VARCHAR(50)
            )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Database Setup Failed: {e}")

    def get_db_connection(self):
        return get_db_connection()

    def open_attendance_date_calendar(self):
        try:
            initial_date = datetime.datetime.strptime(self.var_atten_date.get(), "%d/%m/%Y").date()
        except:
            initial_date = datetime.date.today()
        def set_date(selected_date):
            self.var_atten_date.set(selected_date.strftime("%d/%m/%Y"))
        DatePickerDialog(self.root, initial_date, set_date)

    # ================= CRUD OPERATIONS (MySQL) =================

    def fetch_data(self, rows):
        self.attendence_table.delete(*self.attendence_table.get_children())
        for i in rows:
            display_data = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]) 
            self.attendence_table.insert('', END, values=display_data)

    def auto_load_data(self):
        global mydata
        mydata.clear()
        try:
            conn = self.get_db_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT * FROM attendance")
            rows = my_cursor.fetchall()
            for r in rows:
                mydata.append(r)
            self.fetch_data(mydata)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data: {e}")

    def add_data(self):
        if self.var_atten_id.get() == "" or self.var_atten_name.get() == "":
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return
        
        try:
            conn = self.get_db_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT * FROM attendance WHERE Student_id=%s AND Date=%s", 
                            (self.var_atten_id.get(), self.var_atten_date.get()))
            if my_cursor.fetchone():
                messagebox.showerror("Error", "Attendance already marked for this student today.", parent=self.root)
                conn.close()
                return

            my_cursor.execute("INSERT INTO attendance (Student_id, Student_name, Roll, Dep, Time, Date, Status) VALUES (%s,%s,%s,%s,%s,%s,%s)", (
                self.var_atten_id.get(),
                self.var_atten_name.get(),
                self.var_atten_roll.get(),
                self.var_atten_dept.get(),
                self.var_atten_time.get(),
                self.var_atten_date.get(),
                self.var_atten_status.get()
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Attendance Added Successfully", parent=self.root)
            self.auto_load_data()
            self.set_current_date_time()

        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self.root)

    def update_data(self):
        if self.var_atten_id.get() == "":
            messagebox.showerror("Error", "Student ID is required", parent=self.root)
            return

        # Check if a record was actually selected for update
        if self.attendance_id is None:
             messagebox.showerror("Error", "Please select a record from the table to update", parent=self.root)
             return

        confirm = messagebox.askyesno(
            "Confirm Update",
            "Are you sure you want to update this attendance record?",
            parent=self.root
        )

        if not confirm:
            return  # user clicked No

        try:
            conn = self.get_db_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("""
                UPDATE attendance 
                SET Student_id=%s, Student_name=%s, Roll=%s, Dep=%s, Time=%s, Date=%s, Status=%s 
                WHERE id=%s
            """, (
                self.var_atten_id.get(),
                self.var_atten_name.get(),
                self.var_atten_roll.get(),
                self.var_atten_dept.get(),
                self.var_atten_time.get(),
                self.var_atten_date.get(),
                self.var_atten_status.get(),
                self.attendance_id
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Attendance Updated Successfully", parent=self.root)
            self.auto_load_data()

        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self.root)

    def delete_data(self):
        if self.attendance_id is None:
            messagebox.showerror("Error", "Please select a record from the table to delete", parent=self.root)
            return
        
        try:
            delete = messagebox.askyesno("Delete", "Do you want to delete this record?", parent=self.root)
            if delete:
                conn = self.get_db_connection()
                my_cursor = conn.cursor()
                my_cursor.execute("DELETE FROM attendance WHERE id=%s", (self.attendance_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Deleted Successfully", parent=self.root)
                self.auto_load_data()
                self.reset_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self.root)

    def reset_data(self):
        self.var_atten_id.set("")
        self.var_atten_name.set("")
        self.var_atten_roll.set("")
        self.var_atten_dept.set("")
        self.var_atten_time.set("")
        self.var_atten_date.set("")
        self.var_atten_status.set("Status")
        self.attendance_id = None
        self.set_current_date_time()

    def get_cursor(self, event=None):
        cursor_row = self.attendence_table.focus()
        content = self.attendence_table.item(cursor_row)
        rows = content['values']
        if rows:
            self.attendance_id = rows[0] # Capture the hidden DB ID
            self.var_atten_id.set(rows[1])
            self.var_atten_name.set(rows[2])
            self.var_atten_roll.set(rows[3])
            self.var_atten_dept.set(rows[4])
            self.var_atten_time.set(rows[5])
            self.var_atten_date.set(rows[6])
            self.var_atten_status.set(rows[7])

    # ================= FILTERS, SORT & SEARCH =================

    def reset_search(self):
        self.var_search_entry.set("")
        self.var_search_combo.set("Select Option")
        self.active_filters = {
            "Status": [],
            "Department": [],
            "DateRange": []
        }
        self.auto_load_data()

    def advanced_search(self, event=None):
        search_txt = self.var_search_entry.get().lower()
        search_by = self.var_search_combo.get()
        
        col_map = {
            "Student_id": 1,
            "Name": 2,
            "Roll": 3,
            "Dep": 4,
            "Date": 6,
            "Status": 7
        }
        
        idx = col_map.get(search_by, 1)
        
        filtered = []
        for row in mydata:
            if search_txt in str(row[idx]).lower():
                filtered.append(row)
        
        self.fetch_data(filtered)

    def attendance_sort(self, col, reverse):
        col_type = self.attendance_columns[col]
        data = [(self.attendence_table.set(k, col), k) for k in self.attendence_table.get_children('')]
        
        def sort_key(item):
            value = item[0].strip()
            if col_type == int: return int(value) if value.isdigit() else 0
            elif col_type == 'date': 
                try:
                    return datetime.datetime.strptime(value, "%d/%m/%Y")
                except:
                    return datetime.datetime.min
            else: return value.lower()

        data.sort(key=sort_key, reverse=reverse)
        for index, (_, k) in enumerate(data): self.attendence_table.move(k, '', index)
        self.attendence_table.heading(col, command=lambda: self.attendance_sort(col, not reverse))

    def open_filter_window(self):
        win = Toplevel(self.root)
        win.title("Advanced Filters")
        win.geometry("380x480")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        try:
            win.iconbitmap(resource_path('college_images\\bg1.ico'))
        except:
            pass
        
        # ================= DEPARTMENT FILTER =================
        Label(win, text="Department", font=("times new roman", 11, "bold")).pack(anchor=W, padx=10, pady=(10, 5))
        
        dept_vars = {}
        for d in ("Computer", "IT", "Civil", "Mechenical"):
            v = BooleanVar(value=d in self.active_filters["Department"])
            dept_vars[d] = v
            Checkbutton(win, text=d, variable=v).pack(anchor=W, padx=25)

        # ================= STATUS FILTER =================
        Label(win, text="Attendance Status", font=("times new roman", 11, "bold")).pack(anchor=W, padx=10, pady=(10, 5))
        
        status_vars = {}
        for s in ("Present", "Absent"):
            v = BooleanVar(value=s in self.active_filters["Status"])
            status_vars[s] = v
            Checkbutton(win, text=s, variable=v).pack(anchor=W, padx=25)
            
        # ================= DATE FILTER =================
        Label(win, text="Date Range", font=("times new roman", 11, "bold")).pack(anchor=W, padx=10, pady=(10, 5))
        
        f_frame = Frame(win)
        f_frame.pack(fill=X, padx=25)
        Label(f_frame, text="From:", width=5).pack(side=LEFT)
        ttk.Entry(f_frame, textvariable=self.filter_from_date, width=15).pack(side=LEFT)
        Button(f_frame, text="📅", font=("Segoe UI Emoji", 9), cursor="hand2", bg="#3498db", fg="white", command=lambda: self.pick_date(self.filter_from_date)).pack(side=LEFT, padx=5)
        
        t_frame = Frame(win)
        t_frame.pack(fill=X, padx=25, pady=5)
        Label(t_frame, text="To:", width=5).pack(side=LEFT)
        ttk.Entry(t_frame, textvariable=self.filter_to_date, width=15).pack(side=LEFT)
        Button(t_frame, text="📅", font=("Segoe UI Emoji", 9), cursor="hand2", bg="#3498db", fg="white", command=lambda: self.pick_date(self.filter_to_date)).pack(side=LEFT, padx=5)

        # ================= BUTTONS =================
        btn_frame = Frame(win)
        btn_frame.pack(pady=20)
        
        Button(btn_frame, text="Apply Filters", bg="green", fg="white", width=15, 
               font=('times new roman', 10, 'bold'), cursor='hand2', 
               command=lambda: self.apply_filter(win, dept_vars, status_vars)).pack(side=LEFT, padx=5)
               
        Button(btn_frame, text="Clear Filters", bg="red", fg="white", width=15, 
               font=('times new roman', 10, 'bold'), cursor='hand2', 
               command=lambda: self.clear_filter(win)).pack(side=LEFT, padx=5)

    def pick_date(self, var):
        try:
            initial = datetime.datetime.strptime(var.get(), "%d/%m/%Y").date()
        except:
            initial = datetime.date.today()
        def set_d(d): var.set(d.strftime('%d/%m/%Y'))
        DatePickerDialog(self.root, initial, set_d)

    def apply_filter(self, win, dept_vars, status_vars):
        # 1. Update Active Filters
        self.active_filters["Department"] = [k for k, v in dept_vars.items() if v.get()]
        self.active_filters["Status"] = [k for k, v in status_vars.items() if v.get()]
        
        # 2. Start with full data (Reload global mydata ensures we filter from source)
        # Note: If database is large, fetching all and filtering in Python is slow.
        # But since mydata is already loaded, we filter memory for speed.
        filtered = mydata.copy()
        
        # 3. Filter by Department
        if self.active_filters["Department"]:
            filtered = [r for r in filtered if r[4] in self.active_filters["Department"]] # Index 4 is Dep
            
        # 4. Filter by Status
        if self.active_filters["Status"]:
            filtered = [r for r in filtered if r[7] in self.active_filters["Status"]] # Index 7 is Status
            
        # 5. Filter by Date Range
        f_date = self.filter_from_date.get()
        t_date = self.filter_to_date.get()
        
        if f_date and t_date:
            try:
                fd = datetime.datetime.strptime(f_date, "%d/%m/%Y")
                td = datetime.datetime.strptime(t_date, "%d/%m/%Y")
                
                if td < fd:
                    messagebox.showerror("Error", "'To Date' must be ahead of or equal to 'From Date'", parent=win)
                    return
                
                date_filtered = []
                for r in filtered:
                    try:
                        rd = datetime.datetime.strptime(r[6], "%d/%m/%Y") # Index 6 is Date
                        if fd <= rd <= td:
                            date_filtered.append(r)
                    except: pass # Skip invalid dates
                filtered = date_filtered
            except Exception as e:
                messagebox.showerror("Date Error", "Invalid Date Format", parent=win)
                return

        self.fetch_data(filtered)
        win.destroy()

    def clear_filter(self, win):
        self.active_filters = {
            "Status": [],
            "Department": [],
            "DateRange": []
        }
        self.filter_from_date.set("")
        self.filter_to_date.set("")
        self.auto_load_data()
        win.destroy()

    # ================= REPORT / OTHERS =================

    def plot_attendance_graph(self):
        report_data = [list(r[1:]) for r in mydata]
        if not report_data:
            messagebox.showerror("No Data", "No data available for report")
            return
        DetailedAttendanceReport(self.root, report_data)

    def inform(self):
        self.new_window = Toplevel(self.root)
        self.app = Inform(self.new_window)

    def update_time(self):
        if self.root.winfo_exists():
            current_time = strftime('%I:%M:%S %p')
            self.time_lbl.config(text=current_time)
            self.time_lbl.after(1000, self.update_time)

    def back(self):
        self.root.destroy()

    # ================== RESIZING LOGIC ==================
    def on_resize(self, event):
        """Variable delay to prevent lag while dragging"""
        if event.widget == self.root:
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            self.resize_timer = self.root.after(100, self.update_layout_images)

    def update_layout_images(self):
        """Resizes background and header images and handles Z-order"""
        # Get current dimensions
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        
        if win_w < 100 or win_h < 100: return
        
        # 1. Header Images
        h_h = int(win_h * 0.25) # 170/680 = 0.25
        h_w_1 = int(win_w * 0.46) # 625/1360 approx 0.46
        # h_w_2 = remainder
        
        # Helper to update label image
        def update_img(lbl, orig, w, h):
            if w<=0 or h<=0: return
            try:
                resized = orig.resize((w, h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized)
                lbl.config(image=photo)
                lbl.image = photo 
            except Exception as e:
                pass
            
        if hasattr(self, 'h_lbl1') and hasattr(self, 'org_img_h1'):
            update_img(self.h_lbl1, self.org_img_h1, h_w_1, h_h)
            
        if hasattr(self, 'h_lbl2') and hasattr(self, 'org_img_h2'):
            # Calculate remaining width to avoid gaps
            h_w_2 = win_w - h_w_1
            update_img(self.h_lbl2, self.org_img_h2, h_w_2, h_h)
        
        # 2. Background Image
        bg_h = int(win_h * 0.75) # 510/680 = 0.75
        if hasattr(self, 'bg_lbl') and hasattr(self, 'org_img_bg'):
            update_img(self.bg_lbl, self.org_img_bg, win_w, bg_h)
        
        # 3. Inner Frame Image (left_frame image)
        if hasattr(self, 'f_lbl_left') and hasattr(self, 'org_img_left'):
            try:
                self.f_lbl_left.update_idletasks()
                lf_w = self.f_lbl_left.winfo_width()
                lf_h = self.f_lbl_left.winfo_height()
                if lf_w > 10 and lf_h > 10:
                    update_img(self.f_lbl_left, self.org_img_left, lf_w, lf_h)
            except:
                pass
            
        # 3. Z-Order Lifting (Critical for visibility)
        if hasattr(self, 'title_lbl'): self.title_lbl.lift()
        if hasattr(self, 'time_lbl'): self.time_lbl.lift()
        if hasattr(self, 'back_btn_frame'): self.back_btn_frame.lift()
        
        # Force a redraw
        self.root.update_idletasks()

    def check_attendance_alert(self):
        try:
            from notifications import LowAttendanceNotifier
            notifier = LowAttendanceNotifier()
            messagebox.showinfo("Processing", "Checking attendance levels and sending alerts (Email/Telegram)... This happens in background.",parent=self.root)
            
            def notify_callback(result):
                messagebox.showinfo("Attendance Alert Result", result,parent=self.root)
                
            notifier.check_and_notify_threaded(notify_callback)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to allow threaded check: {e}",parent=self.root)

if __name__ == '__main__':
    root = Tk()
    obj = attendance(root)
    root.mainloop()