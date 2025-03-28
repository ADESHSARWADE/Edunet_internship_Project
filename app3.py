from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import bcrypt
from flask_mysqldb import MySQL
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# MySQL Config
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")  # Use the correct MySQL host
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")  # Use your MySQL username
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")  # Use your MySQL password
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")  # Use the correct database name
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')  # Your HTML content

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/employee', methods=['GET', 'POST'])
def employee():
    if request.method == 'POST':
        full_name = request.form['fullName']
        email = request.form['email']
        phone_no = request.form['phone']
        join_date = request.form['joinDate']
        designation = request.form['designation']
        salary = request.form['salary']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('employee'))

        # Hashing the password with bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Get the current date and time for registration
        registration_datetime = datetime.now()

        # Create a cursor
        cur = mysql.connection.cursor()

        # Insert data into the employees table
        cur.execute("""
        INSERT INTO employees (full_name, email, phone_no, join_date, designation, salary, password, registration_datetime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (full_name, email, phone_no, join_date, designation, salary, hashed_password, registration_datetime))  

        # Commit the transaction
        mysql.connection.commit()

        # Close the cursor
        cur.close()

        # Flash success message
        flash('Thank you for registering! Your account has been created.', 'success')

        # Redirect to the registration page again or another page
        return redirect(url_for('employee'))
    
    return render_template('employee.html')

@app.route('/manager', methods=['GET', 'POST'])
def manager():
    if request.method == 'POST':
        full_name = request.form['fullName']
        email = request.form['email']
        phone = request.form['phone']
        join_date = request.form['joinDate']
        department = request.form['department']
        salary = request.form['salary']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('manager'))
        
        # Hashing the password with bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Get the current date and time for registration
        registration_datetime = datetime.now()

        # Create a cursor
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO managers (full_name, email, phone_no, join_date, department, salary, password, registration_datetime)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (full_name, email, phone, join_date, department, salary, hashed_password, registration_datetime))
        
        # Commit the transaction
        mysql.connection.commit()
        
        # Close the cursor
        cur.close()
        
        # Flash success message
        flash('Manager account has been successfully created!', 'success')
        
        # Redirect to the manager registration page again
        return redirect(url_for('manager'))
    
    return render_template('manager.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        email = request.form.get('email')
        password = request.form.get('password')

        cur = mysql.connection.cursor()

        # For Employee Login
        if user_type == 'employee':
            cur.execute('SELECT * FROM employees WHERE email = %s', (email,))
            employee = cur.fetchone()
            if employee and bcrypt.checkpw(password.encode('utf-8'), employee[7].encode('utf-8')):  # Check hashed password (corrected index)
                session['user_id'] = employee[0]  # Store user id in session
                session['user_name'] = employee[1]  # Store full name in session
                session['email'] = employee[2]  # Store email in session
                session['phone_no'] = employee[3]  # Store phone number in session
                session['join_date'] = employee[4]  # Store join date in session
                session['designation'] = employee[5]  # Store designation in session
                session['salary'] = employee[6]  # Store salary in session
                session['password'] = employee[7]  # Store password in session
                session['registration_datetime'] = employee[8]  # Store registration datetime in session
                session['created_at'] = employee[9]  # Store creation timestamp in session
                
                session['user_role'] = 'employee'  # Store role in session
                flash(f'Login successful as {session["user_role"]}!', 'success')  # Flash message
                return redirect(url_for('employee_dashboard'))  # Redirect to employee dashboard
            else:
                flash('Wrong password entered for employee.', 'danger')
                return redirect(url_for('login'))

        # For Manager Login
        elif user_type == 'manager':  
            cur.execute('SELECT * FROM managers WHERE email = %s', (email,))  
            manager = cur.fetchone()
            if manager and bcrypt.checkpw(password.encode('utf-8'), manager[7].encode('utf-8')):  # Check hashed password
                session['user_id'] = manager[0]  # Store user id (manager's ID) in session
                session['user_name'] = manager[1]  # Store full name in session
                session['email'] = manager[2]  # Store email in session
                session['phone_no'] = manager[3]  # Store phone number in session
                session['join_date'] = manager[4]  # Store join date in session
                session['department'] = manager[5]  # Store department in session
                session['salary'] = manager[6]  # Store salary in session
                session['password'] = manager[7]  # Store password in session
                session['registration_datetime'] = manager[8]  # Store registration datetime in session

                session['user_role'] = 'manager'  # Store role in session
                flash(f'Login successful as {session["user_role"]}!', 'success')  # Flash message
                return redirect(url_for('manager_dashboard'))  # Redirect to manager dashboard
            else:
                flash('Wrong password entered for manager.', 'danger')
                return redirect(url_for('login'))

        cur.close()

    return render_template('login.html')  # Render login page

@app.route('/employee_dashboard')
def employee_dashboard():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, full_name, email, phone_no, join_date, designation, salary FROM employees')
    employees = cur.fetchall()
    cur.close()
    
    return render_template('employee_dashboard.html',employees=employees, user_name=session.get('user_name'), designation=session.get('designation'))

@app.route('/manager_dashboard')
def manager_dashboard():
    # Create a cursor
    cur = mysql.connection.cursor()

    # Execute query to fetch employee data
    cur.execute('SELECT id, full_name, email, phone_no, join_date, designation, salary FROM employees')

    # Fetch all results from the query
    employees = cur.fetchall()

    # Close the cursor
    cur.close()

    # Pass the employees data to the template
    return render_template('manager_dashboard.html', employees=employees)


@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))  # Redirect to the login page



@app.route('/attendance')
def attendance():
    return render_template('attendance.html', user_id = session.get('user_id') ,user_name=session.get('user_name'), designation=session.get('designation'),join_date = session.get('join_date') )  # Assuming you have this template



@app.route('/profile')
def profile():
    # Fetch user data from session
    user_id = session.get('user_id')
    full_name = session.get('full_name')
    email = session.get('email')
    phone_no = session.get('phone_no')
    join_date = session.get('join_date')
    designation = session.get('designation')
    salary = session.get('salary')
    registration_datetime = session.get('registration_datetime')
    created_at = session.get('created_at')

    if not user_id:
        # If no user_id is found in session, redirect to login or handle appropriately
        return redirect(url_for('login'))

    # Connect to the database and fetch the employee details based on the user_id
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, full_name, email, phone_no, join_date, designation, salary, registration_datetime, created_at FROM employees') 

    # Fetch the specific employee details
    employee = cur.fetchone()

    # Close the cursor
    cur.close()

    # If employee is not found, redirect to login or handle accordingly
    if not employee:
        return redirect(url_for('login'))

    # Pass the employee details to the template and render it
    return render_template(
        'profile.html',
        employee=employee,  # Pass the entire employee record
        full_name=full_name,
        email=email,
        phone_no=phone_no,
        join_date=join_date,
        designation=designation,
        salary=salary,
        registration_datetime=registration_datetime,
        created_at=created_at
    )


# Updating employee profile
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        # Get updated data from form
        full_name = request.form['full_name']
        email = request.form['email']
        phone_no = request.form['phone_no']
        # Assume the image is uploaded or updated
        
        # Get the employee_id from session
        employee_id = session.get('employee_id')
        
        cur = mysql.connection.cursor()
        cur.execute('''UPDATE employees 
                       SET full_name=%s, email=%s, phone_no=%s, profile_picture=%s 
                       WHERE id=%s''', (full_name, email, phone_no, employee_id))
        mysql.connection.commit()
        cur.close()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html')

# Applying for leave
@app.route('/apply_leave', methods=['GET', 'POST'])
def apply_leave():
    if request.method == 'POST':
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        reason = request.form['reason']
        
        # Get the employee_id from session
        employee_id = session.get('employee_id')
        
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO employee_leaves (employee_id, leave_type, start_date, end_date, reason, status)
                       VALUES (%s, %s, %s, %s, %s, %s)''', (employee_id, leave_type, start_date, end_date, reason, 'Pending'))
        mysql.connection.commit()
        cur.close()

        flash('Leave application submitted successfully!', 'success')
        return redirect(url_for('attendance'))  # Redirect to attendance or dashboard

    return render_template('apply_leave.html')

# View applied leaves
@app.route('/leave_history')
def leave_history():
    employee_id = session.get('employee_id')
    cur = mysql.connection.cursor()
    cur.execute('SELECT leave_type, start_date, end_date, status FROM employee_leaves WHERE employee_id = %s', (employee_id,))
    leaves = cur.fetchall()
    cur.close()
    
    return render_template('leave_history.html', leaves=leaves)

# Submit a report to manager
@app.route('/report_to_manager', methods=['GET', 'POST'])
def report_to_manager():
    if request.method == 'POST':
        subject = request.form['subject']
        message = request.form['message']
        
        employee_id = session.get('employee_id')
        
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO reports (employee_id, subject, message) VALUES (%s, %s, %s)', (employee_id, subject, message))
        mysql.connection.commit()
        cur.close()

        flash('Report submitted successfully!', 'success')
        return redirect(url_for('employee_dashboard'))

    return render_template('report_to_manager.html')


@app.route('/attendance_manager')
def attendance_manager():
    return render_template('attendance_manager.html')

if __name__ == '__main__':
    app.run(debug=True)
