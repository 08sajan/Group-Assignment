import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime, date

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sajan111', # Ensure this matches your MySQL root password
    'database': 'attendance_system'
}

# --- Full Routine Data (Must match Instructor.py) ---
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

# --- NEW: Hardcoded Subjects List ---
HARDCODED_SUBJECTS = [
    "Mathematics", "English", "Science", "History", "Art",
    "Economics", "Chemistry", "Biology", "Physics"
]
# Ensure it only has unique values for consistency
HARDCODED_SUBJECTS = sorted(list(set(HARDCODED_SUBJECTS)))


# --- Database Connection Helper ---
def connect_db_student():
    """Establishes a connection to the MySQL database."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Student GUI: DB connection error: {err}")
        return None

# ====================================================================
# == StudentPortalInterface Class (Student Portal GUI) ==
# ====================================================================
class StudentPortalInterface:
    """Defines the Tkinter GUI for the student to view their routine and attendance."""

    def __init__(self, root, student_data, logout_callback):
        self.root = root
        self.student_info = student_data
        self.student_id = self.student_info['student_id']
        self.logout_callback = logout_callback
        self.root.title(f"Student Portal - {self.student_info['name']} ({self.student_id})")
        self.root.geometry("950x550")

        self.conn = connect_db_student() # Still needed for Login and Attendance
        if not self.conn:
            messagebox.showerror("Database Error", "Cannot connect. Closing.")
            self.root.destroy()
            return
        self.cursor = self.conn.cursor(dictionary=True)

        self.enrolled_subject_names = HARDCODED_SUBJECTS # Use hardcoded list
        self.create_widgets()
        self.load_student_subjects() # Now uses hardcoded list
        self.populate_subject_filter_combobox() # Use hardcoded list
        self.load_routine_display()  # Now shows all classes
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Creates the main tab control."""
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        self.create_my_info_tab()
        self.create_routine_tab()
        self.create_view_attendance_tab()

        logout_button = ttk.Button(self.root, text="Logout", command=self.logout)
        logout_button.pack(side="bottom", anchor="se", pady=5, padx=10)

    def create_my_info_tab(self):
        """Creates a tab to display student's information (MODIFIED)."""
        self.my_info_tab = ttk.Frame(self.tab_control, padding=10)
        self.tab_control.add(self.my_info_tab, text="My Information")

        info_frame = ttk.LabelFrame(self.my_info_tab, text="Personal Details", padding=10)
        info_frame.pack(fill="x", pady=5)
        ttk.Label(info_frame, text=f"Student ID: {self.student_info['student_id']}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Name: {self.student_info['name']}").pack(anchor="w")
        # --- MODIFIED ---
        ttk.Label(info_frame, text="Grade: 10").pack(anchor="w")
        # Primary Course and Class ID removed
        # --- END MODIFIED ---

        subjects_frame = ttk.LabelFrame(self.my_info_tab, text="My Enrolled Subjects (All)", padding=10)
        subjects_frame.pack(fill="both", expand=True, pady=10)
        self.subjects_list_text = tk.Text(subjects_frame, height=10, width=50, state="disabled", relief="sunken", borderwidth=1)
        self.subjects_list_text.pack(pady=5, fill="both", expand=True)

    def create_routine_tab(self):
        """Creates the tab for viewing the full class routine."""
        self.routine_tab = ttk.Frame(self.tab_control, padding=10)
        # --- MODIFIED ---
        self.tab_control.add(self.routine_tab, text="My Class Routine (All)")
        ttk.Label(self.routine_tab, text="Full Weekly Schedule", font=("Arial", 14, "bold")).pack(pady=10)
        # --- END MODIFIED ---
        self._setup_routine_treeview(self.routine_tab)

    def _setup_routine_treeview(self, parent_frame):
        """Sets up the Treeview widget for the routine."""
        columns = ("class_id", "day", "subject", "time", "teacher", "location")
        self.routine_tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        self.routine_tree.pack(fill="both", expand=True)
        headings = {"class_id": "Class ID", "day": "Day", "subject": "Subject", "time": "Time", "teacher": "Teacher", "location": "Location"}
        widths = {"class_id": 80, "day": 100, "subject": 150, "time": 150, "teacher": 120, "location": 100}
        for col_id in columns:
            self.routine_tree.heading(col_id, text=headings[col_id])
            self.routine_tree.column(col_id, width=widths[col_id], anchor="center")

    def load_student_subjects(self):
        """--- MODIFIED: Displays hardcoded subjects, NO DB QUERY ---"""
        self.subjects_list_text.config(state="normal")
        self.subjects_list_text.delete(1.0, tk.END)
        self.subjects_list_text.insert(tk.END, "You are enrolled in:\n")
        for subj in self.enrolled_subject_names: # Uses hardcoded list
            self.subjects_list_text.insert(tk.END, f"- {subj}\n")
        self.subjects_list_text.config(state="disabled")
        # --- END MODIFIED ---

    def load_routine_display(self):
        """--- MODIFIED: Displays ALL classes from ROUTINE_DATA ---"""
        for item in self.routine_tree.get_children():
            self.routine_tree.delete(item)

        # Use all classes
        actual_routine = list(ROUTINE_DATA)

        # Sort by day for better readability
        day_order = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}
        actual_routine.sort(key=lambda x: day_order.get(x[1], 99))

        # Populate the treeview
        for entry in actual_routine:
            self.routine_tree.insert("", "end", values=entry)
        # --- END MODIFIED ---

    def create_view_attendance_tab(self):
        """Creates the tab for viewing attendance (uses hardcoded subjects for filter)."""
        self.view_attendance_tab = ttk.Frame(self.tab_control, padding=10)
        self.tab_control.add(self.view_attendance_tab, text="My Attendance")

        filter_frame = ttk.Frame(self.view_attendance_tab)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Start Date:").pack(side="left", padx=(0, 2))
        self.start_date_entry = ttk.Entry(filter_frame, width=12); self.start_date_entry.pack(side="left", padx=(0, 10))
        ttk.Label(filter_frame, text="End Date:").pack(side="left", padx=(0, 2))
        self.end_date_entry = ttk.Entry(filter_frame, width=12); self.end_date_entry.insert(0, date.today().strftime('%Y-%m-%d')); self.end_date_entry.pack(side="left", padx=(0, 10))
        ttk.Label(filter_frame, text="Subject:").pack(side="left", padx=(0, 2))
        self.subject_filter_combobox = ttk.Combobox(filter_frame, state="readonly", width=15); self.subject_filter_combobox.pack(side="left", padx=(0, 10))
        ttk.Button(filter_frame, text="Filter Attendance", command=self.load_student_attendance).pack(side="left", padx=10)

        tk.Label(self.view_attendance_tab, text="My Attendance Records", font=("Arial", 14, "bold")).pack(pady=(15, 10))
        self.attendance_tree = ttk.Treeview(self.view_attendance_tab, columns=("Class ID", "Subject", "Date", "Status"), show="headings")
        self.attendance_tree.heading("Class ID", text="Class ID"); self.attendance_tree.heading("Subject", text="Subject"); self.attendance_tree.heading("Date", text="Date"); self.attendance_tree.heading("Status", text="Status")
        self.attendance_tree.column("Class ID", width=80, anchor="center"); self.attendance_tree.column("Subject", width=150); self.attendance_tree.column("Date", width=100, anchor="center"); self.attendance_tree.column("Status", width=80, anchor="center")
        self.attendance_tree.pack(fill="both", expand=True, pady=5)
        self.load_student_attendance() # Load initially

    def populate_subject_filter_combobox(self):
        """Populates the subject filter dropdown with hardcoded subjects."""
        filter_options = ["All Subjects"] + self.enrolled_subject_names # Uses hardcoded list
        self.subject_filter_combobox['values'] = filter_options
        self.subject_filter_combobox.set("All Subjects")

    def load_student_attendance(self):
        """Loads student attendance based on selected filters."""
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        start_date_str = self.start_date_entry.get().strip()
        end_date_str = self.end_date_entry.get().strip()
        selected_subject = self.subject_filter_combobox.get()
        today_date = date.today()
        params = [self.student_id]
        query = "SELECT a.class_id, a.date, a.present FROM attendance a WHERE a.student_id = %s"

        subject_class_ids = []
        if selected_subject and selected_subject != "All Subjects":
            subject_class_ids = [entry[0] for entry in ROUTINE_DATA if entry[2] == selected_subject]
            if not subject_class_ids:
                self.attendance_tree.insert("", "end", values=("", "No classes for this subject.", "", ""))
                return
            query += " AND a.class_id IN ({})".format(",".join(["%s"] * len(subject_class_ids)))
            params.extend(subject_class_ids)

        try:
            if start_date_str: params.append(datetime.strptime(start_date_str, '%Y-%m-%d').date()); query += " AND a.date >= %s"
            if end_date_str: params.append(datetime.strptime(end_date_str, '%Y-%m-%d').date()); query += " AND a.date <= %s"
            else: params.append(today_date); query += " AND a.date <= %s"
            query += " ORDER BY a.date DESC, a.class_id ASC"

            class_to_subject = {entry[0]: entry[2] for entry in ROUTINE_DATA}
            self.cursor.execute(query, tuple(params))
            results = self.cursor.fetchall()

            if not results:
                self.attendance_tree.insert("", "end", values=("", "No records found.", "", ""))
                return

            for row in results:
                status_text = "Present" if row['present'] == 1 else "Absent"
                display_date = row['date'].strftime('%Y-%m-%d') if row['date'] else 'N/A'
                subject = class_to_subject.get(row['class_id'], 'N/A')
                self.attendance_tree.insert("", "end", values=(row['class_id'], subject, display_date, status_text))
        except ValueError:
             messagebox.showerror("Input Error", "Invalid Date format. Use YYYY-MM-DD.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve attendance: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def logout(self):
        if messagebox.askokcancel("Logout", "Are you sure you want to logout?"):
            self.on_closing(is_logout=True)
            self.logout_callback()

    def on_closing(self, is_logout=False):
        if not is_logout and not messagebox.askokcancel("Quit", "Do you want to quit?"):
            return
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("Student GUI: Database connection closed.")
        self.root.destroy()

# ====================================================================
# == StudentLogin Class (Login GUI) - Modified to not rely on class_id/course ==
# ====================================================================
class StudentLogin:
    def __init__(self, master, success_callback):
        self.master = master
        self.master.title("Student Login")
        self.master.geometry("350x200")
        self.master.resizable(False, False)
        self.success_callback = success_callback

        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        frame = ttk.Frame(master, padding="20 20 20 20")
        frame.pack(expand=True, fill="both")
        ttk.Label(frame, text="Student ID:").pack(pady=5)
        self.id_entry = ttk.Entry(frame, width=30)
        self.id_entry.pack()
        ttk.Label(frame, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(frame, show="*", width=30)
        self.password_entry.pack()
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())
        self.login_button = ttk.Button(frame, text="Login", command=self.attempt_login)
        self.login_button.pack(pady=15)
        self.id_entry.focus_set()

    def attempt_login(self):
        student_id = self.id_entry.get().strip()
        password = self.password_entry.get()

        if not student_id or not password:
            messagebox.showerror("Login Error", "Please enter both Student ID and password.")
            return

        conn_login = None
        try:
            conn_login = connect_db_student()
            if not conn_login: return
            cursor_login = conn_login.cursor(dictionary=True)
            # Query only needed fields for login check
            query = "SELECT student_id, name, password FROM students WHERE student_id = %s"
            cursor_login.execute(query, (student_id,))
            student = cursor_login.fetchone()

            if student and student['password'] == password:
                messagebox.showinfo("Login Success", f"Welcome, {student['name']}!")
                self.master.destroy()
                # Pass a simplified dictionary, as course/class_id are not used anymore
                self.success_callback({'student_id': student['student_id'], 'name': student['name']})
            else:
                messagebox.showerror("Login Failed", "Invalid Student ID or Password.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Login failed: {err}")
        finally:
            if conn_login and conn_login.is_connected():
                cursor_login.close()
                conn_login.close()

# --- Main Application Runner ---
def start_student_login():
    login_root_student = tk.Tk()
    StudentLogin(login_root_student, start_student_portal)
    login_root_student.mainloop()

def start_student_portal(student_data):
    if student_data:
        portal_root = tk.Tk()
        StudentPortalInterface(portal_root, student_data, start_student_login)
        portal_root.mainloop()
    else:
        start_student_login()

if __name__ == "__main__":
    print("Starting Student Application...")
    start_student_login()