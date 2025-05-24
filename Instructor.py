import tkinter as tk
from tkinter import messagebox, ttk, Listbox
import mysql.connector
import datetime

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sajan111', #  MySQL root password
    'database': 'attendance_system'
}

# --- Hardcoded Routine Data ---
ROUTINE_DATA = [
    ("C1", "Monday", "Mathematics", "9:00 AM - 11:00 AM", "kc", "Room 11"),
    ("C2", "Monday", "English", "10:15 AM - 12:15 PM", "Nimi", "Room 8"),
    ("C3", "Tuesday", "Science", "8:00 AM - 11:00 AM", "Upendra", "Room 1"),
    ("C4", "Tuesday", "History", "10:15 AM - 12:15 PM", "Rana", "Room 22"),
    ("C5", "Wednesday", "Art", "8:00 AM - 10:00 AM", "Guras", "Room 13"),
    ("C6", "Wednesday", "Economics", "9:15 AM - 11:15 AM", "Fulmaya", "Room 7"),
    ("C7", "Thursday", "Mathematics", "8:00 AM - 10:00 AM", "kc", "Room 10"),
    ("C8", "Thursday", "Chemistry", "9:15 AM - 11:15 AM", "Biste", "Lab 5"),
    ("C9", "Friday", "Biology", "8:00 AM - 10:00 AM", "Ram", "Room 4"),
    ("C10", "Friday", "Physics", "1:00 PM - 3:00 PM", "Upendra", "Lab 3")
]

# --- Database Connection Helper ---
def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
        return None

# --- Database Initialization Helper ---
def initialize_database():
    try:
        conn_setup = mysql.connector.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'], password=DB_CONFIG['password'])
        cursor_setup = conn_setup.cursor()
        cursor_setup.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor_setup.close()
        conn_setup.close()
        conn_init = connect_db()
        if not conn_init: return False
        cursor_init = conn_init.cursor(dictionary=True)
        # Ensure all tables exist
        cursor_init.execute("CREATE TABLE IF NOT EXISTS instructors (instructor_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL UNIQUE, password VARCHAR(255) NOT NULL, class_id VARCHAR(255))")
        cursor_init.execute("CREATE TABLE IF NOT EXISTS students (student_id VARCHAR(50) PRIMARY KEY, name VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, course VARCHAR(255), class_id VARCHAR(50))")
        cursor_init.execute("CREATE TABLE IF NOT EXISTS subjects (subject_id INT AUTO_INCREMENT PRIMARY KEY, subject_name VARCHAR(255) NOT NULL UNIQUE)")
        cursor_init.execute("CREATE TABLE IF NOT EXISTS student_subjects (student_id VARCHAR(50), subject_id INT, PRIMARY KEY (student_id, subject_id), FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE ON UPDATE CASCADE)")
        cursor_init.execute("CREATE TABLE IF NOT EXISTS attendance (attendance_id INT AUTO_INCREMENT PRIMARY KEY, student_id VARCHAR(50), class_id VARCHAR(50), date DATE, present BOOLEAN, FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE ON UPDATE CASCADE, UNIQUE KEY unique_attendance (student_id, class_id, date))")

        # Populate if empty
        cursor_init.execute("SELECT COUNT(*) AS count FROM instructors")
        if cursor_init.fetchone()['count'] == 0:
            instructors_to_add = [('kc', 'sajan', 'C1'), ('Nimi', 'sajan', 'C2'), ('Upendra', 'sajan', 'C3'), ('Rana', 'sajan', 'C4'), ('Guras', 'sajan', 'C5'), ('Fulmaya', 'sajan', 'C6'), ('Biste', 'sajan', 'C8'), ('Ram', 'sajan', 'C9')]
            cursor_init.executemany("INSERT IGNORE INTO instructors (name, password, class_id) VALUES (%s, %s, %s)", instructors_to_add)
        cursor_init.execute("SELECT COUNT(*) AS count FROM subjects")
        if cursor_init.fetchone()['count'] == 0:
            # Ensure all subjects from ROUTINE_DATA are included
            db_subjects_set = set(entry[2] for entry in ROUTINE_DATA)
            # Add other desired subjects
            db_subjects_set.update(['English Literature', 'Geography', 'Computer Programming', 'Data Structures', 'Business Studies', 'Fine Arts'])
            subjects_to_add_tuples = [(subj,) for subj in sorted(list(db_subjects_set))]
            cursor_init.executemany("INSERT IGNORE INTO subjects (subject_name) VALUES (%s)", subjects_to_add_tuples)
        conn_init.commit()
        cursor_init.close()
        conn_init.close()
        return True
    except Exception as e:
        messagebox.showerror("DB Init Error", f"Database initialization failed: {e}")
        return False

