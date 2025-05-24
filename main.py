import os
from datetime import datetime, date
import mysql.connector

# --- Get the directory where this script is located ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # Use abspath for reliability
STUDENTS_FILE = os.path.join(SCRIPT_DIR, "students.txt")
ATTENDANCE_FILE = os.path.join(SCRIPT_DIR, "attendance.txt")

# --- Hardcoded Routine Data (as in Student.py) ---
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
]

# Create a mapping for easier lookup
SUBJECT_TO_CLASS = {}
ROUTINE_SUBJECT_NAMES = [] # This will hold the 8 unique subjects from ROUTINE_DATA
for class_id, _, subject, _, _, _ in ROUTINE_DATA:
    if subject not in ROUTINE_SUBJECT_NAMES:
        ROUTINE_SUBJECT_NAMES.append(subject)
    if subject not in SUBJECT_TO_CLASS:
        SUBJECT_TO_CLASS[subject] = []
    SUBJECT_TO_CLASS[subject].append(class_id)
ROUTINE_SUBJECT_NAMES.sort()


class AttendanceSystemCLI:
    """
    Manages the core logic of the attendance system (CLI only),
    interacting with a MySQL database.
    """
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'sajan111', # IMPORTANT:  MySQL root password
            'database': 'attendance_system'
        }
        self.conn = None
        self.cursor = None
        if not self.connect_db():
            print("FATAL: Could not connect to database. CLI cannot operate.")

    def connect_db(self):
        """Establishes connection to the MySQL database."""
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor(dictionary=True) # Use dictionary cursor
            # print("Successfully connected to the database (CLI).") # Can be noisy
            return True
        except mysql.connector.Error as err:
            print(f"Error: Failed to connect to database (CLI): {err}")
            self.conn = None
            self.cursor = None
            return False

    def close_db(self):
        """Closes the database connection."""
        if self.cursor: self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()
            # print("CLI: Database connection closed.") 

    def _update_text_file(self, file_path, student_id_to_remove, id_index=0):
        """Helper function to remove lines from students.txt or attendance.txt."""
        try:
            with open(file_path, "r") as f: lines = f.readlines()
            updated = False
            with open(file_path, "w") as f:
                for line in lines:
                    parts = line.strip().split(',')
                    if len(parts) > id_index and parts[id_index] == student_id_to_remove:
                        updated = True
                        continue
                    f.write(line)
            if updated: print(f"Updated {os.path.basename(file_path)}.")
        except FileNotFoundError: print(f"Warning: {os.path.basename(file_path)} not found.")
        except IOError as e: print(f"Error updating {os.path.basename(file_path)}: {e}")

    def register_student(self, student_id, name, password, course=None, class_id=None):
        """Registers a student (basic info) in DB and students.txt."""
        if not self.conn or not self.cursor: print("Database not connected."); return
        try:
            self.cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (student_id,))
            if self.cursor.fetchone(): print(f"Error: Student ID {student_id} already exists."); return

            sql = "INSERT INTO students (student_id, name, password, course, class_id) VALUES (%s, %s, %s, %s, %s)"
            val = (student_id, name, password, course, class_id)
            self.cursor.execute(sql, val)
            self.conn.commit()
            print(f"Student {name} registered successfully!")
            try:
                with open(STUDENTS_FILE, "a") as f: f.write(f"{student_id},{name}\n")
                print("Appended basic info to students.txt.")
            except IOError as e: print(f"Error writing to students.txt: {e}")
            print("Info: Ensure SQL script for subject assignment is run for new students if needed, or use Instructor GUI for subject selection.")
        except mysql.connector.Error as err:
            print(f"DB error registering student: {err}"); self.conn.rollback()

    def mark_attendance(self, student_id, status, class_id, attendance_date_str):
        """Marks attendance (by class_id) in DB and appends to attendance.txt."""
        if not self.conn or not self.cursor: print("Database not connected."); return
        try: attendance_date = datetime.strptime(attendance_date_str, "%Y-%m-%d").date()
        except ValueError: print("Error: Invalid date format. Use YYYY-MM-DD."); return

        present_value = 1 if status.lower() == 'present' else 0

        try:
            self.cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (student_id,))
            if not self.cursor.fetchone(): print(f"Error: Student ID {student_id} does not exist."); return

            sql = """
                INSERT INTO attendance (student_id, class_id, date, present)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE present = VALUES(present)
            """
            self.cursor.execute(sql, (student_id, class_id, attendance_date, present_value))
            self.conn.commit()
            print(f"Attendance for {student_id} in class {class_id} on {attendance_date_str} marked as {status}.")
            try:
                current_time = datetime.now().strftime('%H:%M')
                with open(ATTENDANCE_FILE, "a") as f: f.write(f"{attendance_date_str},{student_id},{status.capitalize()},{current_time}\n")
                print("Appended record to attendance.txt.")
            except IOError as e: print(f"Error writing to attendance.txt: {e}")
        except mysql.connector.Error as err:
            print(f"DB error marking attendance: {err}"); self.conn.rollback()

    def mark_attendance_by_subject(self):
        """Marks attendance by selecting a subject first."""
        print("--- Mark Attendance by Subject ---")
        sid = input("Enter Student ID: ").strip()
        if not sid: print("Student ID required."); return

        try:
            self.cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (sid,))
            if not self.cursor.fetchone():
                print(f"Error: Student with ID {sid} does not exist.")
                return
        except mysql.connector.Error as err:
            print(f"DB error checking student: {err}"); return


        date_str_input = input(f"Enter Date (YYYY-MM-DD, default: today {date.today().strftime('%Y-%m-%d')}): ").strip()
        if not date_str_input: date_str_input = date.today().strftime('%Y-%m-%d')

        print("\nAvailable Subjects (from Routine):")
        for i, subj_name in enumerate(ROUTINE_SUBJECT_NAMES, 1):
            print(f"{i}. {subj_name}")

        subj_choice_idx = input("Enter the number of the subject: ").strip()
        try:
            selected_subject_name = ROUTINE_SUBJECT_NAMES[int(subj_choice_idx) - 1]
        except (ValueError, IndexError):
            print("Invalid subject choice."); return

        possible_classes = SUBJECT_TO_CLASS.get(selected_subject_name, [])
        class_id = None
        if not possible_classes:
            print(f"Error: No class found for subject {selected_subject_name} in routine."); return
        elif len(possible_classes) == 1:
            class_id = possible_classes[0]
            print(f"Using Class ID: {class_id} for {selected_subject_name}")
        else:
            print(f"Multiple classes teach {selected_subject_name}:")
            for i, cid_option in enumerate(possible_classes, 1):
                print(f"{i}. {cid_option}")
            class_choice_idx = input("Enter the number of the class: ").strip()
            try:
                class_id = possible_classes[int(class_choice_idx) - 1]
            except (ValueError, IndexError):
                print("Invalid class choice."); return

        status = ""
        while status.lower() not in ['present', 'absent']:
            status = input("Enter Status (Present/Absent): ").strip()

        if sid and class_id and status:
            self.mark_attendance(sid, status, class_id, date_str_input)
        else:
            print("Could not proceed. Missing information.")


    def delete_student(self, student_id):
        """Deletes a student from DB and updates text files."""
        if not self.conn or not self.cursor: print("Database not connected."); return
        try:
            self.cursor.execute("SELECT name FROM students WHERE student_id = %s", (student_id,))
            student = self.cursor.fetchone()
            if not student: print(f"Error: Student ID {student_id} does not exist."); return

            confirm = input(f"WARNING: Delete {student_id} ({student['name']}) & all records? (yes/no): ").lower()
            if confirm != 'yes': print("Deletion cancelled."); return

            self.cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
            self.conn.commit()
            print(f"Student {student_id} deleted from database (related records in 'attendance' and 'student_subjects' are handled by CASCADE).")

            self._update_text_file(STUDENTS_FILE, student_id, id_index=0)
            self._update_text_file(ATTENDANCE_FILE, student_id, id_index=1)
        except mysql.connector.Error as err:
            print(f"DB error deleting student: {err}"); self.conn.rollback()

    def view_students_with_subjects(self): # MODIFIED FUNCTION
        """Displays all students and their enrolled subjects, filtered by routine subjects."""
        if not self.conn or not self.cursor: print("Database not connected."); return
        try:
            self.cursor.execute("SELECT student_id, name, course, class_id FROM students ORDER BY name")
            students = self.cursor.fetchall()
            if not students: print("No students registered."); return

            print("\n--- Registered Students & Their Subjects (Filtered by Routine) ---")
            print(f"{'ID':<12} | {'Name':<25} | {'Course':<15} | {'Routine Subjects Enrolled'}")
            print("-" * 120) # Adjusted width

            for student in students:
                # Fetch ALL subjects the student is actually enrolled in from the DB
                self.cursor.execute("""
                    SELECT sub.subject_name FROM subjects sub
                    JOIN student_subjects ss ON sub.subject_id = ss.subject_id
                    WHERE ss.student_id = %s ORDER BY sub.subject_name
                """, (student['student_id'],))
                all_enrolled_db_subjects = [s['subject_name'] for s in self.cursor.fetchall()]

                # Filter these DB subjects to show only those present in ROUTINE_SUBJECT_NAMES
                display_subjects = [s_name for s_name in all_enrolled_db_subjects if s_name in ROUTINE_SUBJECT_NAMES]
                
                
                if not all_enrolled_db_subjects and student['name'] == "Frienson Pradhan": # Example specific handling if needed
                     subject_names_str = "None (or registration needs subject assignment)"
                elif not display_subjects and all_enrolled_db_subjects: # Enrolled in subjects, but none are 'routine' ones
                    subject_names_str = "None from routine (enrolled in others)"
                elif not display_subjects:
                    subject_names_str = "None"
                else:
                    subject_names_str = ", ".join(display_subjects)

                print(f"{student['student_id']:<12} | {student['name']:<25} | {student.get('course') or 'N/A':<15} | {subject_names_str}")
        except mysql.connector.Error as err: print(f"Error viewing students: {err}")


    def view_attendance_records(self):
        """Displays all attendance records."""
        if not self.conn or not self.cursor: print("Database not connected."); return
        try:
            self.cursor.execute("""
                SELECT s.student_id, s.name, a.class_id, a.present, a.date FROM attendance a
                JOIN students s ON a.student_id = s.student_id ORDER BY a.date DESC, s.name ASC
            """)
            records = self.cursor.fetchall()
            if not records: print("No attendance records found."); return
            print("--- All Attendance Records (from DB) ---")
            print(f"{'Student ID':<12} | {'Name':<20} | {'Class ID':<10} | {'Status':<7} | {'Date':<10}")
            print("-" * 70)
            for record in records:
                status = "Present" if record['present'] == 1 else "Absent"
                date_str = record['date'].strftime('%Y-%m-%d') if record['date'] else 'N/A'
                print(f"{record['student_id']:<12} | {record['name']:<20} | {record.get('class_id') or 'N/A':<10} | {status:<7} | {date_str}")
        except mysql.connector.Error as err: print(f"Error viewing attendance: {err}")


