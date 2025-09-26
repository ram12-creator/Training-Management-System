# from flask import Flask
# from flask_login import LoginManager
# from flask_mail import Mail
# import mysql.connector
# from dotenv import load_dotenv
# import os

# # from flask_wtf.csrf import CSRFProtect
# # csrf = CSRFProtect()

# # Load environment variables
# load_dotenv()

# # Initialize extensions
# login_manager = LoginManager()
# mail = Mail()

# def create_app():
#     app = Flask(__name__)

#     # app.log_activity = log_activity
    
#     # Configuration
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
#     # Correctly parse environment variables to their data types
#     app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    
#     # Database configuration
#     app.config['DB_CONFIG'] = {
#         'host': os.getenv('DB_HOST'),
#         'database': os.getenv('DB_NAME'),
#         'user': os.getenv('DB_USER'),
#         'password': os.getenv('DB_PASSWORD')
#     }
    
#     # Email configuration
#     app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
#     app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
#     app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False').lower() in ['true', '1', 't']
#     app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
#     app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
#     app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
#     # Set Flask-Mail debug to match Flask's debug mode
#     app.config['MAIL_DEBUG'] = app.config['DEBUG']
    
#     # Initialize extensions
#     login_manager.init_app(app)
#     login_manager.login_view = 'auth.login'
#     login_manager.login_message_category = 'info'
    
#     mail.init_app(app)
    
#     # Register blueprints
#     from app.routes.auth import auth_bp
#     from app.routes.super_admin import super_admin_bp
#     from app.routes.admin import admin_bp
#     from app.routes.trainer import trainer_bp
#     from app.routes.student import student_bp
#     from app.main import main_bp  # Import the new main blueprint
#     from app.utils.template_filters import filters_bp
    
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
#     app.register_blueprint(admin_bp, url_prefix='/admin')
#     app.register_blueprint(trainer_bp, url_prefix='/trainer')
#     app.register_blueprint(student_bp, url_prefix='/student')
    
#     # Register the main blueprint for the root URL
#     app.register_blueprint(main_bp)

#     app.register_blueprint(filters_bp)


#     # In your app configuration (__init__.py or app.py)
#     app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'profile_pictures')
#     app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
#     app.config['MAX_FILE_SIZE'] = 2 * 1024 * 1024  # 2MB

# # Create the upload directory if it doesn't exist
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    
#     # Database connection function
#     def get_db_connection():
#         try:
#             conn = mysql.connector.connect(**app.config['DB_CONFIG'])
#             return conn
#         except mysql.connector.Error as err:
#             print(f"Error connecting to database: {err}")
#             return None
    
#     app.get_db_connection = get_db_connection
#     # csrf.init_app(app)
#     return app


# ____________________________________________________-

# from flask import Flask
# from flask_login import LoginManager
# import mysql.connector
# from dotenv import load_dotenv
# import os
# from celery import Celery

# # Load environment variables
# load_dotenv()

# # Initialize extensions WITHOUT app object initially
# login_manager = LoginManager()
# celery = Celery(__name__, broker=os.getenv('CELERY_BROKER_URL'), backend=os.getenv('CELERY_RESULT_BACKEND'))

# def create_app():
#     app = Flask(__name__)

#     # --- Configuration ---
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
#     app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
#     app.config['DB_CONFIG'] = {
#         'host': os.getenv('DB_HOST'),
#         'database': os.getenv('DB_NAME'),
#         'user': os.getenv('DB_USER'),
#         'password': os.getenv('DB_PASSWORD')
#     }
#     app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
#     # Update Celery configuration with Flask app config
#     celery.conf.update(
#         broker_url=os.getenv('CELERY_BROKER_URL'),
#         result_backend=os.getenv('CELERY_RESULT_BACKEND')
#     )
    
#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
#     celery.Task = ContextTask

#     # --- Initialize extensions with app ---
#     login_manager.init_app(app)
#     login_manager.login_view = 'auth.login'
#     login_manager.login_message_category = 'info'
    
#     # --- Database Connection ---
#     def get_db_connection():
#         try:
#             return mysql.connector.connect(**app.config['DB_CONFIG'])
#         except mysql.connector.Error as err:
#             print(f"Error connecting to database: {err}")
#             return None
#     app.get_db_connection = get_db_connection

