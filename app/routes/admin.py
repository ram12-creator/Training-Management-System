
# ___________________________________________
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import User
from app.utils.helpers import generate_password, hash_password, get_user_stats
from app.utils.email_service import send_credentials_email,send_leave_status_email
from app.utils.validators import validate_email, validate_phone, validate_date_range
import mysql.connector
from datetime import datetime,timedelta
import csv
import io
from collections import defaultdict

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def before_request():
    """Protects all admin routes and ensures the user is an admin."""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('auth.login'))

def log_activity(user_id, action, table_affected, record_id, description):
    """Helper function to log admin activities."""
    conn = current_app.get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO activity_logs (user_id, action, table_affected, record_id, description, ip_address) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, action, table_affected, record_id, description, request.remote_addr)
            )
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error logging activity: {err}")
            conn.rollback()
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()





@admin_bp.route('/dashboard')
def dashboard():
    stats = get_user_stats(current_user.user_id, 'admin')
    
    conn = current_app.get_db_connection()
    chart_data = {}
    students_to_watch = []
    pending_leaves_list = []

    if not conn:
        flash('Database connection error. Could not load dashboard data.', 'danger')
        return render_template('admin/dashboard.html', stats=stats, chart_data={}, students_to_watch=[], pending_leaves_list=[])

    try:
        cursor = conn.cursor(dictionary=True)
        
        # --- 1. Fetch Data for Charts ---

        #  Chart 1: Course Popularity (by student enrollment)
        cursor.execute("""
            SELECT c.course_name, COUNT(s.student_id) as student_count
            FROM courses c
            JOIN students s ON c.course_id = s.course_id
            JOIN course_admins ca ON c.course_id = ca.course_id
            WHERE ca.admin_id = %s
            GROUP BY c.course_id, c.course_name
            ORDER BY student_count DESC
            LIMIT 7
        """, (current_user.user_id,))
        course_popularity = cursor.fetchall()
        chart_data['course_popularity'] = {
            'labels': [row['course_name'] for row in course_popularity],
            'data': [row['student_count'] for row in course_popularity]
        }

        #  Chart 2: Leave Applications Breakdown
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM leave_applications la
            JOIN students s ON la.student_id = s.student_id
            JOIN course_admins ca ON s.course_id = ca.course_id
            WHERE ca.admin_id = %s
            GROUP BY la.status
        """, (current_user.user_id,))
        leave_breakdown = cursor.fetchall()
        chart_data['leave_breakdown'] = {
            'labels': [row['status'].title() for row in leave_breakdown],
            'data': [row['count'] for row in leave_breakdown]
        }
        
        # NEW Chart 3: Assignment Submission Status
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN asub.grade IS NOT NULL THEN 1 ELSE 0 END) as graded,
                SUM(CASE WHEN asub.submission_id IS NOT NULL AND asub.grade IS NULL THEN 1 ELSE 0 END) as submitted_ungraded
            FROM assignment_submissions asub
            JOIN students s ON asub.student_id = s.student_id
            JOIN course_admins ca ON s.course_id = ca.course_id
            WHERE ca.admin_id = %s
        """, (current_user.user_id,))
        assignment_status = cursor.fetchone()
        chart_data['assignment_status'] = {
            'labels': ['Graded', 'Submitted (Needs Grading)'],
            'data': [
                int(assignment_status['graded']) if assignment_status and assignment_status['graded'] else 0,
                int(assignment_status['submitted_ungraded']) if assignment_status and assignment_status['submitted_ungraded'] else 0
            ]
        }

        # --- 2. Fetch Data for Reports (No Change) ---
        thirty_days_ago = datetime.now() - timedelta(days=30)
        cursor.execute("""
            SELECT u.full_name, b.batch_name, AVG(a.is_present) * 100 as attendance_pct
            FROM attendance a JOIN students s ON a.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id JOIN course_admins ca ON a.course_id = ca.course_id
            LEFT JOIN batch_students bs ON s.student_id = bs.student_id AND bs.is_active = TRUE
            LEFT JOIN batches b ON bs.batch_id = b.batch_id
            WHERE ca.admin_id = %s AND a.attendance_date >= %s
            GROUP BY u.user_id, u.full_name, b.batch_name
            HAVING attendance_pct < 75 ORDER BY attendance_pct ASC LIMIT 5
        """, (current_user.user_id, thirty_days_ago))
        students_to_watch = cursor.fetchall()
        
        cursor.execute("""
            SELECT u.full_name, la.start_date, la.end_date, la.leave_id
            FROM leave_applications la JOIN students s ON la.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id JOIN course_admins ca ON s.course_id = ca.course_id
            WHERE ca.admin_id = %s AND la.status = 'pending'
            ORDER BY la.applied_at ASC LIMIT 5
        """, (current_user.user_id,))
        pending_leaves_list = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f'Error retrieving dashboard data: {err}', 'danger')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('admin/dashboard.html', 
                           stats=stats, 
                           chart_data=chart_data,
                           students_to_watch=students_to_watch,
                           pending_leaves_list=pending_leaves_list)

