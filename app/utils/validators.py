# import re
# from datetime import datetime,timedelta

# def validate_email(email):
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None

# def validate_phone(phone):
#     # Remove any non-digit characters
#     digits = re.sub(r'\D', '', phone)
#     # Check if it has between 10-15 digits (international numbers)
#     return 10 <= len(digits) <= 15

# def validate_password(password):
#     # At least 8 characters, one uppercase, one lowercase, one number
#     if len(password) < 8:
#         return False, "Password must be at least 8 characters long"
    
#     if not re.search(r'[A-Z]', password):
#         return False, "Password must contain at least one uppercase letter"
    
#     if not re.search(r'[a-z]', password):
#         return False, "Password must contain at least one lowercase letter"
    
#     if not re.search(r'[0-9]', password):
#         return False, "Password must contain at least one number"
    
#     return True, "Password is valid"

# def validate_date_range(start_date, end_date):
#     try:
#         start = datetime.strptime(start_date, '%Y-%m-%d')
#         end = datetime.strptime(end_date, '%Y-%m-%d')
#         return start <= end
#     except (ValueError, TypeError):
#         return False

# def validate_course_dates(start_date, end_date, duration_weeks):
#     try:
#         start = datetime.strptime(start_date, '%Y-%m-%d')
#         end = datetime.strptime(end_date, '%Y-%m-%d')
        
#         # Calculate expected end date based on duration
#         expected_end = start + timedelta(weeks=duration_weeks)
        
#         # Allow some flexibility (±2 weeks)
#         min_end = expected_end - timedelta(weeks=2)
#         max_end = expected_end + timedelta(weeks=2)
        
#         return min_end <= end <= max_end
#     except (ValueError, TypeError):
#         return False

# def validate_csv_headers(headers, expected_headers):
#     return set(headers) == set(expected_headers)

# def validate_leave_dates(start_date, end_date, max_leaves, existing_leaves):
#     try:
#         start = datetime.strptime(start_date, '%Y-%m-%d')
#         end = datetime.strptime(end_date, '%Y-%m-%d')
        
#         # Check if end date is after start date
#         if end < start:
#             return False, "End date must be after start date"
        
#         # Check if dates are in the future
#         today = datetime.now().date()
#         if start.date() < today:
#             return False, "Leave cannot be applied for past dates"
        
#         # Calculate number of leave days (excluding weekends)
#         leave_days = 0
#         current = start
#         while current <= end:
#             if current.weekday() < 5:  # Monday to Friday
#                 leave_days += 1
#             current += timedelta(days=1)
        
#         # Check if exceeds max leaves
#         total_used_leaves = sum(existing_leaves)
#         if total_used_leaves + leave_days > max_leaves:
#             return False, f"Exceeds maximum allowed leaves. You have {max_leaves - total_used_leaves} leaves remaining."
        
#         return True, f"{leave_days} leave days requested"
#     except (ValueError, TypeError):
#         return False, "Invalid date format"




# __________________________________________-

# Imports necessary modules
# import re                      # For regular expressions (pattern matching).
# from datetime import datetime, timedelta # For date and time operations.

# # --- Basic Validations ---

# def validate_email(email):
#     """
#     Validates if the provided string is a valid email address format.
#     """
#     # Regex pattern for common email structures.
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     # re.match checks if the pattern matches from the beginning of the string.
#     return re.match(pattern, email) is not None

# def validate_phone(phone):
#     """
#     Validates a phone number format, checking for 10-15 digits after removing non-digit characters.
#     """
#     # Removes all non-digit characters from the phone number string.
#     digits = re.sub(r'\D', '', phone)
#     # Checks if the resulting digits string has a length between 10 and 15.
#     return 10 <= len(digits) <= 15

# def validate_password(password):
#     """
#     Validates a password against common security criteria:
#     - Minimum 8 characters
#     - At least one uppercase letter
#     - At least one lowercase letter
#     - At least one number
#     """
#     if len(password) < 8:
#         return False, "Password must be at least 8 characters long"
    
#     if not re.search(r'[A-Z]', password):
#         return False, "Password must contain at least one uppercase letter"
    
#     if not re.search(r'[a-z]', password):
#         return False, "Password must contain at least one lowercase letter"
    
#     if not re.search(r'[0-9]', password):
#         return False, "Password must contain at least one number"
    
#     return True, "Password is valid" # All criteria met.

# # --- Date Validations ---

# def validate_date_range(start_date_str, end_date_str):
#     """
#     Validates if the end_date is on or after the start_date.
#     Expects dates in 'YYYY-MM-DD' format.
#     """
#     try:
#         # Parses date strings into datetime objects.
#         start = datetime.strptime(start_date_str, '%Y-%m-%d')
#         end = datetime.strptime(end_date_str, '%Y-%m-%d')
#         # Returns True if end date is chronologically after or the same as start date.
#         return start <= end
#     except (ValueError, TypeError):
#         # Returns False if dates are invalid or in the wrong format.
#         return False

