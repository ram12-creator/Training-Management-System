# Training Management System

A comprehensive training management system built with Flask, MySQL, and Celery for handling background tasks. The application supports multiple user roles (Super Admin, Admin, Trainer, Student) with distinct functionalities for each.

## Features
-   **Multi-Role Authentication:** Secure login for four different user roles.
-   **Course & Batch Management:** Admins can create and manage courses and student batches.
-   **Student Management:** Admins can enroll, manage, and track student details.
-   **Attendance System:** Admins can mark and export attendance records.
-   **Leave Management:** Students can apply for leave, and admins can approve or reject requests with email notifications.
-   **Hierarchical Curriculum:** Trainers can create a nested curriculum of topics and sub-topics.
-   **Assignment Workflow:** Trainers can create assignments with optional auto-grading (Python, SQL, etc.), and students can submit their work.
-   **Background Tasks:** Uses Celery and Redis for handling time-consuming tasks like auto-grading without freezing the application.

---

## Setup and Installation

Follow these steps to get the project running on your local machine.

### Prerequisites
-   Python 3.8+
-   Git
-   MySQL Server (e.g., MySQL Community Server)
-   Redis Server (for Celery)

### 1. Clone the Repository```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```
*(Replace the URL with your actual GitHub repository URL after you create it.)*

### 2. Create and Activate Virtual Environment
This isolates the project's dependencies from your system.

```bash
# For Windows
python -m venv util_venv
util_venv\Scripts\activate

# For macOS/Linux
python3 -m venv util_venv
source util_venv/bin/activate
```

### 3. Install Dependencies
This command installs all the required Python packages from the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
This project uses a `.env` file to manage secret keys and configuration.

**a. Create your local environment file:**
Copy the example file to a new file named `.env`.

```bash
# For Windows (Command Prompt)
copy .env.example .env

# For macOS/Linux or Git Bash
cp .env.example .env
```

**b. Edit the `.env` file:**
Open the new `.env` file in your editor and fill in your actual database password, a new secret key, and your SendGrid API key.

```env
# .env
DB_HOST=localhost
DB_NAME=training_management
DB_USER=root
DB_PASSWORD=your_mysql_password_here
SECRET_KEY=a_very_strong_and_random_secret_key
MAIL_PASSWORD=your_sendgrid_api_key_here

### 5. Set Up the Database
You need to create the database and then import the schema from the provided SQL file.

**a. Log in to your MySQL client:**
```bash
mysql -u root -p
```
*(Enter your MySQL root password when prompted.)*

**b. Create the database:** (Make sure the name matches `DB_NAME` in your `.env` file)
```sql
CREATE DATABASE training_management;
```

**c. Exit MySQL and import the schema:**
Run the following command from your project's root directory (`Train System`). It will create all the necessary tables.
```bash
mysql -u root -p training_management < database/schema.sql
```
*(Enter your MySQL password again when prompted.)*

### 6. Run the Application
You need to run three separate processes in three different terminals.

**Terminal 1: Start the Redis Server**
Make sure your Redis server is running. If you installed it as a service, it might already be running. Otherwise, start it manually.
```bash
redis-server
```

**Terminal 2: Start the Celery Worker**
(Make sure your virtual environment is activated in this terminal)
```bash
celery -A celery_app.celery worker --loglevel=info --pool=solo
```

**Terminal 3: Start the Flask Web Server**
(Make sure your virtual environment is activated in this terminal)
```bash
python run.py
```

The application should now be running at `http://127.0.0.1:5000`. You can log in with the superadmin credentials:
-   **Email:** `superadmin@trainingsystem.com`
-   **Password:** `admin123`