# --- BATCH MANAGEMENT ROUTES (NEW & REFACTORED) ---



@admin_bp.route('/batches')
def batch_management():
    conn = current_app.get_db_connection()
    courses = []
    batches_by_course = {}
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.course_id, c.course_name 
                FROM courses c JOIN course_admins ca ON c.course_id = ca.course_id 
                WHERE ca.admin_id = %s AND c.is_active = TRUE
            """, (current_user.user_id,))
            courses = cursor.fetchall()
            
            course_ids = [c['course_id'] for c in courses]
            if course_ids:
                placeholders = ', '.join(['%s'] * len(course_ids))
                cursor.execute(f"""
                    SELECT b.*, c.course_name, COUNT(bs.student_id) as student_count
                    FROM batches b
                    JOIN courses c ON b.course_id = c.course_id
                    LEFT JOIN batch_students bs ON b.batch_id = bs.batch_id AND bs.is_active = TRUE
                    WHERE b.course_id IN ({placeholders})
                    GROUP BY b.batch_id
                    ORDER BY c.course_name, b.start_date DESC
                """, tuple(course_ids))
                batches = cursor.fetchall()
                for course in courses:
                    batches_by_course[course['course_id']] = {
                        'course_name': course['course_name'],
                        'batches': [b for b in batches if b['course_id'] == course['course_id']]
                    }
        except mysql.connector.Error as err:
            flash(f'Error retrieving batches: {err}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return render_template('admin/batch_management.html', courses=courses, batches_by_course=batches_by_course)



@admin_bp.route('/create_batch', methods=['POST'])
def create_batch():
    data = request.get_json()
    batch_name = data.get('batch_name')
    course_id = data.get('course_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    max_students = data.get('max_students')
    
    # --- Capture all new leave limits from the form ---
    personal_leave_limit = data.get('personal_leave_limit')
    medical_leave_limit = data.get('medical_leave_limit')
    academic_leave_limit = data.get('academic_leave_limit')
    special_leave_limit = data.get('special_leave_limit')
    
    # --- Validation (can be expanded for new fields if needed) ---
    errors = {}
    if not batch_name or len(batch_name) < 3: errors['batch_name'] = 'Name must be at least 3 characters.'
    if not course_id: errors['course_id'] = 'Please select a course.'
    if not start_date: errors['start_date'] = 'Start date is required.'
    if not end_date: errors['end_date'] = 'End date is required.'
    if start_date and end_date and end_date < start_date: errors['end_date'] = 'End date cannot be before start date.'
    if not max_students or not max_students.isdigit() or int(max_students) < 1: errors['max_students'] = 'Max students must be a positive number.'

    if errors:
        return jsonify({'success': False, 'errors': errors})

    conn = current_app.get_db_connection()
    try:
        cursor = conn.cursor()
        # --- MODIFIED INSERT STATEMENT with all leave limits ---
        cursor.execute(
            """INSERT INTO batches (batch_name, course_id, start_date, end_date, max_students, 
                                 personal_leave_limit, medical_leave_limit, academic_leave_limit, special_leave_limit, created_by) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (batch_name, course_id, start_date, end_date, int(max_students), 
             personal_leave_limit, medical_leave_limit, academic_leave_limit, special_leave_limit, current_user.user_id)
        )
        batch_id = cursor.lastrowid
        conn.commit()
        log_activity(current_user.user_id, 'create', 'batches', batch_id, f"Created batch: {batch_name}")
        return jsonify({'success': True, 'message': 'Batch created successfully!'})
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# ===============================================================
# MODIFICATION 2: Update Batch Update Logic
# ===============================================================
@admin_bp.route('/update_batch/<int:batch_id>', methods=['POST'])
def update_batch(batch_id):
    data = request.get_json()
    batch_name = data.get('batch_name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    max_students = data.get('max_students')
    is_active = data.get('is_active')
    
    # --- Capture all new leave limits from the form ---
    personal_leave_limit = data.get('personal_leave_limit')
    medical_leave_limit = data.get('medical_leave_limit')
    academic_leave_limit = data.get('academic_leave_limit')
    special_leave_limit = data.get('special_leave_limit')
    
    conn = current_app.get_db_connection()
    try:
        cursor = conn.cursor()
        # --- MODIFIED UPDATE STATEMENT with all leave limits ---
        cursor.execute(
            """UPDATE batches SET batch_name=%s, start_date=%s, end_date=%s, max_students=%s, is_active=%s, 
                                personal_leave_limit=%s, medical_leave_limit=%s, academic_leave_limit=%s, special_leave_limit=%s
               WHERE batch_id=%s""",
            (batch_name, start_date, end_date, max_students, is_active, 
             personal_leave_limit, medical_leave_limit, academic_leave_limit, special_leave_limit, batch_id)
        )
        conn.commit()
        log_activity(current_user.user_id, 'update', 'batches', batch_id, f"Updated batch: {batch_name}")
        return jsonify({'success': True, 'message': 'Batch updated successfully!'})
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()









@admin_bp.route('/delete_batch/<int:batch_id>', methods=['POST'])
def delete_batch(batch_id):
    conn = current_app.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM batch_students WHERE batch_id = %s AND is_active = TRUE", (batch_id,))
        if cursor.fetchone()['count'] > 0:
            return jsonify({'success': False, 'message': 'Cannot delete batch with enrolled students.'})
        
        cursor.execute("SELECT batch_name FROM batches WHERE batch_id = %s", (batch_id,))
        batch_name = cursor.fetchone()['batch_name']
        cursor.execute("DELETE FROM batches WHERE batch_id = %s", (batch_id,))
        conn.commit()
        log_activity(current_user.user_id, 'delete', 'batches', batch_id, f"Deleted batch: {batch_name}")
        return jsonify({'success': True, 'message': 'Batch deleted successfully.'})
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- STUDENT MANAGEMENT ROUTES (REFACTORED FOR BATCHES & AJAX) ---





@admin_bp.route('/students', defaults={'batch_id': None})
@admin_bp.route('/students/batch/<int:batch_id>')
def student_management(batch_id):
    conn = current_app.get_db_connection()
    students, courses, batches = [], [], []
    batch_name = None
    
    # --- GET FILTER/CONTEXT PARAMETERS ---
    selected_course_id = request.args.get('course_id', type=int)
    selected_batch_id = request.args.get('batch_id', type=int)

    # If a batch_id is in the URL path (e.g., /students/batch/5), it takes precedence
    if batch_id:
        selected_batch_id = batch_id

    if not conn:
        flash('Database connection error.', 'danger')
        return render_template('admin/student_management.html', students=[], courses=[], batches=[])
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Get all courses this admin manages (for modals)
        cursor.execute("""
            SELECT c.course_id, c.course_name FROM courses c JOIN course_admins ca ON c.course_id = ca.course_id 
            WHERE ca.admin_id = %s AND c.is_active = TRUE
        """, (current_user.user_id,))
        courses = cursor.fetchall()
        
        # Base query for students
        sql = """
            SELECT s.student_id, u.user_id, u.full_name, u.email, u.phone, u.is_active, u.gender,
                   c.course_name, c.course_id, b.batch_name, b.batch_id
            FROM students s 
            JOIN users u ON s.user_id = u.user_id 
            JOIN courses c ON s.course_id = c.course_id 
            JOIN course_admins ca ON c.course_id = ca.course_id
            LEFT JOIN batch_students bs ON s.student_id = bs.student_id AND bs.is_active = TRUE
            LEFT JOIN batches b ON bs.batch_id = b.batch_id 
            WHERE ca.admin_id = %s
        """
        params = [current_user.user_id]

        # Apply filters or context from URL
        if selected_course_id:
            sql += " AND c.course_id = %s"
            params.append(selected_course_id)
            cursor.execute("SELECT batch_id, batch_name FROM batches WHERE course_id = %s AND is_active = TRUE", (selected_course_id,))
            batches = cursor.fetchall()

        if selected_batch_id:
            sql += " AND b.batch_id = %s"
            params.append(selected_batch_id)
            # Get batch details for the page title and pre-filling the "Add Student" form
            cursor.execute("SELECT batch_name, course_id FROM batches WHERE batch_id = %s", (selected_batch_id,))
            batch_result = cursor.fetchone()
            if batch_result:
                batch_name = batch_result['batch_name']
                # Ensure the course_id is set for the context, even if not filtered
                selected_course_id = batch_result['course_id']
        
        sql += " ORDER BY u.full_name"
        cursor.execute(sql, tuple(params))
        students = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f'Error retrieving students: {err}', 'danger')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
    return render_template('admin/student_management.html', 
                           students=students, 
                           courses=courses, 
                           batches=batches,
                           batch_name=batch_name,
                           # Pass context to the template for the Add Student modal
                           selected_course_id=selected_course_id,
                           selected_batch_id=selected_batch_id,
                           # Pass filter selections back to the filter modal
                           selected_course=selected_course_id,
                           selected_batch=selected_batch_id)