# --- InstructorLogin Class ---
class InstructorLogin:
    def __init__(self, master, success_callback):
        self.master = master; self.master.title("Instructor Login"); self.master.geometry("350x200")
        self.success_callback = success_callback
        frame = ttk.Frame(master, padding="20"); frame.pack(expand=True, fill="both")
        ttk.Label(frame, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(frame, width=30); self.username_entry.pack()
        ttk.Label(frame, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(frame, show="*", width=30); self.password_entry.pack()
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())
        ttk.Button(frame, text="Login", command=self.attempt_login).pack(pady=15)
        self.username_entry.focus_set()

    def attempt_login(self):
        username = self.username_entry.get().strip(); password = self.password_entry.get()
        if not username or not password: messagebox.showerror("Login Error", "Input Username/Password."); return
        conn = None
        try:
            conn = connect_db();
            if not conn: return
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM instructors WHERE name = %s", (username,))
            instructor = cursor.fetchone()
            if instructor and instructor['password'] == password:
                self.master.destroy(); self.success_callback(instructor)
            else: messagebox.showerror("Login Failed", "Invalid credentials.")
        except mysql.connector.Error as err: messagebox.showerror("DB Error", f"Login error: {err}")
        finally:
            if conn: cursor.close(); conn.close()

# --- InstructorInterface Class ---
class InstructorInterface:
    def __init__(self, root, instructor_data, logout_callback):
        self.root = root; self.root.title(f"Instructor Portal - {instructor_data['name']}"); self.root.geometry("1050x700")
        self.instructor_data = instructor_data; self.instructor_name = instructor_data['name']
        self.logout_callback = logout_callback
        self.conn = connect_db()
        if not self.conn: self.root.destroy(); return
        self.cursor = self.conn.cursor(dictionary=True)

        self.all_subjects_map_name_to_id = {}
        self.load_all_subjects_from_db()

        self.instructor_schedule_details = [entry for entry in ROUTINE_DATA if entry[4] == self.instructor_name]
        self.taught_class_ids_list = sorted(list(set([item[0] for item in self.instructor_schedule_details])))
        self.taught_subject_names = sorted(list(set([entry[2] for entry in self.instructor_schedule_details])))

        self.create_widgets()
        self.load_classes_for_comboboxes()

    def load_all_subjects_from_db(self):
        try:
            self.cursor.execute("SELECT subject_id, subject_name FROM subjects")
            self.all_subjects_map_name_to_id = {s['subject_name']: s['subject_id'] for s in self.cursor.fetchall()}
        except mysql.connector.Error as err: messagebox.showerror("DB Error", f"Failed to load subjects: {err}")

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10); main_frame.pack(expand=1, fill="both")
        self.tab_control = ttk.Notebook(main_frame); self.tab_control.pack(expand=1, fill="both", pady=(0, 10))
        self.create_my_classes_overview_tab()
        self.create_registration_tab()
        self.create_record_attendance_tab()
        self.create_view_attendance_tab()
        ttk.Button(main_frame, text="Logout", command=self.logout).pack(side="bottom", anchor="se", pady=5, padx=5)

    def create_my_classes_overview_tab(self):
        tab = ttk.Frame(self.tab_control, padding=15); self.tab_control.add(tab, text="My Classes Overview")
        ttk.Label(tab, text=f"Schedule & Student Counts for {self.instructor_name}", font=("Arial", 14, "bold")).pack(pady=10)
        tree_frame = ttk.Frame(tab); tree_frame.pack(fill="both", expand=True, pady=10)
        cols = ("Class ID", "Subject", "Day", "Time", "Location", "Student Count")
        self.overview_tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols: self.overview_tree.heading(col, text=col); self.overview_tree.column(col, width=150)
        self.overview_tree.column("Student Count", width=100, anchor="center")
        self.overview_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.overview_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.overview_tree.configure(yscrollcommand=scrollbar.set)
        self.populate_my_classes_overview()

    def populate_my_classes_overview(self):
        for i in self.overview_tree.get_children(): self.overview_tree.delete(i)
        if not self.instructor_schedule_details: self.overview_tree.insert("", "end", values=("N/A", "No classes assigned.", "", "", "", "")); return
        for entry in self.instructor_schedule_details:
            class_id, day, subject, time, _, location = entry
            try:
                subject_id = self.all_subjects_map_name_to_id.get(subject)
                if subject_id:
                    self.cursor.execute("SELECT COUNT(*) AS count FROM student_subjects WHERE subject_id = %s", (subject_id,))
                    count = self.cursor.fetchone()['count']
                else: count = 0
            except mysql.connector.Error as err: count = "Error"
            self.overview_tree.insert("", "end", values=(class_id, subject, day, time, location, count))

    def create_registration_tab(self):
        tab = ttk.Frame(self.tab_control, padding=15); self.tab_control.add(tab, text="Student Registration")
        form_frame = ttk.Frame(tab); form_frame.pack(pady=10, padx=10, fill="x")
        self.reg_entries = {}
        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.reg_entries["student_id"] = ttk.Entry(form_frame, width=40); self.reg_entries["student_id"].grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(form_frame, text="Student Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.reg_entries["student_name"] = ttk.Entry(form_frame, width=40); self.reg_entries["student_name"].grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(form_frame, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.reg_entries["password"] = ttk.Entry(form_frame, width=40, show="*"); self.reg_entries["password"].grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(form_frame, text="Assign Primary Class:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.reg_class_combobox = ttk.Combobox(form_frame, state="readonly", width=38, values=self.taught_class_ids_list)
        if self.taught_class_ids_list: self.reg_class_combobox.set(self.taught_class_ids_list[0])
        else: self.reg_class_combobox.set("No classes found")
        self.reg_class_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(form_frame, text="Assign Subjects You Teach:").grid(row=4, column=0, padx=5, pady=10, sticky="nw")
        self.subjects_listbox = Listbox(form_frame, selectmode=tk.MULTIPLE, height=len(self.taught_subject_names) + 1 if self.taught_subject_names else 3, exportselection=False, width=38)
        self.subjects_listbox.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        for subject_name in self.taught_subject_names:
            self.subjects_listbox.insert(tk.END, subject_name)
        form_frame.grid_columnconfigure(1, weight=1)
        ttk.Button(tab, text="Register Student", command=self.register_student).pack(pady=20)

    def register_student(self):
        student_id = self.reg_entries["student_id"].get().strip()
        name = self.reg_entries["student_name"].get().strip()
        password = self.reg_entries["password"].get()
        assigned_class_id = self.reg_class_combobox.get()
        if not all([student_id, name, password, assigned_class_id]) or assigned_class_id == "No classes found":
            messagebox.showerror("Error", "Student ID, Name, Password, and a valid Primary Class are required."); return
        selected_subject_names = [self.subjects_listbox.get(i) for i in self.subjects_listbox.curselection()]
        if not selected_subject_names: messagebox.showerror("Error", "Please assign at least one subject."); return
        student_course = "General Studies"
        for cid, _, subj, _, _, _ in ROUTINE_DATA:
            if cid == assigned_class_id: student_course = subj; break
        subject_ids_to_assign = [self.all_subjects_map_name_to_id[sub_name] for sub_name in selected_subject_names if sub_name in self.all_subjects_map_name_to_id]
        try:
            self.cursor.execute("INSERT INTO students (student_id, name, password, course, class_id) VALUES (%s, %s, %s, %s, %s)", (student_id, name, password, student_course, assigned_class_id))
            subject_assign_data = [(student_id, sub_id) for sub_id in subject_ids_to_assign]
            self.cursor.executemany("INSERT IGNORE INTO student_subjects (student_id, subject_id) VALUES (%s, %s)", subject_assign_data)
            self.conn.commit()
            messagebox.showinfo("Success", f"Student '{name}' registered!")
            try:
                with open('students.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{student_id},{name}\n")
            except Exception as e:
                print(f"WARNING: Could not write to students.txt: {e}")
            for entry in self.reg_entries.values(): entry.delete(0, tk.END)
            if self.taught_class_ids_list: self.reg_class_combobox.set(self.taught_class_ids_list[0])
            self.subjects_listbox.selection_clear(0, tk.END); self.populate_my_classes_overview()
        except mysql.connector.Error as err: self.conn.rollback(); messagebox.showerror("DB Error", f"Register student failed: {err}")

    def create_record_attendance_tab(self):
        tab = ttk.Frame(self.tab_control, padding=15); self.tab_control.add(tab, text="Record Attendance")
        top_frame = ttk.Frame(tab); top_frame.pack(fill="x", pady=5)
        ttk.Label(top_frame, text="Select Your Class:").pack(side="left", padx=5)
        self.class_combobox_record = ttk.Combobox(top_frame, state="readonly", width=20); self.class_combobox_record.pack(side="left", padx=5, fill="x", expand=True)
        self.class_combobox_record.bind("<<ComboboxSelected>>", self.on_class_selected_for_attendance)
        self.subject_display_label = ttk.Label(top_frame, text="Subject: N/A", width=25, anchor="w"); self.subject_display_label.pack(side="left", padx=5)
        ttk.Label(top_frame, text="Date:").pack(side="left", padx=5)
        self.date_entry_record = ttk.Entry(top_frame, font=("Arial", 10), justify="center", width=12); self.date_entry_record.insert(0, datetime.date.today().strftime('%Y-%m-%d')); self.date_entry_record.pack(side="left", padx=5)
        tree_frame = ttk.Frame(tab); tree_frame.pack(fill="both", expand=True, pady=10)
        self.attendance_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Course", "Status"), show="headings");
        self.attendance_tree.heading("ID", text="Student ID"); self.attendance_tree.heading("Name", text="Name"); self.attendance_tree.heading("Course", text="Class Subject"); self.attendance_tree.heading("Status", text="Status")
        self.attendance_tree.pack(side="left", fill="both", expand=True); self.attendance_tree.bind("<Double-1>", self.toggle_attendance_status)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.attendance_tree.yview); scrollbar.pack(side="right", fill="y"); self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        ttk.Button(tab, text="Save Attendance", command=self.save_attendance).pack(pady=10)

    def load_classes_for_comboboxes(self):
        self.class_combobox_record['values'] = self.taught_class_ids_list
        if hasattr(self, 'class_combobox_view'): self.class_combobox_view['values'] = self.taught_class_ids_list
        if self.taught_class_ids_list:
            default_class = self.taught_class_ids_list[0]
            self.class_combobox_record.set(default_class)
            if hasattr(self, 'class_combobox_view'): self.class_combobox_view.set(default_class)
            self.update_subject_display_label(default_class); self.load_students_for_attendance()
        else:
            self.class_combobox_record.set("");
            if hasattr(self, 'class_combobox_view'): self.class_combobox_view.set("")
            self.subject_display_label.config(text="Subject: N/A"); self.load_students_for_attendance()

    def get_subject_for_class(self, class_id):
        for cid, _, subj, _, tchr, _ in self.instructor_schedule_details:
            if cid == class_id and tchr == self.instructor_name:
                return subj
        return None

    def update_subject_display_label(self, selected_class_id):
        subject_name = "N/A"; day_time_info = ""
        for cid_routine, day_routine, subj_routine, time_routine, tchr_routine, _ in self.instructor_schedule_details:
            if cid_routine == selected_class_id and tchr_routine == self.instructor_name:
                subject_name = subj_routine; day_time_info = f"({day_routine.capitalize()}, {time_routine})"; break
        self.subject_display_label.config(text=f"Subject: {subject_name} {day_time_info}")

    def on_class_selected_for_attendance(self, event):
        selected_class_id = self.class_combobox_record.get()
        if selected_class_id: self.update_subject_display_label(selected_class_id); self.load_students_for_attendance()

    def load_students_for_attendance(self):
        selected_class_id = self.class_combobox_record.get()
        for i in self.attendance_tree.get_children(): self.attendance_tree.delete(i)
        if not selected_class_id: self.update_subject_display_label(""); return

        subject_name_for_display = self.get_subject_for_class(selected_class_id)

        if not subject_name_for_display:
            print(f"Debug: No subject found for {selected_class_id} taught by {self.instructor_name}")
            self.update_subject_display_label(selected_class_id)
            return

        subject_id = self.all_subjects_map_name_to_id.get(subject_name_for_display)
        if not subject_id:
            messagebox.showerror("Error", f"Subject '{subject_name_for_display}' (for class {selected_class_id}) not found in internal subject map. Check 'subjects' table in DB.")
            return
        try:
            query = "SELECT s.student_id, s.name FROM students s JOIN student_subjects ss ON s.student_id = ss.student_id WHERE ss.subject_id = %s ORDER BY s.name" # Removed s.course
            self.cursor.execute(query, (subject_id,)); students = self.cursor.fetchall()
            if not students:
                 current_subj_text = self.subject_display_label.cget("text")
                 if " - No Students" not in current_subj_text: self.subject_display_label.config(text=current_subj_text + " - No Students")
                 return
            self.update_subject_display_label(selected_class_id)
            for s in students:
                self.attendance_tree.insert("", "end", values=(s['student_id'], s['name'], subject_name_for_display, "Absent"))
        except mysql.connector.Error as err: messagebox.showerror("DB Error", f"Load students failed: {err}")

    def toggle_attendance_status(self, event):
        item_id = self.attendance_tree.focus();
        if not item_id: return
        vals = self.attendance_tree.item(item_id, "values")
        new_status = "Present" if vals[3] == "Absent" else "Absent"
        self.attendance_tree.item(item_id, values=(vals[0], vals[1], vals[2], new_status))

    def save_attendance(self):
        class_id = self.class_combobox_record.get(); date_str = self.date_entry_record.get()
        if not class_id or not date_str: messagebox.showerror("Error", "Class and Date required."); return
        try:
            attendance_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("Error", "Invalid Date. Use YYYY-MM-DD."); return

        records = [(self.attendance_tree.item(i)["values"][0], class_id, attendance_date, 1 if self.attendance_tree.item(i)["values"][3] == "Present" else 0) for i in self.attendance_tree.get_children()]
        if not records: messagebox.showwarning("Warning", "No student records."); return
        try:
            self.cursor.executemany("INSERT INTO attendance (student_id, class_id, date, present) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE present = VALUES(present)", records)
            self.conn.commit(); messagebox.showinfo("Success", f"Attendance saved for Class {class_id}!")
            try:
                now_time = datetime.datetime.now().strftime('%H:%M')
                with open('attendance.txt', 'a', encoding='utf-8') as f:
                    for record in records:
                        student_id_att = record[0]
                        date_att_str = record[2].strftime('%Y-%m-%d')
                        status_att = "Present" if record[3] == 1 else "Absent"
                        f.write(f"{date_att_str},{student_id_att},{status_att},{now_time}\n")
            except Exception as e:
                print(f"WARNING: Could not write to attendance.txt: {e}")
        except mysql.connector.Error as err:
            self.conn.rollback(); messagebox.showerror("DB Error", f"Save attendance failed: {err}")

    def create_view_attendance_tab(self):
        tab = ttk.Frame(self.tab_control, padding=15); self.tab_control.add(tab, text="View Saved Attendance")
        filter_frame = ttk.Frame(tab); filter_frame.pack(fill="x", pady=5)
        ttk.Label(filter_frame, text="Select Your Class:").pack(side="left", padx=5)
        self.class_combobox_view = ttk.Combobox(filter_frame, state="readonly", width=15); self.class_combobox_view.pack(side="left", padx=5)
        ttk.Label(filter_frame, text="Date (YYYY-MM-DD):").pack(side="left", padx=5)
        self.date_entry_view = ttk.Entry(filter_frame, width=12); self.date_entry_view.insert(0, datetime.date.today().strftime('%Y-%m-%d')); self.date_entry_view.pack(side="left", padx=5)
        ttk.Label(filter_frame, text="Student ID (Opt):").pack(side="left", padx=5)
        self.student_id_entry_view = ttk.Entry(filter_frame, width=15); self.student_id_entry_view.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="View Attendance", command=self.view_saved_attendance).pack(side="left", padx=10)
        view_tree_frame = ttk.Frame(tab); view_tree_frame.pack(fill="both", expand=True, pady=10)
        cols_view = ("ID", "Name", "Class", "Course", "Status", "Date") # "Course" here will be the class's subject
        self.attendance_view_tree = ttk.Treeview(view_tree_frame, columns=cols_view, show="headings");
        for col in cols_view: self.attendance_view_tree.heading(col, text=col)
        self.attendance_view_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(view_tree_frame, orient="vertical", command=self.attendance_view_tree.yview); scrollbar.pack(side="right", fill="y"); self.attendance_view_tree.configure(yscrollcommand=scrollbar.set)
        self.load_classes_for_comboboxes()

    def view_saved_attendance(self):
        class_id_filter = self.class_combobox_view.get(); date_str_filter = self.date_entry_view.get().strip(); student_id_filter = self.student_id_entry_view.get().strip()
        if not date_str_filter: messagebox.showerror("Error", "Date required."); return
        try: attendance_date_f = datetime.datetime.strptime(date_str_filter, '%Y-%m-%d').date()
        except ValueError: messagebox.showerror("Error", "Invalid Date. Use YYYY-MM-DD."); return

        # Query to get student name and attendance details. We'll determine course (subject) from ROUTINE_DATA.
        query = "SELECT s.student_id, s.name, a.class_id, a.present, a.date FROM students s JOIN attendance a ON s.student_id = a.student_id WHERE a.date = %s"
        params = [attendance_date_f]

        if class_id_filter:
             if class_id_filter not in self.taught_class_ids_list: messagebox.showerror("Error", "You can only view your own classes."); return
             query += " AND a.class_id = %s"; params.append(class_id_filter)
        elif self.taught_class_ids_list: # If no specific class selected, show all classes for this teacher
             query += " AND a.class_id IN ({})".format(",".join(["%s"] * len(self.taught_class_ids_list))); params.extend(self.taught_class_ids_list)
        else: # No classes taught by this instructor
             messagebox.showinfo("No Data", "No classes assigned to view attendance."); return

        if student_id_filter: query += " AND s.student_id = %s"; params.append(student_id_filter)
        query += " ORDER BY a.class_id, s.name"

        try:
            self.cursor.execute(query, tuple(params)); results = self.cursor.fetchall()
            for i in self.attendance_view_tree.get_children(): self.attendance_view_tree.delete(i)
            if not results: messagebox.showinfo("No Data", "No records for criteria."); return

            # Helper to get subject from ROUTINE_DATA based on class_id
            class_id_to_subject_map = {entry[0]: entry[2] for entry in ROUTINE_DATA}

            for r in results:
                # Get subject from class_id ---
                class_subject = class_id_to_subject_map.get(r['class_id'], 'N/A')
                
                self.attendance_view_tree.insert("", "end", values=(
                    r['student_id'],
                    r['name'],
                    r['class_id'],
                    class_subject, # Use the determined subject of the class
                    "Present" if r['present'] else "Absent",
                    r['date'].strftime('%Y-%m-%d')
                ))
        except mysql.connector.Error as err: messagebox.showerror("DB Error", f"Retrieve attendance failed: {err}")

    def logout(self):
        if messagebox.askokcancel("Logout", "Are you sure?"):
            if self.conn and self.conn.is_connected(): self.cursor.close(); self.conn.close()
            self.root.destroy(); self.logout_callback()

# --- Main Application Runner ---
def start_login_interface():
    login_root = tk.Tk()
    InstructorLogin(login_root, start_instructor_interface)
    login_root.mainloop()

def start_instructor_interface(instructor_data):
    if instructor_data:
        app_root = tk.Tk()
        InstructorInterface(app_root, instructor_data, start_login_interface)
        app_root.mainloop()

if __name__ == "__main__":
    if initialize_database():
        start_login_interface()
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", "Failed to initialize DB.")
        root.destroy()