#     # --- Register Blueprints (Import them here to avoid circular imports) ---
#     from app.routes.auth import auth_bp
#     from app.routes.super_admin import super_admin_bp
#     from app.routes.admin import admin_bp
#     from app.routes.trainer import trainer_bp
#     from app.routes.student import student_bp
#     from app.main import main_bp
    
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
#     app.register_blueprint(admin_bp, url_prefix='/admin')
#     app.register_blueprint(trainer_bp, url_prefix='/trainer')
#     app.register_blueprint(student_bp, url_prefix='/student')
#     app.register_blueprint(main_bp)

#     return app

# ___________________________________________________________-

# from flask import Flask
# from flask_login import LoginManager
# import mysql.connector
# from dotenv import load_dotenv
# import os
# from celery import Celery

# # Load environment variables from .env file
# load_dotenv()

# # ===============================================================
# # Initialize Extensions (Application Factory Pattern)
# # ===============================================================
# # We create the extension objects here, but we will configure and
# # connect them to the app inside the create_app function.

# login_manager = LoginManager()
# celery = Celery(__name__, 
#                 broker=os.getenv('CELERY_BROKER_URL'), 
#                 backend=os.getenv('CELERY_RESULT_BACKEND'))

# # --- NEW: Tell Celery where our tasks are defined ---
# # This is the crucial line that allows the worker to find your tasks.
# celery.conf.imports = ('app.tasks',)


# def create_app():
#     """
#     Create and configure an instance of the Flask application.
#     """
#     app = Flask(__name__)

#     # --- Configuration ---
#     # Load configuration from environment variables
#     app.config.from_mapping(
#         SECRET_KEY=os.getenv('SECRET_KEY'),
#         DEBUG=os.getenv('DEBUG', 'False').lower() in ['true', '1', 't'],
#         DB_CONFIG={
#             'host': os.getenv('DB_HOST'),
#             'database': os.getenv('DB_NAME'),
#             'user': os.getenv('DB_USER'),
#             'password': os.getenv('DB_PASSWORD')
#         },
#         # Define upload folders
#         UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
        
#         # Celery configuration, ensuring it matches the app's settings
#         CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL'),
#         CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND')
#     )
    
#     # Create upload directories if they don't exist
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments'), exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'submissions'), exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'test_cases'), exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    
#     # --- Update Celery with the Flask app's config and context ---
#     celery.conf.update(
#         broker_url=app.config['CELERY_BROKER_URL'],
#         result_backend=app.config['CELERY_RESULT_BACKEND']
#     )
    
#     # This custom Task class ensures that background tasks run with the Flask app's context
#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
#     celery.Task = ContextTask

#     # --- Initialize extensions with the app ---
#     login_manager.init_app(app)
#     login_manager.login_view = 'auth.login'
#     login_manager.login_message_category = 'info'
    
#     # --- Database Connection Helper ---
#     # Attach a helper function to the app object to get a DB connection
#     def get_db_connection():
#         try:
#             return mysql.connector.connect(**app.config['DB_CONFIG'])
#         except mysql.connector.Error as err:
#             print(f"Error connecting to database: {err}")
#             return None
#     app.get_db_connection = get_db_connection

#     # --- Register Blueprints (Import them INSIDE the function to avoid circular imports) ---
#     with app.app_context():
#         from app.routes.auth import auth_bp
#         from app.routes.super_admin import super_admin_bp
#         from app.routes.admin import admin_bp
#         from app.routes.trainer import trainer_bp
#         from app.routes.student import student_bp
#         from app.main import main_bp
#         from app.utils.template_filters import filters_bp
        
#         app.register_blueprint(auth_bp)
#         app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
#         app.register_blueprint(admin_bp, url_prefix='/admin')
#         app.register_blueprint(trainer_bp, url_prefix='/trainer')
#         app.register_blueprint(student_bp, url_prefix='/student')
#         app.register_blueprint(main_bp)
#         app.register_blueprint(filters_bp)

#     return app


# ____________________________________________________________-

# from flask import Flask
# from flask_login import LoginManager
# import mysql.connector
# from dotenv import load_dotenv
# import os
# from celery import Celery

# # Load environment variables from .env file
# load_dotenv()