def print_main_menu_cli():
    """Prints the main menu options."""
    print("\n" + "="*40)
    print("  STUDENT ATTENDANCE SYSTEM (CLI)")
    print("="*40)
    print("1. Register Student (Basic)")
    print("2. Mark Attendance by Subject")
    print("3. Mark Attendance by Class ID")
    print("4. View Students & Their Subjects (Routine Filtered)") 
    print("5. View All Attendance Records")
    print("6. Delete Student")
    print("7. Exit")

def run_cli_interface():
    """Main function to run the command-line interface."""
    system = AttendanceSystemCLI()
    if not system.conn or not system.cursor: print("Exiting: DB connection failed."); return

    try:
        while True:
            print_main_menu_cli()
            choice = input("Enter choice (1-7): ").strip()

            if choice == '1':
                print("\n--- Register New Student ---")
                sid = input("Enter Student ID: ").strip()
                name = input("Enter Student Name: ").strip()
                pwd = input("Enter Student Password: ").strip()
                course = input("Enter Primary Course (optional): ").strip() or None
                cid = input("Enter Primary Class ID (optional): ").strip() or None
                if sid and name and pwd: system.register_student(sid, name, pwd, course, cid)
                else: print("ID, Name, and Password required.")
            elif choice == '2':
                system.mark_attendance_by_subject()
            elif choice == '3':
                print("\n--- Mark Attendance by Class ---")
                sid = input("Enter Student ID: ").strip()
                cid = input("Enter Class ID: ").strip()
                # --- Using dynamic date for "Mark by Class" too ---
                date_str_input = input(f"Enter Date (YYYY-MM-DD, default: today {date.today().strftime('%Y-%m-%d')}): ").strip()
                if not date_str_input: date_str_input = date.today().strftime('%Y-%m-%d')
                # ---
                status = input("Enter Status (Present/Absent): ").strip()
                if sid and cid and status.lower() in ['present', 'absent']:
                    system.mark_attendance(sid, status, cid, date_str_input)
                else: print("ID, Class ID, and Status required.")
            elif choice == '4':
                system.view_students_with_subjects()
            elif choice == '5':
                system.view_attendance_records()
            elif choice == '6':
                print("\n--- Delete Student ---")
                sid = input("Enter Student ID to DELETE: ").strip()
                if sid: system.delete_student(sid)
                else: print("Student ID required.")
            elif choice == '7':
                print("Exiting. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")

    except KeyboardInterrupt: print("\nExiting.")
    finally: system.close_db()

if __name__ == "__main__":
    run_cli_interface()