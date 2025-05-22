import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
import datetime


class InstructorInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Instructor Attendance Interface")
        self.root.geometry("1200x1000")

        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'sajan111',
            'database': 'attendance_system'
        }
        self.conn = self.connect_db()
        self.cursor = self.conn.cursor()

        self.create_widgets()

    def connect_db(self):
        """Establishes a connection to the MySQL database."""
        try:
            return mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Failed to connect to database: {err}")
            self.root.destroy()  # Close the application if DB connection fails
            return None

    def create_widgets(self):
        """Creates and arranges all GUI widgets."""
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both")

        self.create_registration_tab()
        self.create_record_attendance_tab()
        self.create_view_attendance_tab()

    def create_registration_tab(self):
        """Configures the student registration tab."""
        self.registration_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.registration_tab, text="Student Registration")

        labels = ["Student ID:", "Class Id:", "Student Name:", "Course:"]
        self.reg_entries = {}
        for i, text in enumerate(labels):
            tk.Label(self.registration_tab, text=text).grid(row=i, column=0, padx=10, pady=10)
            entry = tk.Entry(self.registration_tab)
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.reg_entries[text.replace(":", "").replace(" ", "_").lower()] = entry

        tk.Button(self.registration_tab, text="Register Student", command=self.register_student).grid(
            row=len(labels), column=0, columnspan=2, pady=10)

    def create_record_attendance_tab(self):
        """Configures the record attendance tab."""
        self.record_attendance_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.record_attendance_tab, text="Record Attendance")

        tk.Label(self.record_attendance_tab, text="Class ID:").grid(row=0, column=0, padx=2, pady=5)
        self.class_id_entry_record = tk.Entry(self.record_attendance_tab)
        self.class_id_entry_record.grid(row=0, column=1, padx=2, pady=5)

        tk.Label(self.record_attendance_tab, text="Date:").grid(row=2, column=0, padx=10, pady=10)
        self.date_entry_record = tk.Entry(self.record_attendance_tab, font=("Arial", 12), justify="center")
        self.date_entry_record.insert(0, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.date_entry_record.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.record_attendance_tab, text="Load Class for Attendance", command=self.load_students_for_attendance).grid(
            row=3, column=0, columnspan=2, pady=10)

        self.attendance_tree = ttk.Treeview(self.record_attendance_tab, columns=("ID", "Name", "Status", "Course"),
                                            show="headings")
        self.attendance_tree.heading("ID", text="Student ID")
        self.attendance_tree.heading("Name", text="Student Name")
        self.attendance_tree.heading("Status", text="Status")
        self.attendance_tree.column("Status", width=80)
        self.attendance_tree.heading("Course", text="Course")
        self.attendance_tree.grid(row=4, column=0, columnspan=2, pady=10)
        self.attendance_tree.bind("<Double-1>", self.toggle_attendance_status)

        tk.Button(self.record_attendance_tab, text="Save Attendance", command=self.save_attendance).grid(
            row=5, column=0, columnspan=2, pady=10)

    def create_view_attendance_tab(self):
        """Configures the view saved attendance tab."""
        self.view_attendance_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.view_attendance_tab, text="View Saved Attendance")

        tk.Label(self.view_attendance_tab, text="Class ID:").grid(row=0, column=0, padx=10, pady=10)
        self.class_id_entry_view = tk.Entry(self.view_attendance_tab)
        self.class_id_entry_view.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.view_attendance_tab, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=10)
        self.date_entry_view = tk.Entry(self.view_attendance_tab)
        self.date_entry_view.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.view_attendance_tab, text="View Attendance", command=self.view_saved_attendance).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        self.attendance_view_tree = ttk.Treeview(self.view_attendance_tab,
                                                columns=("ID", "Name", "Status", "Course", "Date"),
                                                show="headings")
        self.attendance_view_tree.heading("ID", text="Student ID")
        self.attendance_view_tree.heading("Name", text="Student Name")
        self.attendance_view_tree.heading("Status", text="Status")
        self.attendance_view_tree.column("Status", width=80)
        self.attendance_view_tree.heading("Course", text="Course")
        self.attendance_view_tree.heading("Date", text="Date")
        self.attendance_view_tree.grid(row=4, column=0, columnspan=2, pady=10)

    def register_student(self):
        """Registers a new student in the database."""
        student_id = self.reg_entries["student_id"].get()
        class_id = self.reg_entries["class_id"].get()
        student_name = self.reg_entries["student_name"].get()
        course = self.reg_entries["course"].get()

        if not all([student_id, class_id, student_name, course]):
            messagebox.showerror("Error", "All registration fields are required.")
            return

        try:
            self.cursor.execute("INSERT INTO students (student_id, name, course) VALUES (%s, %s, %s)",
                                (student_id, student_name, course))
            self.cursor.execute("INSERT INTO attendance (student_id, class_id) VALUES (%s, %s)",
                                (student_id, class_id))
            self.conn.commit()
            messagebox.showinfo("Success", f"Student '{student_name}' registered successfully!")
            self.clear_registration_entries()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not register student: {err}")

    def clear_registration_entries(self):
        """Clears the entry fields in the student registration tab."""
        for entry in self.reg_entries.values():
            entry.delete(0, tk.END)

    def load_students_for_attendance(self):
        """Loads students for a given class into the attendance treeview."""
        class_id = self.class_id_entry_record.get()
        if not class_id:
            messagebox.showerror("Error", "Please enter a Class ID to load students.")
            return

        try:
            self.cursor.execute("""
                SELECT s.student_id, s.name, a.present, s.course
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.class_id = %s
            """, (class_id,))
            students_data = self.cursor.fetchall()

            for item in self.attendance_tree.get_children():
                self.attendance_tree.delete(item)

            for student in students_data:
                status = "Present" if student[2] == 1 else "Absent"
                self.attendance_tree.insert("", "end", values=(student[0], student[1], status, student[3]))

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load students: {err}")

    def toggle_attendance_status(self, event):
        """Toggles the attendance status of a selected student in the treeview."""
        selected_item = self.attendance_tree.focus()
        if not selected_item:
            return

        current_values = self.attendance_tree.item(selected_item, "values")
        new_status = "Absent" if current_values[2] == "Present" else "Present"
        self.attendance_tree.item(selected_item, values=(current_values[0], current_values[1], new_status, current_values[3]))

    def save_attendance(self):
        """Saves the current attendance records to the database."""
        class_id = self.class_id_entry_record.get()
        current_datetime = self.date_entry_record.get()

        if not class_id:
            messagebox.showerror("Error", "Please enter a Class ID to save attendance.")
            return

        try:
            for item in self.attendance_tree.get_children():
                student_id, _, status, _ = self.attendance_tree.item(item)["values"]
                present_value = 1 if status == "Present" else 0

                self.cursor.execute("""
                    UPDATE attendance
                    SET present = %s
                    WHERE student_id = %s AND class_id = %s
                """, (present_value, student_id, class_id))

                self.cursor.execute("""
                    UPDATE students
                    SET date = %s
                    WHERE student_id = %s
                """, (current_datetime, student_id))

            self.conn.commit()
            messagebox.showinfo("Success", "Attendance saved successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to save attendance: {err}")

    def view_saved_attendance(self):
        """Displays saved attendance records based on class ID and date."""
        class_id = self.class_id_entry_view.get()
        attendance_date = self.date_entry_view.get()

        if not all([class_id, attendance_date]):
            messagebox.showerror("Error", "Please enter both Class ID and Date to view saved attendance.")
            return

        try:
            query = """
                SELECT s.student_id, s.name, a.present, s.course, s.date
                FROM students s
                JOIN attendance a ON s.student_id = a.student_id
                WHERE a.class_id = %s AND s.date = %s
            """
            self.cursor.execute(query, (class_id, attendance_date))
            results = self.cursor.fetchall()

            for item in self.attendance_view_tree.get_children():
                self.attendance_view_tree.delete(item)

            for row in results:
                status = "Present" if row[2] == 1 else "Absent"
                self.attendance_view_tree.insert("", "end", values=(row[0], row[1], status, row[3], row[4]))

            if not results:
                messagebox.showinfo("No Data", "No attendance records found for the specified class and date.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve saved attendance: {err}")

    def __del__(self):
        """Ensures database connection is closed when the application exits."""
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = InstructorInterface(root)
    root.mainloop()