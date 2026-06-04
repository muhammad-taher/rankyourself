from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db_manager import execute_query

admin_bp = Blueprint('admin', __name__)

# Hardcoded Admin Credentials
ADMIN_USER = "taher"
ADMIN_PASS = "itstaher"

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['is_admin'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            
    return render_template('admin/login.html')

@admin_bp.route('/')
def dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
        
    users = execute_query("""
        SELECT s.id, s.name, s.student_id, s.email, d.short_code as dept, b.batch_number 
        FROM students s
        JOIN departments d ON s.dept_id = d.id
        JOIN batches b ON s.batch_id = b.id
    """)
    return render_template('admin/dashboard.html', users=users)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
        
    # Delete student (cascades will handle accounts, stats, etc. if FKs are set to CASCADE)
    execute_query("DELETE FROM students WHERE id = %s", (user_id,), commit=True)
    flash(f'User ID {user_id} has been removed.', 'warning')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin.login'))