# def make_celery(app):
#     """
#     This function configures Celery with the Flask app context.
#     It's a helper for our application factory.
#     """
#     # Create the Celery instance, pulling broker and backend URLs from the app's config
#     celery = Celery(
#         app.import_name,
#         backend=app.config['result_backend'], 
#         broker=app.config['broker_url']      
#     )
#     celery.conf.update(app.config)

#     # This special class ensures that every Celery task runs inside a Flask application context.
#     # This is what solves the "Working outside of application context" error.
#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)

#     celery.Task = ContextTask
#     return celery

# # Initialize extensions in the global scope, they will be configured inside create_app
# login_manager = LoginManager()

# # This is a placeholder that will be replaced by the fully configured instance
# # once the app is created. It helps prevent circular import issues.
# celery = None

# def create_app():
#     """
#     Create and configure an instance of the Flask application (the Application Factory).
#     """
#     app = Flask(__name__)

#     # --- Configuration ---
#     app.config.from_mapping(
#         SECRET_KEY=os.getenv('SECRET_KEY'),
#         DEBUG=os.getenv('DEBUG', 'False').lower() in ['true', '1', 't'],
#         DB_CONFIG={
#             'host': os.getenv('DB_HOST'),
#             'database': os.getenv('DB_NAME'),
#             'user': os.getenv('DB_USER'),
#             'password': os.getenv('DB_PASSWORD')
#         },
#         UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
        
#         # Celery configuration sourced from .env file
#         broker_url=os.getenv('CELERY_BROKER_URL'),
#         result_backend=os.getenv('CELERY_RESULT_BACKEND')
#     )
    
#     # Create necessary upload directories
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments'), exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'submissions'), exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'test_cases'), exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    
#     # --- Initialize extensions with the app ---
#     login_manager.init_app(app)
#     login_manager.login_view = 'auth.login'
#     login_manager.login_message_category = 'info'
    
#     # Make the Celery instance using our helper and attach it to the app
#     global celery
#     celery = make_celery(app)
#     # This line tells the Celery worker to look for tasks in the 'app.tasks' module.
#     celery.conf.imports = ('app.tasks',)

#     # --- Database Connection Helper ---
#     def get_db_connection():
#         try:
#             return mysql.connector.connect(**app.config['DB_CONFIG'])
#         except mysql.connector.Error as err:
#             print(f"Error connecting to database: {err}")
#             return None
#     app.get_db_connection = get_db_connection

#     # --- Register Blueprints (Imported inside the function to prevent circular imports) ---
#     with app.app_context():
#         from app.routes.auth import auth_bp
#         from app.routes.super_admin import super_admin_bp
#         from app.routes.admin import admin_bp
#         from app.routes.trainer import trainer_bp
#         from app.routes.student import student_bp
#         from app.main import main_bp
#         from app.utils.template_filters import filters_bp
        
#         app.register_blueprint(auth_bp)
#         app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
#         app.register_blueprint(admin_bp, url_prefix='/admin')
#         app.register_blueprint(trainer_bp, url_prefix='/trainer')
#         app.register_blueprint(student_bp, url_prefix='/student')
#         app.register_blueprint(main_bp)
#         app.register_blueprint(filters_bp)

#     return app

# __________________________________________

# from flask import Flask
# from flask_login import LoginManager
# import mysql.connector
# from dotenv import load_dotenv
# import os
# from celery import Celery

# # Load environment variables
# load_dotenv()

# # ===============================================================
# # Initialize Extensions Globally
# # ===============================================================
# # We create the extension objects here. They will be configured and
# # connected to the app inside the create_app() factory.
# login_manager = LoginManager()
# celery = Celery(__name__, 
#                 broker=os.getenv('CELERY_BROKER_URL'), 
#                 backend=os.getenv('CELERY_RESULT_BACKEND'))

# def create_app():
#     """
#     The Flask Application Factory.
#     """
#     app = Flask(__name__)

#     # --- Load Configuration from .env ---
#     app.config.from_mapping(
#         SECRET_KEY=os.getenv('SECRET_KEY'),
#         DEBUG=os.getenv('DEBUG', 'False').lower() in ['true', '1', 't'],
#         DB_CONFIG={
#             'host': os.getenv('DB_HOST'),
#             'database': os.getenv('DB_NAME'),
#             'user': os.getenv('DB_USER'),
#             'password': os.getenv('DB_PASSWORD')
#         },
#         UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
#         # Pass Celery config to Flask config. Use uppercase for Flask conventions.
#         CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL'),
#         CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND')
#     )
    
