import os
from datetime import datetime

class AttendanceFileHandler:
    """
    Handles all file-related operations for the attendance system,
    abstracting away the details of reading from and writing to text files.
    """
    def __init__(self, students_file, attendance_file):
        self.students_file = students_file
        self.attendance_file = attendance_file

    def _read_lines(self, filename):
        """
        Private helper method to read all non-empty lines from a specified file.
        Returns an empty list if the file does not exist.
        """
        if not os.path.exists(filename):
            return []
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def _append_line(self, filename, line):
        """
        Private helper method to append a new line to a specified file.
        """
        with open(filename, 'a') as f:
            f.write(line + "")

    def add_student_record(self, student_id, name):
        """
        Appends a new student's ID and name to the students file.
        """
        self._append_line(self.students_file, f"{student_id},{name}")

    def add_attendance_entry(self, date, student_id, status, time):
        """
        Appends a new attendance record (date, student ID, status, time)
        to the attendance file.
        """
        self._append_line(self.attendance_file, f"{date},{student_id},{status},{time}")

    def get_all_students_data(self):
        """
        Reads all student records from the students file and parses them
        into a list of dictionaries.
        Each dictionary contains 'id' and 'name' keys.
        """
        students_data = []
        for line in self._read_lines(self.students_file):
            try:
                student_id, name = line.split(',')
                students_data.append({'id': student_id, 'name': name})
            except ValueError:
                # Silently skip malformed lines to match original behavior
                pass
        return students_data

    def get_all_attendance_data(self):
        """
        Reads all attendance records from the attendance file and parses them
        into a list of dictionaries.
        Each dictionary contains 'date', 'id', 'status', and 'time' keys.
        """
        attendance_data = []
        for line in self._read_lines(self.attendance_file):
            try:
                date, student_id, status, time = line.split(',')
                attendance_data.append({'date': date, 'id': student_id, 'status': status, 'time': time})
            except ValueError:
                # Silently skip malformed lines to match original behavior
                pass
        return attendance_data

class AttendanceSystem:
    """
    Manages the core logic of the attendance system, using a file handler
    to interact with persistent storage.
    """
    def __init__(self):
        # Initialize the file handler with the names of the data files
        self.file_handler = AttendanceFileHandler("students.txt", "attendance.txt")
    
    def register_student(self, student_id, name):
        """
        Registers a new student by adding their ID and name to the system.
        """
        try:
            self.file_handler.add_student_record(student_id, name)
            print(f"Student {name} registered successfully!")
        except Exception as e:
            print(f"Error: {e}")
    
    def mark_attendance(self, student_id, status):
        """
        Marks attendance for a given student with a specified status (Present/Absent).
        Records the current date and time.
        """
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M")
            
            self.file_handler.add_attendance_entry(current_date, student_id, status, current_time)
            print(f"Attendance marked: {student_id} - {status}")
        except Exception as e:
            print(f"Error: {e}")
    
    def view_students(self):
        """
        Displays all registered students. If no students are registered,
        it prints a corresponding message.
        """
        try:
            students = self.file_handler.get_all_students_data()
            
            if not students:
                print("No students registered yet.")
                return
            
            print("--- Registered Students ---")
            for student in students:
                print(f"ID: {student['id']}, Name: {student['name']}")
        except Exception as e:
            print(f"Error: {e}")
    
    def view_attendance(self):
        """
        Displays all recorded attendance records. If no records are found,
        it prints a corresponding message.
        """
        try:
            attendance_records = self.file_handler.get_all_attendance_data()
            
            if not attendance_records:
                print("No attendance records found.")
                return
            
            print("--- Attendance Records ---")
            print("Date       | ID   | Status  | Time")
            print("-" * 35)
            
            for record in attendance_records:
                print(f"{record['date']} | {record['id']:4} | {record['status']:7} | {record['time']}")
        except Exception as e:
            print(f"Error: {e}")

def print_main_menu():
    """
    Prints the main menu options for the attendance system.
    """
    print("" + "="*30)
    print("ATTENDANCE SYSTEM")
    print("="*30)
    print("1. Register Student")
    print("2. Mark Attendance")
    print("3. View Students")
    print("4. View Attendance")
    print("5. Exit")

def main():
    """
    The main function to run the command-line interface for the attendance system.
    """
    system = AttendanceSystem()
    
    while True:
        try:
            print_main_menu() # Display the menu
            
            choice = input("Enter choice (1-5): ")
            
            if choice == '1':
                student_id = input("Enter Student ID: ")
                name = input("Enter Student Name: ")
                system.register_student(student_id, name)
            
            elif choice == '2':
                student_id = input("Enter Student ID: ")
                status = input("Enter Status (Present/Absent): ")
                system.mark_attendance(student_id, status)
            
            elif choice == '3':
                system.view_students()
            
            elif choice == '4':
                system.view_attendance()
            
            elif choice == '5':
                print("See you next time!")
                break # Exit the loop and end the program
            
            else:
                print("Invalid choice!")
        
        except KeyboardInterrupt:
            print("See you next time!") # Handle Ctrl+C gracefully
            break
        except Exception as e:
            # Catch any unexpected errors and print them, matching original behavior
            print(f"Error: {e}")

if __name__ == "__main__":
    main()