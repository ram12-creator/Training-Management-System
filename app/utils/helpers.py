
# _____________________________________________________


import re                      # For regular expressions (used in validation).
import bcrypt                  # For secure password hashing.
import random                  # For generating random choices (used in password reset tokens).
import string                  # Provides constants for string characters.
from datetime import datetime, timedelta # For date and time operations.
from flask import current_app  # To access Flask application context (like DB config).
import mysql.connector         # For interacting with MySQL database.
from flask import request      # To access request object (e.g., for IP address logging).

# --- Password Generation and Verification ---

def generate_password(last_name, phone_number):
    """
    Generates a raw password based on the user's last name and phone number.
    This is typically for initial account creation or temporary passwords.
    """
    # Extracts only the digits from the phone number string using regex.
    phone_digits = re.sub(r'\D', '', phone_number)
    # Takes the last 5 digits, padding with zeros if fewer than 5.
    last_five = phone_digits[-5:] if len(phone_digits) >= 5 else phone_digits.zfill(5)
    
    # Combines the last name (you might want to add .lower() or .strip() for consistency)
    # with the extracted phone digits to form a raw password.
    raw_password = f"{last_name}{last_five}"
    return raw_password

def hash_password(password):
    """
    Hashes a given password using bcrypt for secure storage.
    """
    # Encodes password to bytes, generates a salt, hashes, and decodes back to string.
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verifies if a plain text password matches a stored bcrypt hash.
    """
    # Encodes both password and hash to bytes for comparison with bcrypt.
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_reset_token():
    """
    Generates a random, URL-safe token for password reset links.
    """
    # Creates a 32-character token using alphanumeric characters.
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# --- Statistics Helper Functions ---

def get_course_stats(course_id):
    """
    Fetches high-level statistics for a specific course.
    """
    conn = current_app.get_db_connection()
    stats = {
        'total_students': 0,
        'active_students': 0,
        'avg_attendance': 0
    }
    
    if not conn:
        return stats
        
    try:
        cursor = conn.cursor(dictionary=True)
        # Get total and active students for the course
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN s.is_active = TRUE THEN 1 ELSE 0 END) as active
            FROM students s 
            WHERE s.course_id = %s
        """, (course_id,))
        student_data = cursor.fetchone()
        if student_data:
            stats['total_students'] = student_data.get('total', 0)
            stats['active_students'] = student_data.get('active', 0)
        
        # Get average attendance for the course
        cursor.execute("""
            SELECT AVG(is_present) * 100 as avg_att
            FROM attendance 
            WHERE course_id = %s
        """, (course_id,))
        attendance_data = cursor.fetchone()
        if attendance_data and attendance_data['avg_att'] is not None:
            stats['avg_attendance'] = round(attendance_data['avg_att'], 1)
        
    except mysql.connector.Error as err:
        print(f"Error getting course stats: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    
    return stats

def get_user_stats(user_id, role):
    """
    Fetches statistics relevant to a specific user based on their role.
    """
    conn = current_app.get_db_connection()
    stats = {
        'total_courses': 0, 'total_students': 0, 'pending_leaves': 0, 'active_batches': 0,
        'total_topics': 0, 'total_assignments': 0, 'attendance_percentage': 0,
        'max_leaves': 0, 'remaining_leaves': 0, 'submitted_assignments': 0, 'avg_grade': 0
    }
    
    if not conn:
        return stats

    try:
        cursor = conn.cursor(dictionary=True)
        
        if role == 'admin':
            # Fetches statistics for an Admin user's dashboard.
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT ca.course_id) as total_courses,
                    COUNT(DISTINCT s.student_id) as total_students,
                    (SELECT COUNT(*) FROM leave_applications la_in
                     JOIN students s_in ON la_in.student_id = s_in.student_id
                     JOIN course_admins ca_in ON s_in.course_id = ca_in.course_id
                     WHERE ca_in.admin_id = ca.admin_id AND la_in.status = 'pending') as pending_leaves,
                    (SELECT COUNT(*) FROM batches b_in
                     JOIN course_admins ca_in ON b_in.course_id = ca_in.course_id
                     WHERE ca_in.admin_id = ca.admin_id AND b_in.is_active = TRUE) as active_batches
                FROM course_admins ca
                LEFT JOIN students s ON ca.course_id = s.course_id
                WHERE ca.admin_id = %s
                GROUP BY ca.admin_id
            """, (user_id,))
            admin_stats = cursor.fetchone()
            if admin_stats:
                stats.update(admin_stats)

        elif role == 'trainer':
            # Fetches statistics for a Trainer user's dashboard.
            cursor.execute("""
                SELECT
                    -- Count active batches in courses this trainer is assigned to
                    (SELECT COUNT(*) FROM batches b 
                     JOIN course_trainers ct_in ON b.course_id = ct_in.course_id 
                     WHERE ct_in.trainer_id = %s AND b.is_active = TRUE) as active_batches,

                    -- Count total students in courses this trainer is assigned to
                    (SELECT COUNT(DISTINCT bs.student_id) FROM batch_students bs
                     JOIN batches b ON bs.batch_id = b.batch_id
                     JOIN course_trainers ct_in ON b.course_id = ct_in.course_id
                     WHERE ct_in.trainer_id = %s) as total_students,
                     
                    -- Calculate average grade across all assignments created by this trainer
                    (SELECT AVG(
                        CASE 
                            WHEN grade IS NOT NULL THEN grade 
                            ELSE auto_grade 
                        END
                     ) FROM assignment_submissions 
                     WHERE assignment_id IN (SELECT assignment_id FROM assignments WHERE created_by = %s)) as average_grade,

                    -- Count submissions that are submitted but not yet graded (manually or automatically)
                    (SELECT COUNT(*) FROM assignment_submissions
                     WHERE grade IS NULL AND auto_grade IS NULL AND evaluation_status != 'processing'
                     AND assignment_id IN (SELECT assignment_id FROM assignments WHERE created_by = %s)) as ungraded_submissions

            """, (user_id, user_id, user_id, user_id))
            
            trainer_stats = cursor.fetchone()
            if trainer_stats:
                stats.update(trainer_stats)
                # Ensure numbers are nicely formatted
                stats['average_grade'] = round(stats.get('average_grade', 0) or 0, 1)
        
        elif role == 'student':
            # ===============================================================
            # CORRECTED & FINAL QUERY for student dashboard KPIs
            # ===============================================================
            cursor.execute("""
                SELECT
                    COALESCE(AVG(att.is_present) * 100, 0) as attendance_percentage,
                    
                    -- Get the personal leave limit from the student's current BATCH
                    b.personal_leave_limit as max_leaves,
                    
                    -- Correctly calculate remaining leaves by subtracting ONLY approved PERSONAL leaves
                    (b.personal_leave_limit - (
                        SELECT COALESCE(SUM(la.days_requested), 0) 
                        FROM leave_applications la
                        JOIN leave_types lt ON la.leave_type_id = lt.leave_type_id
                        WHERE la.student_id = s.student_id AND la.batch_id = bs.batch_id 
                          AND lt.type_name = 'Personal' AND la.status = 'approved'
                    )) as remaining_leaves,

                    (SELECT COUNT(*) FROM assignments a WHERE a.batch_id = bs.batch_id AND a.is_active = TRUE) as total_assignments,
                    (SELECT COUNT(*) FROM assignment_submissions asub WHERE asub.student_id = s.student_id) as submitted_assignments,
                    
                    -- Correctly calculate average grade by prioritizing manual grade over auto-grade
                    COALESCE((SELECT AVG(
                        CASE 
                            WHEN grade IS NOT NULL THEN grade 
                            ELSE auto_grade 
                        END
                    ) FROM assignment_submissions asub WHERE asub.student_id = s.student_id AND (grade IS NOT NULL OR auto_grade IS NOT NULL)), 0) as avg_grade
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                LEFT JOIN batch_students bs ON s.student_id = bs.student_id AND bs.is_active = TRUE
                LEFT JOIN batches b ON bs.batch_id = b.batch_id
                LEFT JOIN attendance att ON s.student_id = att.student_id
                WHERE s.user_id = %s
                GROUP BY s.student_id, b.personal_leave_limit, bs.batch_id
            """, (user_id,))
            
            student_stats = cursor.fetchone()
            if student_stats:
                stats.update(student_stats)
                # Ensure numbers are nicely formatted
                stats['attendance_percentage'] = round(stats.get('attendance_percentage', 0), 1)
                stats['avg_grade'] = round(stats.get('avg_grade', 0), 1)
                stats['remaining_leaves'] = max(0, stats.get('remaining_leaves', 0)) # Prevent negative leaves

    except mysql.connector.Error as err:
        print(f"Error getting user stats for role {role}: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    
    return stats