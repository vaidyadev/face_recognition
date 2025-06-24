from time import strftime
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import mysql.connector
import cv2
# open source computer vision librabry full form of opencv


class students:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1360x680+0+0")
        self.root.title("Face Recognition System")
        self.root.resizable(False, False)
        self.root.wm_iconbitmap('college_images\\bg1.ico')

        ###################variables############################
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


        


        # Proceed with images and title label setup
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

    #background image
        img3 = Image.open("college_images\\wp2551980.jpg")
        img3 = img3.resize((1360, 560), Image.Resampling.LANCZOS)
        self.photoimg3 = ImageTk.PhotoImage(img3)
        bg_img = Label(self.root, image=self.photoimg3)
        bg_img.place(x=0, y=131, width=1360, height=560)

        self.title_lbl = Label(bg_img, text='STUDENT MANAGEMENT SYSTEM', font=('times new roman', 35, 'bold'), bg='white', fg='green')
        self.title_lbl.place(x=0, y=0, width=1360, height=45)

        back_btn=Button(self.title_lbl,text="Back",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), bg='red', fg='white',activebackground="green",command=self.back)
        back_btn.place(x=1150,y=10,height=25)

        self.time_lbl = Label(bg_img, font=('times new roman', 15, 'bold'), bg='white', fg='red',borderwidth=0,highlightthickness=0)
        self.time_lbl.place(x=0, y=0, width=120, height=45)
        self.update_time()  # start the clock


    # FRAME 
        main_frame=Frame(bg_img,bd=2)
        main_frame.place(x=10,y=50,width=1330,height=480)

      
    # left_label frame
        left_frame=LabelFrame(main_frame,bd=2,bg='white',relief=RIDGE,text='Students Details',font=('times new roman', 12, 'bold'))
        left_frame.place(x=10,y=10,width=645,height=460)
        img_left = Image.open("college_images\\AdobeStock_303989091.jpeg")
        img_left = img_left.resize((635, 130), Image.Resampling.LANCZOS)
        self.left_photoimg = ImageTk.PhotoImage(img_left)
        f_lbl = Label(left_frame, image=self.left_photoimg)
        f_lbl.place(x=5, y=0, width=635, height=80)

        # current course
        current_course_frame=LabelFrame(left_frame,bd=2,bg='white',relief=RIDGE,text='Current Course Information',font=('times new roman', 12, 'bold'))
        current_course_frame.place(x=5,y=85,width=635,height=90)
        # department
        dep_label=Label(current_course_frame,text='Department',font=('times new roman', 12, 'bold'),bg='white')
        dep_label.grid(row=0,column=0,padx=5,sticky=W)

        dep_combo=ttk.Combobox(current_course_frame,font=('times new roman', 12, 'bold'),width=17,textvariable=self.var_dep,state='read')
        dep_combo['values']=('Computer','IT','Civil','Mechenical')
        dep_combo.set("Select Department")
        dep_combo.grid(row=0,column=1,padx=2,pady=5,sticky=W)
        # Course
        course_label=Label(current_course_frame,text='Course',font=('times new roman', 12, 'bold'),bg='white')
        course_label.grid(row=0,column=2,padx=5,sticky=W)

        course_combo=ttk.Combobox(current_course_frame,font=('times new roman', 12, 'bold'),textvariable=self.var_course,width=17,state='read')
        course_combo['values']=('BCA','S.E.','T.E.','B.E.')
        course_combo.set("Select Course")
        course_combo.grid(row=0,column=3,padx=2,pady=5,sticky=W)
        # year
        year_label=Label(current_course_frame,text='Year',font=('times new roman', 12, 'bold'),bg='white')
        year_label.grid(row=1,column=0,padx=5,sticky=W)

        year_combo=ttk.Combobox(current_course_frame,font=('times new roman', 12, 'bold'),textvariable=self.var_year,width=17,state='read')
        year_combo['values']=('2023-24','2024-25','2025-26','2026-27')
        year_combo.set("Select Year")
        year_combo.grid(row=1,column=1,padx=2,pady=5,sticky=W)
        # Semester
        semester_label=Label(current_course_frame,text='Semester',font=('times new roman', 12, 'bold'),bg='white')
        semester_label.grid(row=1,column=2,padx=5,sticky=W)

        semester_combo=ttk.Combobox(current_course_frame,font=('times new roman', 12, 'bold'),textvariable=self.var_semester,width=17,state='read')
        semester_combo['values']=('Semester 1','Semester-2')
        semester_combo.set("Select Semester")
        semester_combo.grid(row=1,column=3,padx=2,pady=5,sticky=W)

     #  class student information
        class_student_frame=LabelFrame(left_frame,bd=2,bg='white',relief=RIDGE,text='Class Student Information',font=('times new roman', 12, 'bold'))
        class_student_frame.place(x=5,y=180,width=635,height=255)
    # student id

        student_id_label=Label(class_student_frame,text='StudentId :',font=('times new roman', 12, 'bold'),bg='white')
        student_id_label.grid(row=0,column=0,padx=5,sticky=W)

        studentid_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),
                                  textvariable=self.va_std_id)
        studentid_entry.grid(row=0,column=1,padx=5,pady=3,sticky=W)
        
    # student name
        studentname_label=Label(class_student_frame,text='StudentName :',font=('times new roman', 12, 'bold'),bg='white')
        studentname_label.grid(row=0,column=2,padx=5,sticky=W)

        studentname_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold')
                                    ,textvariable=self.var_std_name)
        studentname_entry.grid(row=0,column=3,padx=5,pady=3,sticky=W)
    # class division
        class_div_label=Label(class_student_frame,text='Class Division :',font=('times new roman', 12, 'bold'),bg='white')
        class_div_label.grid(row=1,column=0,padx=5,sticky=W)

        div_combo=ttk.Combobox(class_student_frame,font=('times new roman', 12, 'bold'),textvariable=self.var_div,width=18,state='read')
        div_combo['values']=('A','B','C','D')
        div_combo.set('Select Division')
        div_combo.grid(row=1,column=1,padx=5,pady=5,sticky=W)
    # roll no
        rollno_label=Label(class_student_frame,text='Roll NO :',font=('times new roman', 12, 'bold'),bg='white')
        rollno_label.grid(row=1,column=2,padx=5,sticky=W)

        rollno_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_roll)
        rollno_entry.grid(row=1,column=3,padx=5,pady=3,sticky=W)
    # Gender
        gender_label=Label(class_student_frame,text='Gender :',font=('times new roman', 12, 'bold'),bg='white')
        gender_label.grid(row=2,column=0,padx=5,sticky=W)

        gender_combo=ttk.Combobox(class_student_frame,font=('times new roman', 12, 'bold'),textvariable=self.var_gender,width=18,state='read')
        gender_combo['values']=("Male",'Female','Other')
        gender_combo.set('Select Gender')
        gender_combo.grid(row=2,column=1,padx=5,pady=5,sticky=W)

    # Dob
        dob_label=Label(class_student_frame,text='DOB :',font=('times new roman', 12, 'bold'),bg='white')
        dob_label.grid(row=2,column=2,padx=5,sticky=W)

        dob_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_dob)
        dob_entry.grid(row=2,column=3,padx=5,pady=3,sticky=W)
    # Email
        email_label=Label(class_student_frame,text='Email :',font=('times new roman', 12, 'bold'),bg='white')
        email_label.grid(row=3,column=0,padx=5,sticky=W)

        email_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_email)
        email_entry.grid(row=3,column=1,padx=5,pady=3,sticky=W)
    # Phone no
        phono_label=Label(class_student_frame,text='Phone NO :',font=('times new roman', 12, 'bold'),bg='white')
        phono_label.grid(row=3,column=2,padx=5,sticky=W)

        phono_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_phone)
        phono_entry.grid(row=3,column=3,padx=5,pady=3,sticky=W)
    # Address
        address_label=Label(class_student_frame,text='Address :',font=('times new roman', 12, 'bold'),bg='white')
        address_label.grid(row=4,column=0,padx=5,sticky=W)

        address_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_address)
        address_entry.grid(row=4,column=1,padx=5,pady=3,sticky=W)
    # Teacher Name
        teacher_label=Label(class_student_frame,text='Teacher Name :',font=('times new roman', 12, 'bold'),bg='white')
        teacher_label.grid(row=4,column=2,padx=5,sticky=W)

        teacher_entry=ttk.Entry(class_student_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_teacher)
        teacher_entry.grid(row=4,column=3,padx=5,pady=3,sticky=W)
    # radio buttons

        self.var_radio1=StringVar()
        radiobutton1=ttk.Radiobutton(class_student_frame,variable=self.var_radio1,text='Take Photo Sample',value='yes')
        radiobutton1.grid(row=6,column=0)

        radiobutton2=ttk.Radiobutton(class_student_frame,variable=self.var_radio1,text='No Photo Sample',value='no')
        radiobutton2.grid(row=6,column=1)

        
    # button frame
        btn_frame=Frame(class_student_frame,bd=2,relief=RIDGE,bg='white')
        btn_frame.place(x=0,y=180,width=635,height=25)

        save_btn=Button(btn_frame,text="Save",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.add_data)
        save_btn.grid(row=0,column=0)

        update_btn=Button(btn_frame,text="Update",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.update_data)
        update_btn.grid(row=0,column=1)

        delete_btn=Button(btn_frame,text="Delete",width=22,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.delete_data)
        delete_btn.grid(row=0,column=2)


        reset_btn=Button(btn_frame,text="Reset",width=20,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.reset_data)
        reset_btn.grid(row=0,column=3)

        btn_frame1=Frame(class_student_frame,bd=2,relief=RIDGE,bg='white')
        btn_frame1.place(x=0,y=205,width=635,height=25)

        take_photo_btn=Button(btn_frame1,text="Take Photo Sample",width=45,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.photo_sample,padx=(1.9))
        take_photo_btn.grid(row=1,column=0)

        update_photo_btn=Button(btn_frame1,text="Update Photo Sample",width=45,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.update_photosample)
        update_photo_btn.grid(row=1,column=1)

        
    





    # right_label frame
        right_frame=LabelFrame(main_frame,bd=2,bg='white',relief=RIDGE,text='Students Details',font=('times new roman', 12, 'bold'))
        right_frame.place(x=665,y=10,width=645,height=460)

        img_right = Image.open("college_images\\student.jpg")
        img_right = img_right.resize((635, 130), Image.Resampling.LANCZOS)
        self.right_photoimg = ImageTk.PhotoImage(img_right)
        f_lbl3 = Label(right_frame, image=self.right_photoimg)
        f_lbl3.place(x=5, y=0, width=635, height=80)

    #######################search system ############################
        search_frame=LabelFrame(right_frame,bd=2,bg='white',relief=RIDGE,text='Search System',font=('times new roman', 12, 'bold'))
        search_frame.place(x=5,y=85,width=635,height=55)
        search_label=Label(search_frame,text='Search By :',font=('times new roman', 12, 'bold'),bg='red',fg='white')
        search_label.grid(row=0,column=0,padx=5,sticky=W)

        search_combo=ttk.Combobox(search_frame,font=('times new roman', 12, 'bold'),width=12,state='read',textvariable=self.var_search_combo)
        search_combo['values']=('Roll_No','Phone_No','department')
        search_combo.set("Select Option")
        search_combo.grid(row=0,column=1,padx=2,sticky=W)

        search_entry=ttk.Entry(search_frame,width=20,font=('times new roman', 12, 'bold'),textvariable=self.var_search_entry)
        search_entry.grid(row=0,column=2,padx=5,pady=3,sticky=W)

        search_btn=Button(search_frame,text="Search",width=14,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.search_data)
        search_btn.grid(row=0,column=3,padx=3)

        showall_btn=Button(search_frame,text="Show All",width=14,cursor='hand2',font=('times new roman', 10, 'bold'), bg='darkblue', fg='white',activebackground="red",activeforeground='green',command=self.fetch_data)
        showall_btn.grid(row=0,column=4,padx=3)

        table_frame=Frame(right_frame,bd=2,bg='white',relief=RIDGE)
        table_frame.place(x=5,y=140,width=635,height=290)

        scroll_x=ttk.Scrollbar(table_frame,orient=HORIZONTAL)
        scroll_y=ttk.Scrollbar(table_frame,orient=VERTICAL)
        
        self.student_table=ttk.Treeview(table_frame,column=('dep','course','year','sem','id','name','div','roll','gender','dob','email','phone','address','teacher','photo'),xscrollcommand=scroll_x.set,yscrollcommand=scroll_y.set)
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
        

        self.student_table.pack(fill=BOTH,expand=1)
        self.student_table.bind('<ButtonRelease>',self.get_cursor)
        self.fetch_data()

        ######################Function declaration############################
    ###################add data to db when save is clicked###################
    def add_data(self):
        email = self.var_email.get()
        if self.var_dep.get()=='Select Department' or self.var_std_name.get()=='' or self.va_std_id.get()=='' or self.var_course.get()=='Select Course' or self.var_year.get()=='Select Year' or self.var_semester.get()=='Select Semester' or self.var_div.get()=='Select Division' or self.var_gender.get()=='Select Gender' or self.var_roll.get()==''or self.var_email.get()=='' or self.var_dob.get()==''or self.var_phone.get()=='' or self.var_address.get()=='' or self.var_teacher.get()=='' or self.var_radio1.get()=='':
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
                conn=mysql.connector.connect(host='localhost',username='root',password='1582',database='face_recognizer')
                my_cursor=conn.cursor()
                my_cursor.execute('insert into student values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                                (self.var_dep.get(),
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
                                self.var_address.get(),
                                self.var_teacher.get(),
                                self.var_radio1.get()))
                conn.commit()
                self.fetch_data()
                conn.close()
                messagebox.showinfo("Succes",'Student details has been added Succesfully',parent=self.root)
            except Exception as e:
                messagebox.showerror('Error',f'Student details failed to be added due to {str(e)}',parent=self.root)

        ##########################Fetch data################################
    ####################fetch data and display it on tree view table area###############
    def fetch_data(self):
        
        conn = mysql.connector.connect(host='localhost', username='root', password='1582', database='face_recognizer')
        my_cursor = conn.cursor()  
        my_cursor.execute('select * from student')
        data = my_cursor.fetchall()  # Fetch all rows from the result

        # If there is data in the table
        if(len(data) != 0):
            # Clear all existing data from the GUI table (Treeview)
            self.student_table.delete(*self.student_table.get_children())

            # Insert each row into the GUI table
            for i in data:
                self.student_table.insert('', END, values=i)

            conn.commit()  
        conn.close() 
    ########################## get cursor############################
    #Whenever user clicked on textarea it will set corresponding value in entry field on click release###
    def get_cursor(self,event=''):
        cursor_focus=self.student_table.focus()
        content=self.student_table.item(cursor_focus)
        data=content['values']
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

    ###############Update function##############
    def update_data(self):
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
                update=messagebox.askyesno("Update",'Do you want to update data',parent=self.root)
                if update>0:
                    conn=mysql.connector.connect(host='localhost',username='root',password='1582',database='face_recognizer')
                    my_cursor=conn.cursor()
                    my_cursor.execute('update student set Dep=%s,Course=%s,Year=%s,Semester=%s,Student_name=%s,Division=%s,Roll=%s,Gender=%s,Dob=%s,Email=%s,Phone=%s,Address=%s,Teacher=%s,PhotoSample=%s where Student_id=%s',(
                                self.var_dep.get(),
                                self.var_course.get(),
                                self.var_year.get(),
                                self.var_semester.get(),
                                self.var_std_name.get(),
                                self.var_div.get(),
                                self.var_roll.get(),
                                self.var_gender.get(),
                                self.var_dob.get(),
                                self.var_email.get(),
                                self.var_phone.get(),
                                self.var_address.get(),
                                self.var_teacher.get(),
                                self.var_radio1.get(),
                                self.va_std_id.get()))
                else:
                    if not update:
                        return
                messagebox.showinfo("Succes",'Student details has been Updated Succesfully',parent=self.root)
                conn.commit()
                self.fetch_data()
                conn.close()

                    
            except Exception as e:
                messagebox.showerror('Error',f'Student details failed to be Updated due to {str(e)}',parent=self.root)
    ############Delete function################
    def delete_data(self):
        if self.va_std_id.get()=='':
             messagebox.showerror("Error","Student id must be required",parent=self.root)
        else:
            try:
                delete=messagebox.askyesno("Delete",'Do you want to delete data',parent=self.root)
                if delete>0:
                    conn=mysql.connector.connect(host='localhost',username='root',password='1582',database='face_recognizer')
                    my_cursor=conn.cursor()
                    sql='delete from student where Student_id=%s'
                    val=(self.va_std_id.get(),)
                    my_cursor.execute(sql,val)
                else:
                    if not delete:
                        return
                conn.commit()
                messagebox.showinfo("Succes",'Student details has been Deleted Succesfully',parent=self.root)
                self.fetch_data()
                conn.close()


            except Exception as e:
                messagebox.showerror('Error',f'Student details failed to be Deleted due to {str(e)}',parent=self.root)
    ##################################Search function##########################
    def search_data(self):
        if self.var_search_combo.get() == "" or self.var_search_entry.get() == "":
            messagebox.showerror("Error", "Please select a search option and enter search data", parent=self.root)
        else:
            try:
                column_map = {
                "department":"Dep",
                "Roll_No":"Roll",
                "Phone_No":"Phone"
                }
                search_column = column_map.get(self.var_search_combo.get())
                conn = mysql.connector.connect(host="localhost", username="root", password="1582", database="face_recognizer")
                my_cursor = conn.cursor()
                query = f"SELECT * FROM student WHERE {search_column} LIKE %s"
                value = (f"%{self.var_search_entry.get()}%",)
                my_cursor.execute(query, value)
                rows = my_cursor.fetchall()

                if len(rows) != 0:
                    self.student_table.delete(*self.student_table.get_children())
                    for row in rows:
                        self.student_table.insert("", END, values=row)
                else:
                    messagebox.showinfo("No Result", "No matching records found", parent=self.root)

                conn.close()
            except Exception as es:
                messagebox.showerror("Error", f"Search could not performed due to: {str(es)}", parent=self.root)

    ###############reset function###############
    def reset_data(self):
        self.var_dep.set("Selcect Department")
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
        
   ###################### generate dataset or take a photo sample################################
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
                 conn=mysql.connector.connect(host='localhost',username='root',password='1582',database='face_recognizer')
                 my_cursor=conn.cursor()
                 my_cursor.execute('select * from student')
                 myresult=my_cursor.fetchall()
                 id=0
                 for x in myresult:
                     id+=1
                 my_cursor.execute('update student set Dep=%s,Course=%s,Year=%s,Semester=%s,Student_name=%s,Division=%s,Roll=%s,Gender=%s,Dob=%s,Email=%s,Phone=%s,Address=%s,Teacher=%s,PhotoSample=%s where Student_id=%s',(
                                self.var_dep.get(),
                                self.var_course.get(),
                                self.var_year.get(),
                                self.var_semester.get(),
                                self.var_std_name.get(),
                                self.var_div.get(),
                                self.var_roll.get(),
                                self.var_gender.get(),
                                self.var_dob.get(),
                                self.var_email.get(),
                                self.var_phone.get(),
                                self.var_address.get(),
                                self.var_teacher.get(),
                                self.var_radio1.get(),
                                self.va_std_id.get()))
                 conn.commit()
                 self.fetch_data()
                 self.reset_data()
                 conn.close()

        ######################## load predefined data on frontal face from opencv##########
        # Load the pre-trained Haar Cascade classifier for face detection
                 face_classifier=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        # Function to detect and crop face from an image
                 def face_cropped(img):
                     # Convert the image to grayscale (face detection works better on grayscale)
                     gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                     # Detect faces in the image
                     faces=face_classifier.detectMultiScale(gray,1.3,5)
                     #scaling factor =1.3,Minimum neighbour=5
                    #  1.3: Scale factor – how much the image size is reduced at each image scale. A value of 1.3 means the image is reduced by 30% at each step to detect faces of different sizes.5: minNeighbors – how many neighbors each rectangle should have to be retained as a valid face. A higher value gives fewer false positives.
                     # Loop through the detected faces and crop the face area
                     for (x,y,w,h) in faces:
                         face_cropped=img[y:y+h,x:x+w]#(0:face_height,0:face_width)
                         return face_cropped
                 cap=cv2.VideoCapture(1)
                 img_id=0
                 while True:
                         # cap.read returns numpy array and ret is used to ensure its working properly in case if another software uses webcam it returns false
                         ret,my_frame=cap.read()
                         if face_cropped(my_frame) is not None:
                             img_id+=1
                             # resize the cropped image
                             face=cv2.resize(face_cropped(my_frame),(450,450))
                             # convert the colour of capture image from an video
                             face=cv2.cvtColor(face,cv2.COLOR_BGR2GRAY)
                             file_name_path='data/user.'+str(id)+"."+str(img_id)+'.jpg'
                             #  save image in data folder
                             cv2.imwrite(file_name_path,face)
                             # put the count of an image in a frame
                             cv2.putText(face,str(img_id),(50,50),cv2.FONT_HERSHEY_COMPLEX,2,(0,255,0),2)
                             # show the frame
                             cv2.imshow('Cropped Face',face)
                         # Exit the loop when Enter key (key code 13) is pressed or 100 images are saved
                         if cv2.waitKey(1)==13 or int(img_id)==100:
                             break
                # when everything done release the cam and destroy all windows
                 cap.release()
                 cv2.destroyAllWindows()
                 messagebox.showinfo('Result','Generating data sets completed succesfully',parent=self.root)

            except Exception as e:
                messagebox.showerror('Error',f' Generating dataset is failed due to {str(e)}',parent=self.root)
##########################Update Photo Function#####################
    def update_photosample(self):
        if self.var_dep.get() == "" or self.va_std_id.get() == "":
            messagebox.showerror("Error", "All Fields are required", parent=self.root)
            return

        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="1582", database="face_recognizer")
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
                    face = cv2.resize(face_cropped(frame), (450, 450))
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
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
        self.time_lbl.after(1000, self.update_time)  # call again after 1 second


if __name__ == '__main__':
    root=Tk()
    obj=students(root)
    root.mainloop() 