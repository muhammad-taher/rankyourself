from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db_manager import execute_query
from services.mail_service import send_verification_email, send_reset_password_email
import random
import re
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def is_valid_student_id(student_id):
    # Format: DEPT-YEAR_ROLL (e.g., CE-24031)
    # Allows 2-3 uppercase letters, a dash, and 5 digits
    pattern = r'^[A-Z]{2,3}-\d{5}$'
    return re.match(pattern, student_id) is not None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form.get('student_id').upper()
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        dept_id = request.form.get('dept_id')
        batch_id = request.form.get('batch_id')
        
        # Validation
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('auth.register'))

        if not is_valid_student_id(student_id):
            flash('Invalid Student ID format! Use DEPT-XXXXX (e.g., CE-24031).', 'danger')
            return redirect(url_for('auth.register'))

        if not email.endswith('@mbstu.ac.bd'):
            flash('Only MBSTU emails are allowed!', 'danger')
            return redirect(url_for('auth.register'))
            
        # Check if user already exists
        existing = execute_query("SELECT id FROM students WHERE email = %s OR student_id = %s", (email, student_id))
        if existing:
            flash('Email or Student ID already registered.', 'danger')
            return redirect(url_for('auth.register'))

        # Generate verification code
        code = str(random.randint(100000, 999999))
        expiry = datetime.now() + timedelta(minutes=10)
        
        # Store in session for verification
        session['reg_data'] = {
            'student_id': student_id,
            'name': name,
            'email': email,
            'password_hash': generate_password_hash(password),
            'dept_id': dept_id,
            'batch_id': batch_id,
            'code': code,
            'expiry': expiry.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        send_verification_email(email, code)
        flash('Verification code sent to your email!', 'info')
        return redirect(url_for('auth.verify'))
            
    depts = execute_query("SELECT * FROM departments")
    batches = execute_query("SELECT * FROM batches")
    return render_template('auth/register.html', depts=depts, batches=batches)

@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'reg_data' not in session:
        return redirect(url_for('auth.register'))
        
    if request.method == 'POST':
        input_code = request.form.get('code')
        reg_data = session['reg_data']
        
        expiry = datetime.strptime(reg_data['expiry'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() > expiry:
            flash('Verification code expired. Please register again.', 'danger')
            session.pop('reg_data')
            return redirect(url_for('auth.register'))
            
        if input_code == reg_data['code']:
            # Create user
            query = """
                INSERT INTO students (student_id, name, email, password_hash, dept_id, batch_id, is_verified) 
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            """
            params = (reg_data['student_id'], reg_data['name'], reg_data['email'], 
                      reg_data['password_hash'], reg_data['dept_id'], reg_data['batch_id'])
            
            result = execute_query(query, params, commit=True)
            if result:
                session.pop('reg_data')
                flash('Email verified! You can now login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Registration failed during database save.', 'danger')
        else:
            flash('Invalid verification code.', 'danger')
            
    return render_template('auth/verify.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = execute_query("SELECT id FROM students WHERE email = %s", (email,))
        
        if user:
            code = str(random.randint(100000, 999999))
            expiry = datetime.now() + timedelta(minutes=10)
            
            execute_query("""
                UPDATE students SET reset_token = %s, reset_expiry = %s WHERE email = %s
            """, (code, expiry, email), commit=True)
            
            send_reset_password_email(email, code)
            flash('Password reset code sent to your email!', 'info')
            return redirect(url_for('auth.reset_password', email=email))
        else:
            flash('No account found with that email.', 'danger')
            
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email')
    if request.method == 'POST':
        # Use email from form if available, otherwise from args
        email = request.form.get('email') or email
        code = request.form.get('code', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        print(f"DEBUG: Reset attempt - Email: {email}, Code: {code}")
        
        if not email or not code:
            flash('Email and reset code are required.', 'danger')
            return render_template('auth/reset_password.html', email=email, code=code)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', code=code, email=email)
            
        user = execute_query("SELECT * FROM students WHERE email = %s AND reset_token = %s", (email, code))
        
        if user:
            expiry = user[0]['reset_expiry']
            if datetime.now() > expiry:
                flash('Reset code expired. Please request a new one.', 'danger')
                return redirect(url_for('auth.forgot_password'))
                
            new_hash = generate_password_hash(password)
            execute_query("""
                UPDATE students SET password_hash = %s, reset_token = NULL, reset_expiry = NULL 
                WHERE id = %s
            """, (new_hash, user[0]['id']), commit=True)
            
            flash('Password reset successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            print(f"DEBUG: Reset failed - No user found for {email} with code {code}")
            flash('Invalid reset code or email.', 'danger')
            
    return render_template('auth/reset_password.html', email=email)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = execute_query("SELECT * FROM students WHERE email = %s", (email,))
        
        if user and check_password_hash(user[0]['password_hash'], password):
            if not user[0]['is_verified']:
                flash('Please verify your email first.', 'warning')
                # Optional: Resend verification code logic could go here
                return redirect(url_for('auth.login'))
                
            session['user_id'] = user[0]['id']
            session['user_name'] = user[0]['name']
            flash(f'Welcome back, {user[0]["name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