# ___________________________
# ________________




@admin_bp.route('/create_student', methods=['POST'])
def create_student():
    data = request.get_json()
    full_name, email, phone, course_id, batch_id = data.get('full_name'), data.get('email'), data.get('phone'), data.get('course_id'), data.get('batch_id')
    
    # --- NEW: Get gender from the data ---
    gender = data.get('gender') 

    errors = {}
    if not full_name: errors['full_name'] = 'Full name is required.'
    if not email or not validate_email(email): errors['email'] = 'A valid email is required.'
    if not phone or not validate_phone(phone): errors['phone'] = 'A valid phone number is required.'
    if not course_id: errors['course_id'] = 'Course is required.'
    if not batch_id: errors['batch_id'] = 'Batch is required.'
    # --- NEW: Add validation for gender if it's mandatory ---
    if not gender: errors['gender'] = 'Gender is required.' # Assuming gender is now required
    
    if errors:
        return jsonify({'success': False, 'errors': errors})

    conn = current_app.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'success': False, 'errors': {'email': 'This email address is already in use.'}})

        last_name = full_name.split()[-1]
        raw_password = generate_password(last_name, phone)
        hashed_password = hash_password(raw_password)
        
        # --- MODIFIED INSERT STATEMENT: Added gender ---
        cursor.execute("INSERT INTO users (email, password_hash, full_name, phone, role, created_by, gender) VALUES (%s, %s, %s, %s, 'student', %s, %s)",
                       (email, hashed_password, full_name, phone, current_user.user_id, gender)) # Pass gender
        user_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO students (user_id, course_id) VALUES (%s, %s)", (user_id, course_id))
        student_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO batch_students (batch_id, student_id) VALUES (%s, %s)", (batch_id, student_id))
        
        send_credentials_email(email, full_name, email, raw_password)
        conn.commit()
        log_activity(current_user.user_id, 'create', 'students', student_id, f"Created student: {full_name}")
        return jsonify({'success': True, 'message': 'Student created successfully!'})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@admin_bp.route('/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    data = request.get_json()
    full_name, email, phone, course_id, batch_id, is_active, user_id = data.get('full_name'), data.get('email'), data.get('phone'), data.get('course_id'), data.get('batch_id'), data.get('is_active'), data.get('user_id')

    errors = {} # Add validation as needed
    if errors: return jsonify({'success': False, 'errors': errors})

    conn = current_app.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET full_name=%s, email=%s, phone=%s, is_active=%s WHERE user_id=%s",
                       (full_name, email, phone, is_active, user_id))
        
        cursor.execute("UPDATE students SET course_id=%s WHERE student_id=%s", (course_id, student_id))
        
        # Update batch assignment: deactivate old, insert/update new
        cursor.execute("UPDATE batch_students SET is_active=FALSE WHERE student_id=%s", (student_id,))
        if batch_id:
            cursor.execute("INSERT INTO batch_students (batch_id, student_id, is_active) VALUES (%s, %s, TRUE) ON DUPLICATE KEY UPDATE is_active=TRUE",
                           (batch_id, student_id))
        
        conn.commit()
        log_activity(current_user.user_id, 'update', 'students', student_id, f"Updated student: {full_name}")
        return jsonify({'success': True, 'message': 'Student updated successfully!'})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@admin_bp.route('/delete_student/<int:user_id>', methods=['POST'])
