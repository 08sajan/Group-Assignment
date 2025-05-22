-- Select the attendance_system database.
-- Make sure this database already exists from your previous step.
USE attendance_system;

-- Drop tables if they already exist to avoid errors if you run this multiple times
-- You can comment these lines out after the first successful run.
-- DROP TABLE IF EXISTS attendance;
-- DROP TABLE IF EXISTS students;


-- Create the 'students' table to store student information
CREATE TABLE students (
    student_id VARCHAR(50) PRIMARY KEY, -- Unique identifier for each student
    name VARCHAR(100) NOT NULL,        -- Student's full name (cannot be empty)
    course VARCHAR(100),               -- The course the student is enrolled in
    date DATETIME                      -- Used in Python for the date of attendance marking
);

-- Create the 'attendance' table to store attendance records
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique ID for each attendance record
    student_id VARCHAR(50) NOT NULL,              -- Student ID, links to the students table
    class_id VARCHAR(50) NOT NULL,                -- The ID of the class attended
    present BOOLEAN DEFAULT 0,                    -- Attendance status: 0 for Absent, 1 for Present (default is Absent)
    
    -- Define a foreign key constraint to link student_id to the students table
    -- ON DELETE CASCADE means if a student is deleted, their attendance records are also deleted
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- Optional: You can run these commands after creation to verify the table structures
-- DESCRIBE students;
-- DESCRIBE attendance;