# def validate_course_dates(start_date_str, end_date_str, duration_weeks):
#     """
#     Validates if the end_date is consistent with the start_date and duration_weeks,
#     allowing for a ±2 week tolerance.
#     """
#     try:
#         start = datetime.strptime(start_date_str, '%Y-%m-%d')
#         end = datetime.strptime(end_date_str, '%Y-%m-%d')
        
#         # Calculate the expected end date based on start date and duration.
#         expected_end = start + timedelta(weeks=duration_weeks)
        
#         # Define a tolerance window (±2 weeks) for the end date.
#         min_end = expected_end - timedelta(weeks=2)
#         max_end = expected_end + timedelta(weeks=2)
        
#         # Check if the provided end date falls within the calculated window.
#         return min_end <= end <= max_end
#     except (ValueError, TypeError):
#         # Return False if date parsing or calculation fails.
#         return False

# # --- CSV and Data Validation ---

# def validate_csv_headers(headers, expected_headers):
#     """
#     Validates if the provided list of CSV headers exactly matches the expected headers,
#     ignoring the order.
#     """
#     # Converts both lists to sets for order-independent comparison.
#     return set(headers) == set(expected_headers)

# # --- Leave Date and Limit Validation ---
# def validate_leave_dates(start_date_str, end_date_str, leave_type_id, student_id, batch_id):
#     """
#     Validates leave application dates and checks against leave limits based on type.
    
#     Args:
#         start_date_str (str): The requested start date ('YYYY-MM-DD').
#         end_date_str (str): The requested end date ('YYYY-MM-DD').
#         leave_type_id (int): The ID of the leave type being applied for.
#         student_id (int): The ID of the student applying for leave.
#         batch_id (int): The ID of the batch the leave is associated with.
        
#     Returns:
#         tuple: (bool, str) indicating validation success and a message.
#     """
#     conn = current_app.get_db_connection()
#     if not conn: return False, "Database connection error"
    
#     try:
#         start = datetime.strptime(start_date_str, '%Y-%m-%d')
#         end = datetime.strptime(end_date_str, '%Y-%m-%d')
        
#         # Check if end date is after start date.
#         if end < start:
#             return False, "End date must be after start date"
        
#         # Check if dates are in the future.
#         today = datetime.now().date() # Get today's date.
#         if start.date() < today:
#             return False, "Leave cannot be applied for past dates"
        
#         # Calculate number of requested leave days (excluding weekends).
#         leave_days = 0
#         current = start
#         while current <= end:
#             if current.weekday() < 5:  # Monday is 0, Friday is 4.
#                 leave_days += 1
#             current += timedelta(days=1)
        
#         # Fetch leave type details to check for limits.
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT type_name, has_limit, default_limit_days FROM leave_types WHERE leave_type_id = %s", (leave_type_id,))
#         leave_type = cursor.fetchone()
        
#         if not leave_type:
#             return False, "Invalid leave type selected"

#         allowed_days = 0
#         if leave_type['has_limit']:
#             # Check for student-specific allowance first
#             cursor.execute("""
#                 SELECT allowed_days FROM student_leave_allowances
#                 WHERE student_id = %s AND batch_id = %s AND leave_type_id = %s
#             """, (student_id, batch_id, leave_type_id))
#             allowance = cursor.fetchone()
            
#             if allowance:
#                 max_days = allowance['allowed_days']
#             else:
#                 # If no specific allowance, use the default limit (or 0 if default is NULL/not applicable)
#                 max_days = leave_type['default_limit_days'] if leave_type['default_limit_days'] is not None else 0
#         else:
#             max_days = float('inf') # Represent unlimited leave days.

#         # Calculate used days for this leave type and batch.
#         cursor.execute("""
#             SELECT SUM(days_requested) as used_days
#             FROM leave_applications
#             WHERE student_id = %s AND batch_id = %s AND leave_type_id = %s AND status = 'approved'
#         """, (student_id, batch_id, leave_type_id))
#         used_data = cursor.fetchone()
#         used_days = used_data['used_days'] if used_data and used_data['used_days'] else 0

#         # Check if the requested days exceed the allowed limit.
#         if max_days != float('inf') and (used_days + leave_days > max_days):
#             remaining = max(0, max_days - used_days)
#             return False, f"Exceeds maximum allowed leaves ({max_days} days). You have {remaining} leaves remaining."
        
#         # If validation passes
#         return True, f"{leave_days} days requested for {leave_type['type_name']} leave"
        