def delete_student(user_id):
    # Note: Deleting a user will cascade and delete their student record due to DB constraints
    conn = current_app.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT full_name FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
             return jsonify({'success': False, 'message': 'User not found.'})
        
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        log_activity(current_user.user_id, 'delete', 'users', user_id, f"Deleted student: {user['full_name']}")
        return jsonify({'success': True, 'message': 'Student deleted successfully.'})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Cannot delete student. They may have dependent records (submissions, etc). Error: {err}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- ATTENDANCE & LEAVE MANAGEMENT (Largely unchanged but reviewed for compatibility) ---
@admin_bp.route('/attendance')
def attendance_management():
    conn = current_app.get_db_connection()
    courses, batches, attendance_data = [], [], []
    selected_course = request.args.get('course_id')
    selected_batch = request.args.get('batch_id')
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT c.course_id, c.course_name FROM courses c JOIN course_admins ca ON c.course_id = ca.course_id WHERE ca.admin_id = %s AND c.is_active = TRUE", (current_user.user_id,))
            courses = cursor.fetchall()
            
            if selected_course:
                 cursor.execute("SELECT batch_id, batch_name FROM batches WHERE course_id = %s AND is_active = TRUE", (selected_course,))
                 batches = cursor.fetchall()

            if selected_batch and selected_date:
                cursor.execute("""
                    SELECT 
                        s.student_id, u.full_name, u.email, a.is_present,
                        CASE WHEN a.attendance_id IS NOT NULL THEN TRUE ELSE FALSE END as marked
                    FROM students s
                    JOIN users u ON s.user_id = u.user_id
                    JOIN batch_students bs ON s.student_id = bs.student_id
                    LEFT JOIN attendance a ON s.student_id = a.student_id AND a.attendance_date = %s
                    WHERE bs.batch_id = %s AND bs.is_active = TRUE
                    ORDER BY u.full_name
                """, (selected_date, selected_batch))
                attendance_data = cursor.fetchall()
        except mysql.connector.Error as err:
            flash(f'Error retrieving data: {err}', 'danger')
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    
    return render_template('admin/attendance.html', courses=courses, batches=batches, attendance_data=attendance_data,
                           selected_course=selected_course, selected_batch=selected_batch, selected_date=selected_date)
