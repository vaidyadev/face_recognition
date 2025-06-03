from time import strftime
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import os
import csv
from tkinter import filedialog
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.cm as cm
import numpy as np
from informing import Inform


mydata=[]
class attendance:
    def __init__(self, root):
        
        self.root = root
        self.root.geometry("1360x680+0+0")
        # self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(False, False)
        self.root.wm_iconbitmap('college_images\\bg1.ico')
    ################Text Variable#######################################
        self.var_atten_id=StringVar()
        self.var_atten_name=StringVar()
        self.var_atten_roll=StringVar()
        self.var_atten_dept=StringVar()
        self.var_atten_time=StringVar()
        self.var_atten_date=StringVar()
        self.var_atten_status=StringVar()

        img = Image.open("college_images\\smart-attendance.jpg")
        img = img.resize((625, 170), Image.Resampling.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)
        f_lbl = Label(self.root, image=self.photoimg)
        f_lbl.place(x=0, y=0, width=625, height=170)

        img1 = Image.open("college_images\\12.jpg")
        img1 = img1.resize((735, 170), Image.Resampling.LANCZOS)
        self.photoimg1 = ImageTk.PhotoImage(img1)
        f_lbl1 = Label(self.root, image=self.photoimg1)
        f_lbl1.place(x=625, y=0, width=735, height=170)

        #background
        img3 = Image.open("college_images\\wp2551980.jpg")
        img3 = img3.resize((1360, 560), Image.Resampling.LANCZOS)
        self.photoimg3 = ImageTk.PhotoImage(img3)
        bg_img = Label(self.root, image=self.photoimg3)
        bg_img.place(x=0, y=170, width=1360, height=510)

        self.title_lbl = Label(bg_img, text='ATTENDANCE MANAGEMENT SYSTEM', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(x=0, y=0, width=1360, height=45)

        self.time_lbl = Label(bg_img, font=('times new roman', 15, 'bold'), bg='white', fg='red',borderwidth=0,highlightthickness=0)
        self.time_lbl.place(x=0, y=0, width=120, height=45)
        self.update_time()  # start the clock

        back_btn=Button(self.title_lbl,text="Back",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), bg='red', fg='white',activebackground="green",command=self.back)
        back_btn.place(x=1150,y=10,height=25)

        # FRAME 
        main_frame=Frame(bg_img,bd=2)
        main_frame.place(x=10,y=50,width=1330,height=460)

      
    # left_label frame
        left_frame=LabelFrame(main_frame,bd=2,bg='white',relief=RIDGE,text='Students Attendance Details',font=('times new roman', 12, 'bold'))
        left_frame.place(x=10,y=10,width=645,height=440)
       
        img_left = Image.open("college_images\\face-recognition.png")
        img_left = img_left.resize((635, 90), Image.Resampling.LANCZOS)
        self.left_photoimg = ImageTk.PhotoImage(img_left)
        f_lbl = Label(left_frame, image=self.left_photoimg)
        f_lbl.place(x=5, y=0, width=635, height=90)
    # left inside frame
        left_inside_frame=Frame(left_frame,bd=2,relief=RIDGE,bg='white')
        left_inside_frame.place(x=0,y=95,width=640,height=350)

    # label and entry
    #attendance
        attendance_id_label=Label(left_inside_frame,text='AttendenceId :',font=('times new roman', 12, 'bold'),bg='white')
        attendance_id_label.grid(row=0,column=0,padx=5,sticky=W)

        attendanceid_entry=ttk.Entry(left_inside_frame,width=15,font=('times new roman', 15, 'bold'),textvariable=self.var_atten_id)
        attendanceid_entry.grid(row=0,column=1,padx=5,pady=3,sticky=W)

     #Name
        name_label=Label(left_inside_frame,text='Name :',font=('times new roman', 12, 'bold'),bg='white')
        name_label.grid(row=0,column=3,padx=5,sticky=W)

        name_entry=ttk.Entry(left_inside_frame,width=15,font=('times new roman', 15, 'bold'),textvariable=self.var_atten_name)
        name_entry.grid(row=0,column=4,padx=5,pady=3,sticky=W)
    
     #Roll
        roll_label=Label(left_inside_frame,text='Roll NO :',font=('times new roman', 12, 'bold'),bg='white')
        roll_label.grid(row=1,column=0,padx=5,sticky=W)

        roll_entry=ttk.Entry(left_inside_frame,width=15,font=('times new roman', 15, 'bold'),textvariable=self.var_atten_roll)
        roll_entry.grid(row=1,column=1,padx=5,pady=3,sticky=W)
    #Department
        department_label=Label(left_inside_frame,text='Department :',font=('times new roman', 12, 'bold'),bg='white')
        department_label.grid(row=1,column=3,padx=5,sticky=W)

        department_entry=ttk.Entry(left_inside_frame,width=15,font=('times new roman', 15, 'bold'),textvariable=self.var_atten_dept)
        department_entry.grid(row=1,column=4,padx=5,pady=3,sticky=W)
     #Time
        time_label=Label(left_inside_frame,text='Time :',font=('times new roman', 12, 'bold'),bg='white')
        time_label.grid(row=2,column=0,padx=5,sticky=W)

        time_entry=ttk.Entry(left_inside_frame,width=15,font=('times new roman', 15, 'bold'),textvariable=self.var_atten_time)
        time_entry.grid(row=2,column=1,padx=5,pady=3,sticky=W)
    #Date
        date_label=Label(left_inside_frame,text='Date :',font=('times new roman', 12, 'bold'),bg='white')
        date_label.grid(row=2,column=3,padx=5,sticky=W)

        date_entry=ttk.Entry(left_inside_frame,width=15,font=('times new roman', 15, 'bold'),textvariable=self.var_atten_date)
        date_entry.grid(row=2,column=4,padx=5,pady=3,sticky=W)

    #Attandence status
        staus_label=Label(left_inside_frame,text='Attandence status :',font=('times new roman', 12, 'bold'),bg='white')
        staus_label.grid(row=3,column=0,padx=5,sticky=W)

        status_combo=ttk.Combobox(left_inside_frame,font=('times new roman', 12, 'bold'),width=18,state='read',textvariable=self.var_atten_status)
        status_combo['values']=('Present','Absent')
        status_combo.set('Status')
        status_combo.grid(row=3,column=1,padx=5,pady=5,sticky=W)
    # button frame
    
        btn_frame=Frame(left_inside_frame,bd=2,relief=RIDGE,bg='white')
        btn_frame.place(x=0,y=250,width=635,height=35)

        import_btn=Button(btn_frame,text="Import Csv",width=17,cursor='hand2',font=('times new roman', 11, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.import_csv)
        import_btn.grid(row=0,column=0)

        export_btn=Button(btn_frame,text="Export Csv",width=17,cursor='hand2',font=('times new roman', 11, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.export_csv)
        export_btn.grid(row=0,column=1)

        update_btn=Button(btn_frame,text="Update",width=16,cursor='hand2',font=('times new roman', 11, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.update_data)
        update_btn.grid(row=0,column=2)

        reset_btn=Button(btn_frame,text="Reset",width=16,cursor='hand2',font=('times new roman', 11, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.reset_data)
        reset_btn.grid(row=0,column=3)

        btn_frame1=Frame(left_inside_frame,bd=2,relief=RIDGE,bg='white')
        btn_frame1.place(x=0,y=285,width=635,height=35)

        inform_btn=Button(btn_frame1,text="Inform Students",width=29,cursor='hand2',font=('times new roman', 14, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.inform)
        inform_btn.grid(row=0,column=0)

        report_btn=Button(btn_frame1,text="Attendance Report",width=29,cursor='hand2',font=('times new roman', 14, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.plot_attendance_graph)
        report_btn.grid(row=0,column=1)
     # right_label frame
        right_frame=LabelFrame(main_frame,bd=2,bg='white',relief=RIDGE,text='Attendance Details',font=('times new roman', 12, 'bold'))
        right_frame.place(x=665,y=10,width=645,height=440)

        table_frame1=Frame(right_frame,bd=2,relief=RIDGE,bg='white')
        table_frame1.place(x=0,y=5,width=635,height=410)

        scroll_x=ttk.Scrollbar(right_frame,orient=HORIZONTAL)
        scroll_y=ttk.Scrollbar(right_frame,orient=VERTICAL)
        self.attendence_table=ttk.Treeview(right_frame,column=('id','name','roll','department','time','date','attendance'),xscrollcommand=scroll_x.set,yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM,fill=X)
        scroll_y.pack(side=RIGHT,fill=Y)
        scroll_x.config(command=self.attendence_table.xview)
        scroll_y.config(command=self.attendence_table.yview)

        self.attendence_table.heading('id',text='Attendance ID')
        self.attendence_table.heading('name',text='StudentName')
        self.attendence_table.heading('roll',text='Roll No')
        self.attendence_table.heading('department',text='Department')
        self.attendence_table.heading('time',text='Arriving Time')
        self.attendence_table.heading('date',text='Arriving Date')
        self.attendence_table.heading('attendance',text='Attendance Status')
        self.attendence_table['show']='headings'


        self.attendence_table.column('id',width=100)
        self.attendence_table.column('name',width=100)
        self.attendence_table.column('roll',width=100)
        self.attendence_table.column('department',width=100)
        self.attendence_table.column('time',width=100)
        self.attendence_table.column('date',width=100)
        self.attendence_table.column('attendance',width=105)

        self.attendence_table.pack(fill=BOTH,expand=1)
        self.attendence_table.bind('<ButtonRelease>',self.get_cursor)
#############################fetch data########################
    def fetch_data(self,rows):
        self.attendence_table.delete(*self.attendence_table.get_children())
        for i in rows:
            self.attendence_table.insert('',END,values=i)
############Import csv#################
    def import_csv(self):
        global mydata
        mydata.clear()
        file_name=filedialog.askopenfilename(initialdir=os.getcwd(),title="Open Csv",filetypes=(("Csv","*.csv"),('Excel','.*.xlsx'),("All Files","*.*")),defaultextension='.csv',parent=self.root)
        self.imported_file = file_name  # Store file path for update
        if not file_name:
            return
        with open (file_name)as f1:
            csvread=csv.reader(f1,delimiter=',')
            for i in csvread:
                mydata.append(i)
            self.fetch_data(mydata)
###########Export csv######################
    def export_csv(self):
        try:
            if len(mydata)<1:
                messagebox.showerror("No Data",'No Data Found To Export',parent=self.root)
                return False
            file_name=filedialog.asksaveasfilename(initialdir=os.getcwd(),title="Save Csv",filetypes=(("Csv","*.csv"),('Excel','*.xlsx'),("All Files","*.*")),defaultextension='.csv',parent=self.root)
            if not file_name:
                return False  
            with open (file_name,mode='w',newline='') as f1:
                exp_write=csv.writer(f1,delimiter=',')
                for i in mydata:
                    exp_write.writerow(i)
                messagebox.showinfo('Data Exported','Your data is succesfully exported to '+ os.path.basename(file_name) + ' successfully',parent=self.root)
        except Exception as e:
            messagebox.showerror('Error',f'Failed to export data due to {str(e)}',parent=self.root)
    def get_cursor(self,event=''):
        cursor_row=self.attendence_table.focus()
        content=self.attendence_table.item(cursor_row)
        rows=content['values']
        self.var_atten_id.set(rows[0])
        self.var_atten_name.set(rows[1])
        self.var_atten_roll.set(rows[2])
        self.var_atten_dept.set(rows[3])
        self.var_atten_time.set(rows[4])
        self.var_atten_date.set(rows[5])
        self.var_atten_status.set(rows[6])
    def reset_data(self):
        self.var_atten_id.set('')
        self.var_atten_name.set('')
        self.var_atten_roll.set('')
        self.var_atten_dept.set('')
        self.var_atten_time.set('')
        self.var_atten_date.set('')
        self.var_atten_status.set('Status')
    def update_data(self):
          try:
            selected = self.attendence_table.focus()
            if not selected:
                messagebox.showerror("Error", "Please select a record to update.",parent=self.root)
                return
            self.attendence_table.item(selected, values=(
                self.var_atten_id.get(),
                self.var_atten_name.get(),
                self.var_atten_roll.get(),
                self.var_atten_dept.get(),
                self.var_atten_time.get(),
                self.var_atten_date.get(),
                self.var_atten_status.get(),
            ))
            if not hasattr(self, 'imported_file') or not self.imported_file:
                messagebox.showerror("Error", "No imported file found to update.", parent=self.root)
                return
            with open(self.imported_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                for row_id in self.attendence_table.get_children():
                    row = self.attendence_table.item(row_id)['values']
                    writer.writerow(row)
            messagebox.showinfo("Success", f"CSV file updated: {os.path.basename(self.imported_file)}", parent=self.root)
          except Exception as e:
                messagebox.showerror("Error", f"Failed to update CSV file: due to {str(e)}", parent=self.root)

   

   

    def plot_attendance_graph(self):
        # Check if there's any data to plot
        if len(mydata) < 1:
            messagebox.showerror("Error", "No data to plot", parent=self.root)
            return

        # Dictionary to count number of 'Present' days per student
        attendance_count = defaultdict(int)

        # Loop through each row in imported CSV data
        for row in mydata:
            # Ensure the row has at least 7 columns and status is 'Present'
            if len(row) >= 7 and row[6].strip().lower() == 'present':
                name = row[1]  # Use student name (column 2); you could use roll number (row[2]) instead
                attendance_count[name] += 1  # Increment count for this student

        # If no 'Present' status found, show info message and exit
        if not attendance_count:
            messagebox.showinfo("Info", "No 'Present' records found to plot.", parent=self.root)
            return

        # Get student names and their respective present counts
        names = list(attendance_count.keys())
        counts = list(attendance_count.values())
        # Generate a colormap with a different color for each bar
        colors = cm.get_cmap('tab10', len(names))  # You can use 'tab20', 'Set3', etc.
        


        
       # Set figure windows position
        maneger=plt.get_current_fig_manager()
       #configure arriving position
        maneger.window.wm_geometry('+200+100')
        
        # Create the bar graph
        bars = plt.bar(names, counts, color=[colors(i) for i in range(len(names))])

        # Label the x-axis
        plt.xlabel('Student Name')

        # Label the y-axis
        plt.ylabel('Number of Days Present')

        # Set the title of the graph
        plt.title('Student Attendance Report')

        # Rotate x-axis labels to avoid overlap
        plt.xticks(rotation=45, ha='right')

        # Adjust layout to prevent clipping
        plt.tight_layout()

        # Show the plot window
        plt.show()

    def back(self):
        self.root.destroy()

    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.time_lbl.config(text=current_time)
        self.time_lbl.after(1000, self.update_time)  # call again after 1 second

    def inform(self):
         self.new_window=Toplevel(self.root)
         self.app=Inform(self.new_window)
        

        


       
if __name__ == '__main__':
    root=Tk()
    obj=attendance(root)
    root.mainloop() 