#     except (ValueError, TypeError) as e:
#         print(f"Date validation error: {e}")
#         return False, "Invalid date format or error calculating leave days"
#     finally:
#         # Ensure connection is closed
#         if conn and conn.is_connected():
#             cursor.close()
#             conn.close()
    
#     return False, "Unknown validation error" # Fallback if no specific error matched.

# ____________________________________________________________________________

import re
from datetime import datetime, timedelta
from flask import current_app
import mysql.connector

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    digits = re.sub(r'\D', '', phone)
    return 10 <= len(digits) <= 15

def validate_password(password):
    if len(password) < 8: return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password): return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password): return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password): return False, "Password must contain at least one number"
    return True, "Password is valid"

def validate_date_range(start_date_str, end_date_str):
    try:
        start = datetime.strptime(start_date_str, '%Y-%m-%d')
        end = datetime.strptime(end_date_str, '%Y-%m-%d')
        return start <= end
    except (ValueError, TypeError):
        return False

def validate_course_dates(start_date_str, end_date_str, duration_weeks):
    try:
        start = datetime.strptime(start_date_str, '%Y-%m-%d')
        end = datetime.strptime(end_date_str, '%Y-%m-%d')
        expected_end = start + timedelta(weeks=duration_weeks)
        min_end = expected_end - timedelta(weeks=2)
        max_end = expected_end + timedelta(weeks=2)
        return min_end <= end <= max_end
    except (ValueError, TypeError):
        return False

def validate_csv_headers(headers, expected_headers):
    return set(headers) == set(expected_headers)

# --- MODIFIED LEAVE VALIDATION ---
def validate_leave_dates(start_date_str, end_date_str, leave_type_id, student_id, batch_id):
    """
    Validates leave application dates and checks against leave limits based on type and batch.
    
    Args:
        start_date_str (str): The requested start date ('YYYY-MM-DD').
        end_date_str (str): The requested end date ('YYYY-MM-DD').
        leave_type_id (int): The ID of the leave type being applied for.
        student_id (int): The ID of the student applying for leave.
        batch_id (int): The ID of the batch the leave is associated with.
        
    Returns:
        tuple: (bool, str) indicating validation success and a message.
    """
    conn = current_app.get_db_connection()
    if not conn: return False, "Database connection error"
    
    try:
        start = datetime.strptime(start_date_str, '%Y-%m-%d')
        end = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Basic date validation: end date must be after start date
        if end < start:
            return False, "End date must be after start date"
        
        # Check if dates are in the future
        today = datetime.now().date()
        if start.date() < today:
            return False, "Leave cannot be applied for past dates"
        
        # Calculate number of requested leave days (excluding weekends)
        leave_days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:  # Monday to Friday (0-4)
                leave_days += 1
            current += timedelta(days=1)
        
        # Fetch leave type details to check for limits
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT type_name, has_limit, default_limit_days FROM leave_types WHERE leave_type_id = %s", (leave_type_id,))
        leave_type = cursor.fetchone()
        
        if not leave_type:
            return False, "Invalid leave type selected"

        max_days = 0
        if leave_type['has_limit']:
            # Check for student-specific allowance first
            cursor.execute("""
                SELECT allowed_days FROM student_leave_allowances
                WHERE student_id = %s AND batch_id = %s AND leave_type_id = %s
            """, (student_id, batch_id, leave_type_id))
            allowance = cursor.fetchone()
            
            if allowance:
                max_days = allowance['allowed_days']
            else:
                # If no specific allowance, use the default limit (or 0 if default is NULL)
                max_days = leave_type['default_limit_days'] if leave_type['default_limit_days'] is not None else 0
        else:
            max_days = float('inf') # Represent unlimited leave days.

        # Calculate used days for this leave type and batch
        cursor.execute("""
            SELECT SUM(days_requested) as used_days
            FROM leave_applications
            WHERE student_id = %s AND batch_id = %s AND leave_type_id = %s AND status = 'approved'
        """, (student_id, batch_id, leave_type_id))
        used_data = cursor.fetchone()
        used_days = used_data['used_days'] if used_data and used_data['used_days'] else 0

        # Check if the requested days exceed the allowed limit
        if max_days != float('inf') and (used_days + leave_days > max_days):
            remaining = max(0, max_days - used_days) # Ensure remaining is not negative
            return False, f"Exceeds maximum allowed leaves ({max_days} days). You have {remaining} leaves remaining."
        
        # If all validations pass
        return True, f"{leave_days} days requested for {leave_type['type_name']} leave"
        
    except (ValueError, TypeError) as e:
        print(f"Date validation error: {e}")
        return False, "Invalid date format or error calculating leave days"
    finally:
        # Ensure connection is closed
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    
    return False, "Unknown validation error" # Fallback