# _________________________

@admin_bp.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    batch_id = data.get('batch_id')
    attendance_date = data.get('attendance_date')
    present_ids = data.get('present_ids', [])
    absent_ids = data.get('absent_ids', [])

    if not all([batch_id, attendance_date]):
        return jsonify({'success': False, 'message': 'Batch and date are required.'})
    
    conn = current_app.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT course_id FROM batches WHERE batch_id = %s", (batch_id,))
        course_id = cursor.fetchone()['course_id']
        
        # Use INSERT ... ON DUPLICATE KEY UPDATE for efficiency
        attendance_records = []
        for student_id in present_ids:
            attendance_records.append((student_id, course_id, batch_id, attendance_date, True, current_user.user_id))
        for student_id in absent_ids:
            attendance_records.append((student_id, course_id, batch_id, attendance_date, False, current_user.user_id))
            
        if attendance_records:
            query = """
                INSERT INTO attendance (student_id, course_id, batch_id, attendance_date, is_present, marked_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE is_present = VALUES(is_present), marked_by = VALUES(marked_by)
            """
            cursor.executemany(query, attendance_records)
            conn.commit()
            log_activity(current_user.user_id, 'update', 'attendance', batch_id, f"Marked attendance for batch {batch_id} on {attendance_date}")
            return jsonify({'success': True, 'message': 'Attendance saved successfully!'})
        return jsonify({'success': True, 'message': 'No changes to save.'})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if conn.is_connected(): cursor.close(); conn.close()