#     # Create upload directories
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

#     # --- Configure Celery with the App's Config ---
#     celery.conf.update(
#         broker_url=app.config['CELERY_BROKER_URL'],
#         result_backend=app.config['CELERY_RESULT_BACKEND']
#     )
#     # This is the key line to discover tasks.
#     celery.conf.imports = ('app.tasks',)
    
#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
#     celery.Task = ContextTask
    
#     # --- Initialize Other Extensions ---
#     login_manager.init_app(app)
#     login_manager.login_view = 'auth.login'
#     login_manager.login_message_category = 'info'
    
#     # --- Database Connection Helper ---
#     def get_db_connection():
#         try:
#             return mysql.connector.connect(**app.config['DB_CONFIG'])
#         except mysql.connector.Error as err:
#             print(f"Error connecting to database: {err}")
#             return None
#     app.get_db_connection = get_db_connection

#     # --- Register Blueprints (Imported inside the factory to prevent circular imports) ---
#     with app.app_context():
#         from app.routes.auth import auth_bp
#         from app.routes.super_admin import super_admin_bp
#         from app.routes.admin import admin_bp
#         from app.routes.trainer import trainer_bp
#         from app.routes.student import student_bp
#         from app.main import main_bp
        
#         app.register_blueprint(auth_bp)
#         app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
#         app.register_blueprint(admin_bp, url_prefix='/admin')
#         app.register_blueprint(trainer_bp, url_prefix='/trainer')
#         app.register_blueprint(student_bp, url_prefix='/student')
#         app.register_blueprint(main_bp)

#     return app

# _________________________________

# from flask import Flask
# from flask_login import LoginManager
# from flask_mail import Mail
# import mysql.connector
# from dotenv import load_dotenv
# import os
# from celery import Celery

# # Load environment variables from .env file
# load_dotenv()

# # ===============================================================
# # Initialize Extensions Globally
# # ===============================================================
# # We create the extension objects here. They will be configured and
# # connected to the app inside the create_app() factory function.

# login_manager = LoginManager()
# mail = Mail() # For sending emails
# celery = Celery(__name__, 
#                 broker=os.getenv('CELERY_BROKER_URL'), 
#                 backend=os.getenv('CELERY_RESULT_BACKEND'))

# def create_app():
#     """
#     The Flask Application Factory.
#     This function creates, configures, and returns the Flask app.
#     """
#     app = Flask(__name__)

#     # --- Load ALL Configuration from .env and set defaults ---
#     app.config.from_mapping(
#         SECRET_KEY=os.getenv('SECRET_KEY'),
#         DEBUG=os.getenv('DEBUG', 'False').lower() in ['true', '1', 't'],
        
#         DB_CONFIG={
#             'host': os.getenv('DB_HOST'),
#             'database': os.getenv('DB_NAME'),
#             'user': os.getenv('DB_USER'),
#             'password': os.getenv('DB_PASSWORD')
#         },

#         # Email Configuration for Flask-Mail (works with SendGrid)
#         MAIL_SERVER=os.getenv('MAIL_SERVER'),
#         MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
#         MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't'],
#         MAIL_USERNAME=os.getenv('MAIL_USERNAME'),      # Should be 'apikey' for SendGrid
#         MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),      # This is your SendGrid API Key
#         MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER'),

#         # File Upload Configuration
#         UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
#         ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif'},
#         MAX_CONTENT_LENGTH=2 * 1024 * 1024,  # 2MB Max file size for Flask

#         # Celery Configuration (using lowercase keys)
#         broker_url=os.getenv('CELERY_BROKER_URL'),
#         result_backend=os.getenv('CELERY_RESULT_BACKEND'),
#         imports=('app.tasks',) # Tells Celery where to find tasks
#     )
    
#     # Create the main upload directory and its subdirectories
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pictures'), exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments'), exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'submissions'), exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'test_cases'), exist_ok=True)
#     os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    
#     # --- Configure and Initialize Extensions with the App ---
    
