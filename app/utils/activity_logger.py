# from app import db
# from datetime import datetime

# def log_activity(user_id, action, table_name, record_id, details=None):
#     """
#     Log user activity to the database
#     """
#     from app.models import ActivityLog  # Import here to avoid circular imports
    
#     activity = ActivityLog(
#         user_id=user_id,
#         action=action,
#         table_name=table_name,
#         record_id=record_id,
#         details=details,
#         timestamp=datetime.utcnow()
#     )
    
#     try:
#         db.session.add(activity)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         # You might want to log this error as well
#         print(f"Failed to log activity: {e}")