@admin_bp.route('/export_attendance/<int:batch_id>')
def export_attendance(batch_id):
    conn = current_app.get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin.attendance_management'))

    try:
        cursor = conn.cursor(dictionary=True)
        
        # BUG FIX: Added JOIN to the 'courses' table aliased as 'c'
        cursor.execute("""
            SELECT b.batch_name, c.course_name 
            FROM batches b
            JOIN courses c ON b.course_id = c.course_id
            JOIN course_admins ca ON b.course_id = ca.course_id
            WHERE ca.admin_id = %s AND b.batch_id = %s
        """, (current_user.user_id, batch_id))
        batch_details = cursor.fetchone()

        if not batch_details:
            flash('Access denied to this batch.', 'danger')
            return redirect(url_for('admin.attendance_management'))
        
        cursor.execute("SELECT DISTINCT attendance_date FROM attendance WHERE batch_id = %s ORDER BY attendance_date", (batch_id,))
        dates = [row['attendance_date'] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT s.student_id, u.full_name, u.email FROM students s
            JOIN users u ON s.user_id = u.user_id
            JOIN batch_students bs ON s.student_id = bs.student_id
            WHERE bs.batch_id = %s AND bs.is_active = TRUE ORDER BY u.full_name
        """, (batch_id,))
        students = cursor.fetchall()
        
        cursor.execute("SELECT student_id, attendance_date, is_present FROM attendance WHERE batch_id = %s", (batch_id,))
        attendance_records = cursor.fetchall()
        
        attendance_map = {(rec['student_id'], rec['attendance_date']): ('P' if rec['is_present'] else 'A') for rec in attendance_records}

        output = io.StringIO()
        writer = csv.writer(output)
        
        header = ['Student Name', 'Email', 'Total Present', 'Total Absent'] + [d.strftime('%Y-%m-%d') for d in dates]
        writer.writerow(header)

        for student in students:
            total_present = 0
            attendance_statuses = []
            for date in dates:
                status = attendance_map.get((student['student_id'], date), '-')
                if status == 'P':
                    total_present += 1
                attendance_statuses.append(status)
            
            total_absent = len([s for s in attendance_statuses if s == 'A'])
            
            row = [student['full_name'], student['email'], total_present, total_absent]
            row.extend(attendance_statuses)
            writer.writerow(row)

        response = current_app.response_class(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=attendance_{batch_details["batch_name"]}.csv'}
        )
        log_activity(current_user.user_id, 'export', 'attendance', batch_id, f"Exported attendance for {batch_details['batch_name']}")
        return response

    except mysql.connector.Error as err:
        flash(f'Error exporting attendance: {err}', 'danger')
        return redirect(url_for('admin.attendance_management'))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
        # ________________


# ===============================================================
# MODIFICATION 3: Update Leave Management View
# ===============================================================
@admin_bp.route('/leave_management')
def leave_management():
    conn = current_app.get_db_connection()
    leave_applications = []
    leave_types = []
    student_data = None # For the application form part
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # --- MODIFIED QUERY to get leave type and batch name ---
            cursor.execute("""   
                SELECT 
                    la.*, 
                    u.full_name as student_name, 
                    b.batch_name, 
                    lt.type_name,
                    (SELECT COUNT(*) FROM leave_applications la2 WHERE la2.student_id = la.student_id AND la2.status = 'approved') as approved_leaves
                FROM leave_applications la
                JOIN students s ON la.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                JOIN course_admins ca ON s.course_id = ca.course_id
                LEFT JOIN leave_types lt ON la.leave_type_id = lt.leave_type_id
                LEFT JOIN batches b ON la.batch_id = b.batch_id
                WHERE ca.admin_id = %s
                ORDER BY la.applied_at DESC
            """, (current_user.user_id,))
            leave_applications = cursor.fetchall()

            # Fetch leave types for the form dropdown
            cursor.execute("SELECT leave_type_id, type_name FROM leave_types ORDER BY type_name")
            leave_types = cursor.fetchall()
            
            # Fetch student's own batch for the form (if an admin is also a student in a weird case, or for future use)
            # This part is more relevant for the student's view but good to have the logic ready
            cursor.execute("""
                SELECT s.student_id, b.batch_id, b.batch_name, s.course_id
                FROM students s
                JOIN batch_students bs ON s.student_id = bs.student_id AND bs.is_active = TRUE
                JOIN batches b ON bs.batch_id = b.batch_id
                WHERE s.user_id = %s
            """, (current_user.user_id,))
            student_data = cursor.fetchone()

        except mysql.connector.Error as err:
            flash(f'Error retrieving leaves: {err}', 'danger')
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
            
    return render_template('admin/leave_management.html', 
                           leave_applications=leave_applications, 
                           leave_types=leave_types, 
                           student_data=student_data, 
                           now=datetime.now())


        
@admin_bp.route('/get_batches/<int:course_id>')
def get_batches(course_id):
    conn = current_app.get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT batch_id, batch_name FROM batches WHERE course_id = %s AND is_active = TRUE ORDER BY batch_name", (course_id,))
            batches = cursor.fetchall()
            return jsonify({'success': True, 'batches': batches})
        except mysql.connector.Error as err:
            return jsonify({'success': False, 'message': str(err)})
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    return jsonify({'success': False, 'message': 'Database connection error.'})







# ===============================================================
# MODIFICATION 4: Update Leave Status Logic (for email notifications)
# ===============================================================
@admin_bp.route('/update_leave_status/<int:leave_id>', methods=['POST'])
def update_leave_status(leave_id):
    data = request.get_json()
    status = data.get('status')
    comments = data.get('comments', '')

    if status not in ['approved', 'rejected']:
        return jsonify({'success': False, 'message': 'Invalid status.'})
    if status == 'rejected' and not comments.strip():
        return jsonify({'success': False, 'errors': {'comments': 'Rejection reason is required.'}})

    conn = current_app.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # Fetch leave details for email notification
        cursor.execute("""
            SELECT la.*, u.full_name as student_name, u.email as student_email
            FROM leave_applications la
            JOIN students s ON la.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            JOIN course_admins ca ON s.course_id = ca.course_id
            WHERE ca.admin_id = %s AND la.leave_id = %s
        """, (current_user.user_id, leave_id))
        leave_data = cursor.fetchone()
        
        if not leave_data:
            return jsonify({'success': False, 'message': 'Access denied or leave application not found.'})

        cursor.execute("UPDATE leave_applications SET status=%s, reviewed_by=%s, reviewed_at=NOW(), admin_comments=%s WHERE leave_id=%s",
                       (status, current_user.user_id, comments, leave_id))
        conn.commit()
        
        # Send notification email to the student
        send_leave_status_email(
            recipient=leave_data['student_email'],
            name=leave_data['student_name'],
            leave_details=leave_data,
            status=status
        )
        
        log_activity(current_user.user_id, 'update', 'leave_applications', leave_id, f"Set leave status to {status}")
        return jsonify({'success': True, 'message': f'Leave application has been {status}.'})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()


@admin_bp.route('/toggle_student_status/<int:user_id>', methods=['POST'])
@login_required
def toggle_student_status(user_id):
    """Toggles the active status of a student user."""
    data = request.get_json()
    new_status = data.get('is_active')

    if new_status is None:
        return jsonify({'success': False, 'message': 'Missing status information.'}), 400

    conn = current_app.get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error.'}), 500

    try:
        cursor = conn.cursor()
        # Ensure the user being modified is indeed a student to prevent misuse
        cursor.execute("UPDATE users SET is_active = %s WHERE user_id = %s AND role = 'student'", (new_status, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Student not found or user is not a student.'}), 404
            
        conn.commit()
        
        # Log this important activity
        action_description = "Activated" if new_status else "Deactivated"
        log_activity(current_user.user_id, 'update_status', 'users', user_id, f"{action_description} student account (ID: {user_id})")
        
        return jsonify({'success': True, 'message': f'Student status has been successfully updated to {"Active" if new_status else "Inactive"}.'})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {err}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@admin_bp.route('/get_student_details/<int:student_id>')
@login_required
def get_student_details(student_id):
    """
    Fetches a comprehensive set of details for a single student via AJAX.
    Accessible only by admins who are assigned to the student's course.
    """
    conn = current_app.get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error.'})

    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Security Check and Primary Student/Course/Batch Info
        # This query ensures the admin has access to this student's course.
        cursor.execute("""
            SELECT 
                s.student_id, u.full_name, u.email, u.phone, u.is_active, u.gender,
                c.course_name, b.batch_name
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            JOIN courses c ON s.course_id = c.course_id
            JOIN course_admins ca ON c.course_id = ca.course_id
            LEFT JOIN batch_students bs ON s.student_id = bs.student_id AND bs.is_active = TRUE
            LEFT JOIN batches b ON bs.batch_id = b.batch_id
            WHERE ca.admin_id = %s AND s.student_id = %s
        """, (current_user.user_id, student_id))
        student_details = cursor.fetchone()

        if not student_details:
            return jsonify({'success': False, 'message': 'Access denied or student not found.'})

        # 2. Get recent attendance records (last 60 days for performance)
        cursor.execute("""
            SELECT attendance_date, is_present 
            FROM attendance 
            WHERE student_id = %s 
            ORDER BY attendance_date DESC 
            LIMIT 60
        """, (student_id,))
        attendance_history = cursor.fetchall()
        # Convert date objects to strings for JSON
        for record in attendance_history:
            record['attendance_date'] = record['attendance_date'].strftime('%Y-%m-%d')

        # 3. Get all leave history
        cursor.execute("""
            SELECT la.start_date, la.end_date, la.reason, la.status, la.days_requested, lt.type_name
            FROM leave_applications la
            LEFT JOIN leave_types lt ON la.leave_type_id = lt.leave_type_id
            WHERE la.student_id = %s 
            ORDER BY la.start_date DESC
        """, (student_id,))
        leave_history = cursor.fetchall()
        # Convert date objects to strings for JSON
        for leave in leave_history:
            leave['start_date'] = leave['start_date'].strftime('%Y-%m-%d')
            leave['end_date'] = leave['end_date'].strftime('%Y-%m-%d')

        return jsonify({
            'success': True, 
            'details': student_details,
            'attendance': attendance_history,
            'leaves': leave_history
        })

    except mysql.connector.Error as err:
        print(f"Error getting student details: {err}")
        return jsonify({'success': False, 'message': f'A database error occurred: {err}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()