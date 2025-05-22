import tkinter as tk
from tkinter import ttk

class StudentRoutineInterface:
    # Class-level constant for the routine data, now including Class ID
    ROUTINE_DATA = [
        # Format: (Class ID, Day, Subject, Time, Teacher, Location)
        ("C1", "Monday", "Mathematics", "9:00 AM - 11:00 AM", "Mr.kc", "Room 11"),
        ("C2", "Monday", "English", "10:15 AM - 12:15 PM", "Ms.Nimi", "Room 8"),
        ("C3", "Tuesday", "Science", "8:00 AM - 11:00 AM", "Dr.Upendra", "Room 1"),
        ("C4", "Tuesday", "History", "10:15 AM - 12:15 PM", "Mr.Rana", "Room 22"),
        ("C5", "Wednesday", "Art", "8:00 AM - 10:00 AM", "Ms.Guras", "Room 13"),
        ("C6", "Wednesday", "Economics", "9:15 AM - 11:15 AM", "Mrs.Fulmaya", "Room 7"),
        ("C7", "Thursday", "Mathematics", "8:00 AM - 10:00 AM", "Mr.kc", "Room 10"),
        ("C8", "Thursday", "Chemistry", "9:15 AM - 11:15 AM", "Dr.Biste", "Lab 5"),
        ("C9", "Friday", "Biology", "8:00 AM - 10:00 AM", "Dr.Ram", "Room 4"),
    ]

    def __init__(self, root):
        """
        Initializes the StudentRoutineInterface.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("Routine")
        # Made the window a bit wider to fit the new Class ID column
        self.root.geometry("900x400")

        # Set up the table that will show the class routine
        self._setup_routine_treeview()

    def _setup_routine_treeview(self):
        """
        Orchestrates the creation, configuration, and population of the routine Treeview.
        """
        self._create_treeview_widget()
        self._configure_treeview_columns()
        self._populate_treeview_with_data()

    def _create_treeview_widget(self):
        """
        Creates and packs the ttk.Treeview widget for displaying the routine.
        """
        # Added "class_id" as a new column in the table
        self.columns = ("class_id", "day", "subject", "time", "teacher", "location")

        # Set up the table with the columns
        self.routine_tree = ttk.Treeview(self.root, columns=self.columns, show="headings")
        self.routine_tree.pack(fill="both", expand=True)

    def _configure_treeview_columns(self):
        """
        Defines the column headings and widths for the routine Treeview.
        """
        # Added "class_id" heading and width
        column_headings = {
            "class_id": "Class ID",
            "day": "Day",
            "subject": "Subject",
            "time": "Time",
            "teacher": "Teacher",
            "location": "Location"
        }
        # Added "class_id" width
        column_widths = {
            "class_id": 80, # Adjust width as needed
            "day": 100,
            "subject": 150,
            "time": 100,
            "teacher": 150,
            "location": 100
        }

        for col_id in self.columns:
            self.routine_tree.heading(col_id, text=column_headings[col_id])
            self.routine_tree.column(col_id, width=column_widths[col_id])

    def _populate_treeview_with_data(self):
        """
        Inserts the predefined routine data into the Treeview.
        """
        # This part stays the same just adds each row of data into the ta
        for entry in self.ROUTINE_DATA:
            self.routine_tree.insert("", "end", values=entry)


# Run the Student app
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentRoutineInterface(root)
    root.mainloop()