#     # Configure Celery
#     celery.conf.update(
#         broker_url=app.config['broker_url'],
#         result_backend=app.config['result_backend'],
#         imports=app.config['imports']
#     )
#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
#     celery.Task = ContextTask

#     # Initialize Flask-Login and Flask-Mail
#     login_manager.init_app(app)
#     login_manager.login_view = 'auth.login'
#     login_manager.login_message_category = 'info'
#     mail.init_app(app)
    
#     # --- Database Connection Helper ---
#     def get_db_connection():
#         try:
#             return mysql.connector.connect(**app.config['DB_CONFIG'])
#         except mysql.connector.Error as err:
#             print(f"Error connecting to database: {err}")
#             return None
#     app.get_db_connection = get_db_connection

#     # --- Register Blueprints (Imported inside the factory to prevent circular imports) ---
#     with app.app_context():
#         from app.routes.auth import auth_bp
#         from app.routes.super_admin import super_admin_bp
#         from app.routes.admin import admin_bp
#         from app.routes.trainer import trainer_bp
#         from app.routes.student import student_bp
#         from app.main import main_bp
#         from app.utils.template_filters import filters_bp
        
#         app.register_blueprint(auth_bp)
#         app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
#         app.register_blueprint(admin_bp, url_prefix='/admin')
#         app.register_blueprint(trainer_bp, url_prefix='/trainer')
#         app.register_blueprint(student_bp, url_prefix='/student')
#         app.register_blueprint(main_bp)
#         app.register_blueprint(filters_bp)

#     return app


# _______________________________-

# from flask import Flask
# from flask_login import LoginManager
# from flask_mail import Mail
# import mysql.connector
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()

# # Initialize extensions globally, but without the app
# login_manager = LoginManager()
# mail = Mail()

# def create_app():
#     """
#     The Flask Application Factory.
#     """
#     app = Flask(__name__)

#     # --- Load ALL Configuration from .env ---
#     app.config.from_mapping(
#         SECRET_KEY=os.getenv('SECRET_KEY'),
#         DEBUG=os.getenv('DEBUG', 'False').lower() in ['true', '1', 't'],
#         DB_CONFIG={
#             'host': os.getenv('DB_HOST'),
#             'database': os.getenv('DB_NAME'),
#             'user': os.getenv('DB_USER'),
#             'password': os.getenv('DB_PASSWORD')
#         },
#         # Email Configuration
#         MAIL_SERVER=os.getenv('MAIL_SERVER'),
#         MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
#         MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't'],
#         MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
#         MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
#         MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER'),
#         # File Upload Configuration
#         UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
#         ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif'},
#         MAX_CONTENT_LENGTH=2 * 1024 * 1024,
#         # Celery Configuration (will be used by the Celery app)
#         CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL'),
#         CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND')
#     )
    
#     # Create upload directory
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
#     # --- Initialize Extensions with the App ---
#     login_manager.init_app(app)
#     login_manager.login_view = 'auth.login'
#     mail.init_app(app)
    
#     # --- Database Connection Helper ---
#     def get_db_connection():
#         try:
#             return mysql.connector.connect(**app.config['DB_CONFIG'])
#         except mysql.connector.Error as err:
#             print(f"Error connecting to database: {err}")
#             return None
#     app.get_db_connection = get_db_connection

#     # --- Register Blueprints ---
#     with app.app_context():
#         from app.routes.auth import auth_bp
#         from app.routes.super_admin import super_admin_bp
#         from app.routes.admin import admin_bp
#         from app.routes.trainer import trainer_bp
#         from app.routes.student import student_bp
#         from app.main import main_bp
        
#         app.register_blueprint(auth_bp)
#         app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
#         app.register_blueprint(admin_bp, url_prefix='/admin')
#         app.register_blueprint(trainer_bp, url_prefix='/trainer')
#         app.register_blueprint(student_bp, url_prefix='/student')
#         app.register_blueprint(main_bp)

#     return app

# _________________________

# from flask import Flask
# from dotenv import load_dotenv
# import os
# import mysql.connector
# from .extensions import login_manager, mail, celery

# # Load environment variables
# load_dotenv()

# def create_app():
#     """
#     The Flask Application Factory.
#     """
#     app = Flask(__name__)

