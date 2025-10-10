-- Training Management System Database Schema
-- Version: 1.0
-- Description: This script creates the database, all required tables, and inserts initial data.

-- Create and use the database
CREATE DATABASE IF NOT EXISTS training_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE training_management;

--
-- Table structure for table `users`
--
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(15),
    profile_picture VARCHAR(255),
    qualifications TEXT,
    role ENUM('super_admin', 'admin', 'trainer', 'student') NOT NULL,
    gender ENUM('Male', 'Female') NOT NULL DEFAULT 'Male',
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
);

--
-- Table structure for table `courses`
--
CREATE TABLE courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
);

--
-- Table structure for table `course_admins`
--
CREATE TABLE course_admins (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT,
    admin_id INT,
    assigned_date DATE DEFAULT (CURRENT_DATE),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_course_admin (course_id, admin_id)
);

--
-- Table structure for table `course_trainers`
--
CREATE TABLE course_trainers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT,
    trainer_id INT,
    assigned_date DATE DEFAULT (CURRENT_DATE),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (trainer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_course_trainer (course_id, trainer_id)
);

--
-- Table structure for table `students`
--
CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE,
    course_id INT,
    enrollment_date DATE DEFAULT (CURRENT_DATE),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE SET NULL
);

--
-- Table structure for table `batches`
--
CREATE TABLE batches (
    batch_id INT PRIMARY KEY AUTO_INCREMENT,
    batch_name VARCHAR(255) NOT NULL,
    course_id INT,
    start_date DATE,
    end_date DATE,
    max_students INT DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    personal_leave_limit INT DEFAULT 5,
    medical_leave_limit INT NULL,
    academic_leave_limit INT NULL,
    special_leave_limit INT NULL,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
);

--
-- Table structure for table `batch_students`
--
CREATE TABLE batch_students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id INT,
    student_id INT,
    enrolled_date DATE DEFAULT (CURRENT_DATE),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    UNIQUE KEY unique_batch_student (batch_id, student_id)
);

--
-- Table structure for table `topics`
--
CREATE TABLE topics (
    topic_id INT PRIMARY KEY AUTO_INCREMENT,
    topic_name VARCHAR(255) NOT NULL,
    description TEXT,
    course_id INT,
    trainer_id INT,
    batch_id INT,
    parent_topic_id INT NULL,
    sequence_order INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (trainer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id) ON DELETE SET NULL,
    FOREIGN KEY (parent_topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

--
-- Table structure for table `assignments`
--
CREATE TABLE assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    topic_id INT,
    batch_id INT,
    created_by INT,
    due_date DATETIME,
    assignment_type ENUM('individual', 'group') DEFAULT 'individual',
    max_points INT DEFAULT 100,
    evaluation_type ENUM('none', 'python', 'sql', 'excel', 'web') NULL DEFAULT 'none',
    file_path VARCHAR(500),
    test_case_file_path VARCHAR(500) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

--
-- Table structure for table `assignment_submissions`
--
CREATE TABLE assignment_submissions (
    submission_id INT PRIMARY KEY AUTO_INCREMENT,
    assignment_id INT,
    student_id INT,
    submission_text TEXT,
    file_path VARCHAR(500),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_late BOOLEAN DEFAULT FALSE,
    evaluation_status ENUM('pending', 'processing', 'completed', 'error') NOT NULL DEFAULT 'pending',
    grade INT DEFAULT NULL,
    auto_grade INT NULL,
    feedback TEXT,
    auto_feedback TEXT NULL,
    evaluation_output TEXT NULL,
    graded_by INT DEFAULT NULL,
    graded_at TIMESTAMP NULL,
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (graded_by) REFERENCES users(user_id),
    UNIQUE KEY unique_assignment_student (assignment_id, student_id)
);

--
-- Table structure for table `attendance`
--
CREATE TABLE attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    course_id INT,
    batch_id INT,
    attendance_date DATE,
    is_present BOOLEAN DEFAULT FALSE,
    marked_by INT,
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id) ON DELETE SET NULL,
    FOREIGN KEY (marked_by) REFERENCES users(user_id),
    UNIQUE KEY unique_student_date (student_id, attendance_date)
);

--
-- Table structure for table `leave_types`
--
CREATE TABLE IF NOT EXISTS leave_types (
    leave_type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(100) NOT NULL,
    description TEXT,
    has_limit BOOLEAN NOT NULL DEFAULT TRUE,
    default_limit_days INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

--
-- Table structure for table `leave_applications`
--
CREATE TABLE leave_applications (
    leave_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    batch_id INT,
    leave_type_id INT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    days_requested INT NOT NULL DEFAULT 1,
    supporting_document VARCHAR(500),
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by INT DEFAULT NULL,
    reviewed_at TIMESTAMP NULL,
    admin_comments TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id) ON DELETE SET NULL,
    FOREIGN KEY (leave_type_id) REFERENCES leave_types(leave_type_id) ON DELETE SET NULL,
    FOREIGN KEY (reviewed_by) REFERENCES users(user_id)
);

--
-- Table structure for table `student_leave_allowances`
--
CREATE TABLE IF NOT EXISTS student_leave_allowances (
    allowance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    batch_id INT,
    leave_type_id INT,
    allowed_days INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id) ON DELETE CASCADE,
    FOREIGN KEY (leave_type_id) REFERENCES leave_types(leave_type_id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_batch_leave_type (student_id, batch_id, leave_type_id)
);

--
-- Table structure for table `password_resets`
--
CREATE TABLE password_resets (
    reset_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    reset_token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

--
-- Table structure for table `activity_logs`
--
CREATE TABLE activity_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(255) NOT NULL,
    table_affected VARCHAR(100),
    record_id INT,
    description TEXT,
    old_values JSON,
    new_values JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

--
-- Inserting initial data
--

-- Insert initial super admin user (password: admin123)
INSERT INTO users (email, password_hash, full_name, first_name, last_name, phone, role, is_active) 
VALUES ('superadmin@trainingsystem.com', '$2b$12$BOxFf9nc7KmOsrGsI5wcres4GX/kML3FmTe.6gTXRKcxf9BOnMeGO', 'Super Administrator', 'Super', 'Admin', '1234567890', 'super_admin', TRUE);

-- Insert leave types
INSERT INTO leave_types (type_name, description, has_limit, default_limit_days) VALUES ('Personal', 'General personal leave.', TRUE, 5);
INSERT INTO leave_types (type_name, description, has_limit, default_limit_days) VALUES ('Medical', 'Leave for health reasons.', FALSE, NULL);
INSERT INTO leave_types (type_name, description, has_limit, default_limit_days) VALUES ('Academic', 'Leave for educational purposes.', FALSE, NULL);
INSERT INTO leave_types (type_name, description, has_limit, default_limit_days) VALUES ('Special', 'Leave for exceptional circumstances.', FALSE, NULL);

--
-- Creating indexes for performance
--
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_assignments_due_date ON assignments(due_date);
CREATE INDEX idx_attendance_date ON attendance(attendance_date);
CREATE INDEX idx_leaves_status ON leave_applications(status);