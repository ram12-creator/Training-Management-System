
from flask_login import UserMixin
import mysql.connector
from flask import current_app
import bcrypt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
# ... (other imports) ...

# Import login_manager from your app's main file (e.g., app/__init__.py)
from app import login_manager

class User(UserMixin):
    def __init__(self, user_id, email, password_hash, full_name, phone, role, is_active, 
                 created_by=None, first_name=None, last_name=None, qualifications=None, profile_picture=None,gender = None,
                 # Student-specific attributes (fetched when user.role == 'student' or when context requires it)
                 student_id=None, course_id=None, enrollment_date=None, course_name=None,
                 batch_id=None, batch_name=None): # Added batch_id and batch_name
        
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.phone = phone
        self.role = role
        self._is_active = is_active
        self.created_by = created_by
        self.first_name = first_name
        self.last_name = last_name
        self.qualifications = qualifications
        self.profile_picture = profile_picture
        self.gender = gender
        
        # Student-specific attributes
        self.student_id = student_id
        self.course_id = course_id
        self.enrollment_date = enrollment_date
        self.course_name = course_name
        self.batch_id = batch_id # Store batch_id
        self.batch_name = batch_name # Store batch_name

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    def get_id(self):
        return str(self.user_id)
    
    @staticmethod
    def get(user_id):
        conn = current_app.get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # Query to fetch user details, joining student, batch, and course info if available
            cursor.execute("""
                SELECT u.*, s.student_id, s.course_id, s.enrollment_date, c.course_name, b.batch_name, b.batch_id,u.gender
                FROM users u 
                LEFT JOIN students s ON u.user_id = s.user_id 
                -- Correct join path: students -> batch_students -> batches
                LEFT JOIN batch_students bs ON s.student_id = bs.student_id AND bs.is_active = TRUE 
                LEFT JOIN batches b ON bs.batch_id = b.batch_id 
                LEFT JOIN courses c ON s.course_id = c.course_id 
                WHERE u.user_id = %s
            """, (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data:
                return User(
                    user_id=user_data['user_id'], email=user_data['email'],
                    password_hash=user_data['password_hash'], full_name=user_data['full_name'],
                    phone=user_data['phone'], role=user_data['role'], is_active=user_data['is_active'],
                    created_by=user_data.get('created_by'), first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'), qualifications=user_data.get('qualifications'),
                    profile_picture=user_data.get('profile_picture'),
                    gender=user_data.get('gender'),
                    # Student specific data
                    student_id=user_data.get('student_id'), course_id=user_data.get('course_id'),
                    enrollment_date=user_data.get('enrollment_date'), course_name=user_data.get('course_name'),
                    batch_id=user_data.get('batch_id'), batch_name=user_data.get('batch_name')
                )
        return None
    
    @staticmethod
    def get_by_email(email):
        conn = current_app.get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # Fetch user by email, also joining student/batch/course info if available
            cursor.execute("""
                SELECT u.*, s.student_id, s.course_id, s.enrollment_date, c.course_name, b.batch_name, b.batch_id,u.gender
                FROM users u 
                LEFT JOIN students s ON u.user_id = s.user_id 
                LEFT JOIN batch_students bs ON s.student_id = bs.student_id AND bs.is_active = TRUE
                LEFT JOIN batches b ON bs.batch_id = b.batch_id 
                LEFT JOIN courses c ON s.course_id = c.course_id 
                WHERE u.email = %s
            """, (email,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data:
                return User(
                    user_id=user_data['user_id'], email=user_data['email'],
                    password_hash=user_data['password_hash'], full_name=user_data['full_name'],
                    phone=user_data['phone'], role=user_data['role'], is_active=user_data['is_active'],
                    created_by=user_data.get('created_by'), first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'), qualifications=user_data.get('qualifications'),
                    profile_picture=user_data.get('profile_picture'),
                    # Student specific data
                    student_id=user_data.get('student_id'), course_id=user_data.get('course_id'),
                    enrollment_date=user_data.get('enrollment_date'), course_name=user_data.get('course_name'),
                    batch_id=user_data.get('batch_id'), batch_name=user_data.get('batch_name')
                )
        return None
    
    @staticmethod
    def validate_login(email, password):
        user = User.get_by_email(email)
        if user and user.is_active and user.check_password(password):
            return user
        return None
    
    @staticmethod
    def create_user(email, password_hash, full_name, phone, role, created_by=None, 
                   first_name=None, last_name=None, qualifications=None, profile_picture=None,gender=None):
        conn = current_app.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (email, password_hash, full_name, phone, role, created_by, first_name, last_name, qualifications, profile_picture,gender) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                    (email, password_hash, full_name, phone, role, created_by, first_name, last_name, qualifications, profile_picture,gender)
                )
                user_id = cursor.lastrowid
                conn.commit()
                return user_id
            except mysql.connector.Error as err:
                print(f"Error creating user: {err}")
                conn.rollback()
                return None
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return None
    
    def check_password(self, password):
        if self.password_hash:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        return False
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def update_password(user_id, new_password_hash):
        conn = current_app.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (new_password_hash, user_id))
                conn.commit()
                return True
            except mysql.connector.Error as err:
                print(f"Error updating password: {err}")
                conn.rollback()
                return False
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return False

    # --- NEW METHODS FOR LEAVE MANAGEMENT ---

    def get_leave_balance(self, batch_id, leave_type_id):
        """
        Fetches the remaining leave days for a student for a specific leave type and batch.
        Returns a tuple: (remaining_days, max_days).
        remaining_days can be an integer or 'Unlimited'.
        max_days can be an integer or float('inf').
        """
        conn = current_app.get_db_connection()
        if not conn: 
            return 0, 0 # Return 0s if DB connection fails

        try:
            cursor = conn.cursor(dictionary=True)
            
            # 1. Get leave type details (name, limit status, default limit)
            cursor.execute("SELECT type_name, has_limit, default_limit_days FROM leave_types WHERE leave_type_id = %s", (leave_type_id,))
            leave_type = cursor.fetchone()
            
            if not leave_type:
                return 0, 0 # Invalid leave type

            type_name = leave_type['type_name']
            has_limit = leave_type['has_limit']
            default_limit = leave_type['default_limit_days']

            max_days = 0
            if has_limit:
                # Check for student-specific allowance first in student_leave_allowances
                cursor.execute("""
                    SELECT allowed_days FROM student_leave_allowances
                    WHERE student_id = %s AND batch_id = %s AND leave_type_id = %s
                """, (self.user_id, batch_id, leave_type_id)) # Use self.user_id as student_id
                
                allowance = cursor.fetchone()
                if allowance:
                    max_days = allowance['allowed_days'] # Use student-specific limit if found
                else:
                    # If no specific allowance, use the default limit or 0 if default is NULL
                    max_days = default_limit if default_limit is not None else 0
            else:
                max_days = float('inf') # Represent unlimited leave days.

            # 2. Calculate used days for this leave type and batch
            cursor.execute("""
                SELECT SUM(days_requested) as used_days
                FROM leave_applications
                WHERE student_id = %s AND batch_id = %s AND leave_type_id = %s AND status = 'approved'
            """, (self.user_id, batch_id, leave_type_id)) # Use self.user_id as student_id
            
            used_data = cursor.fetchone()
            used_days = used_data['used_days'] if used_data and used_data['used_days'] else 0

            # 3. Calculate remaining days
            remaining_days = 'Unlimited'
            if has_limit and max_days != float('inf'):
                remaining_days = max(0, max_days - used_days)
            elif has_limit and max_days == 0: # Handle case where limit is explicitly 0
                remaining_days = 0
            
            return remaining_days, max_days

        except mysql.connector.Error as err:
            print(f"Error getting leave balance for student {self.user_id}, batch {batch_id}, type {leave_type_id}: {err}")
            return 0, 0 # Error case
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
        
        return 0, 0 # Fallback if connection failed or other issues

    

    def get_all_leave_balances_for_batch(self, batch_id):
        """
        Fetches all leave balances (per type) for the student in a specific batch.
        """
        balances = {}
        conn = current_app.get_db_connection()
        if not (conn and self.student_id and batch_id): 
            return balances

        try:
            cursor = conn.cursor(dictionary=True)
            
            # Fetch all defined leave types
            cursor.execute("SELECT leave_type_id, type_name, has_limit, default_limit_days FROM leave_types ORDER BY type_name")
            leave_types = cursor.fetchall()
            
            # Fetch batch-specific leave limits
            cursor.execute("""
                SELECT personal_leave_limit, medical_leave_limit, academic_leave_limit, special_leave_limit 
                FROM batches WHERE batch_id = %s
            """, (batch_id,))
            batch_limits = cursor.fetchone()

            for leave_type in leave_types:
                type_name = leave_type['type_name']
                type_name_lower = type_name.lower()
                has_limit = leave_type['has_limit']
                
                max_days = float('inf')
                if has_limit:
                    # Use the batch-specific limit if it's set, otherwise use the leave_type default
                    batch_specific_limit = batch_limits.get(f'{type_name_lower}_leave_limit')
                    if batch_specific_limit is not None:
                        max_days = batch_specific_limit
                    else:
                        max_days = leave_type['default_limit_days'] or 0

                # CORRECTED: Use self.student_id to query the leave_applications table
                cursor.execute("""
                    SELECT COALESCE(SUM(days_requested), 0) as used_days
                    FROM leave_applications
                    WHERE student_id = %s AND batch_id = %s AND leave_type_id = %s AND status = 'approved'
                """, (self.student_id, batch_id, leave_type['leave_type_id']))
                
                used_days = cursor.fetchone()['used_days']

                remaining = 'Unlimited'
                if has_limit:
                    remaining = max(0, int(max_days) - int(used_days))
                
                balances[type_name] = {'remaining': remaining, 'total': max_days if has_limit else 'Unlimited'}
            
        except mysql.connector.Error as err:
            print(f"Error getting all leave balances for student {self.student_id}: {err}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
        
        return balances



# --- Flask-Login User Loader Callback ---
@login_manager.user_loader
def load_user(user_id):
    # Loads user from DB using user_id. This is called by Flask-Login to get the current_user object.
    return User.get(user_id)