#     # --- Load Configuration from .env ---
#     app.config.from_mapping(
#         SECRET_KEY=os.getenv('SECRET_KEY'),
#         DEBUG=os.getenv('DEBUG', 'False').lower() in ['true', '1', 't'],
#         DB_CONFIG={
#             'host': os.getenv('DB_HOST'),
#             'database': os.getenv('DB_NAME'),
#             'user': os.getenv('DB_USER'),
#             'password': os.getenv('DB_PASSWORD')
#         },
#         UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads','profile_pictures'),
#         ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif'},
#         MAX_CONTENT_LENGTH=2 * 1024 * 1024,
#         # Mail Configuration
#         MAIL_SERVER=os.getenv('MAIL_SERVER'),
#         MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
#         MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't'],
#         MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
#         MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
#         MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER'),
#         # Celery Configuration
#         CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL'),
#         CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND')
#     )
    
#     # Create upload directory
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
#     # --- Initialize Extensions ---
#     login_manager.init_app(app)
#     login_manager.login_view = 'auth.login'
#     mail.init_app(app)



#     # --- Configure Celery ---
#     celery.conf.update(
#         broker_url=app.config['CELERY_BROKER_URL'],
#         result_backend=app.config['CELERY_RESULT_BACKEND']
#     )
#     celery.conf.imports = ('app.tasks',)
#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
#     celery.Task = ContextTask
    
#     # --- Database Connection Helper ---
#     def get_db_connection():
#         try:
#             return mysql.connector.connect(**app.config['DB_CONFIG'])
#         except mysql.connector.Error as err:
#             print(f"Error connecting to database: {err}")
#             return None
#     app.get_db_connection = get_db_connection

#     # --- Register Blueprints ---
#     with app.app_context():
#         from app.routes.auth import auth_bp
#         from app.routes.super_admin import super_admin_bp
#         from app.routes.admin import admin_bp
#         from app.routes.trainer import trainer_bp
#         from app.routes.student import student_bp
#         from app.main import main_bp
        
#         app.register_blueprint(auth_bp)
#         app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
#         app.register_blueprint(admin_bp, url_prefix='/admin')
#         app.register_blueprint(trainer_bp, url_prefix='/trainer')
#         app.register_blueprint(student_bp, url_prefix='/student')
#         app.register_blueprint(main_bp)

#     return app



# ______________


from flask import Flask
import mysql.connector
from dotenv import load_dotenv
import os

# Import the extension instances that were created globally
from .extensions import login_manager, mail, celery

# Load environment variables from .env file
load_dotenv()

def create_app():
    """
    The Flask Application Factory.
    Creates, configures, and returns the Flask app.
    """
    app = Flask(__name__)

    # --- Load Configuration from .env ---
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        DEBUG=os.getenv('DEBUG', 'False').lower() in ['true', '1', 't'],
        DB_CONFIG={
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        },
        UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
        ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif'},
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        # Mail Configuration for SendGrid
        MAIL_SERVER=os.getenv('MAIL_SERVER'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't'],
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER'),
        # Celery Configuration
        CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL'),
        CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND')
    )
    
    # Create necessary upload subdirectories if they don't exist
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pictures'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'submissions'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'test_cases'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    
    # --- Initialize Extensions with the App ---
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)

    # --- Configure Celery within the factory ---
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND']
    )
    # This is the crucial line that tells Celery where to find your task definitions
    celery.conf.imports = ('app.tasks',)

    # This ensures tasks run with the Flask application context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    
    # --- Database Connection Helper ---
    def get_db_connection():
        try:
            return mysql.connector.connect(**app.config['DB_CONFIG'])
        except mysql.connector.Error as err:
            app.logger.error(f"Database connection error: {err}")
            return None
    app.get_db_connection = get_db_connection

    # --- Register Blueprints ---
    with app.app_context():
        from app.routes.auth import auth_bp
        from app.routes.super_admin import super_admin_bp
        from app.routes.admin import admin_bp
        from app.routes.trainer import trainer_bp
        from app.routes.student import student_bp
        from app.main import main_bp
        from app.utils.template_filters import filters_bp # Assuming you have this
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(trainer_bp, url_prefix='/trainer')
        app.register_blueprint(student_bp, url_prefix='/student')
        app.register_blueprint(main_bp)
        app.register_blueprint(filters_bp)

    return app