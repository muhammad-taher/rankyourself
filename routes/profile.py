from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db_manager import execute_query
from services.scraper import sync_student_stats

profile_bp = Blueprint('profile', __name__)

from urllib.parse import urlparse

def is_valid_url(url):
    if not url: return True # Optional field
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

@profile_bp.route('/me', methods=['GET', 'POST'])
def my_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    
    if request.method == 'POST':
        # Update Social and Platform Links
        links = {
            'github_url': request.form.get('github_url'),
            'linkedin_url': request.form.get('linkedin_url'),
            'codeforces_url': request.form.get('codeforces_url'),
            'codechef_url': request.form.get('codechef_url'),
            'atcoder_url': request.form.get('atcoder_url'),
            'leetcode_url': request.form.get('leetcode_url'),
            'beecrowd_url': request.form.get('beecrowd_url')
        }
        
        # Validate URLs
        for label, url in links.items():
            if url and not is_valid_url(url):
                flash(f'Invalid URL provided for {label.replace("_", " ").title()}', 'danger')
                return redirect(url_for('profile.my_profile'))
        
        execute_query("""
            UPDATE students SET 
                github_url = %s, linkedin_url = %s,
                codeforces_url = %s, codechef_url = %s,
                atcoder_url = %s, leetcode_url = %s,
                beecrowd_url = %s
            WHERE id = %s
        """, (links['github_url'], links['linkedin_url'], 
              links['codeforces_url'], links['codechef_url'], 
              links['atcoder_url'], links['leetcode_url'], 
              links['beecrowd_url'], user_id), commit=True)
        
        # Add CP Account
        platform_id = request.form.get('platform_id')
        username = request.form.get('username')
        if platform_id and username:
            # Basic sanitization
            username = username.strip()[:100]
            execute_query("""
                INSERT IGNORE INTO student_cp_accounts (student_id, platform_id, username)
                VALUES (%s, %s, %s)
            """, (user_id, platform_id, username), commit=True)
            sync_student_stats(user_id)
            
        # Handle manual Beecrowd solved count
        bc_solved_raw = request.form.get('beecrowd_solved')
        if bc_solved_raw:
            try:
                bc_solved = int(bc_solved_raw)
                if bc_solved < 0: raise ValueError
                
                # Find beecrowd account id
                bc_acc = execute_query("""
                    SELECT a.id FROM student_cp_accounts a 
                    JOIN cp_platforms p ON a.platform_id = p.id 
                    WHERE a.student_id = %s AND p.name = 'Beecrowd'
                """, (user_id,))
                if bc_acc:
                    execute_query("""
                        INSERT INTO cp_current_stats (account_id, total_solved)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE total_solved = %s
                    """, (bc_acc[0]['id'], bc_solved, bc_solved), commit=True)
            except ValueError:
                flash('Beecrowd solved count must be a positive number.', 'danger')
                return redirect(url_for('profile.my_profile'))
        
        flash('Profile updated!', 'success')

    user_results = execute_query("SELECT * FROM students WHERE id = %s", (user_id,))
    if not user_results:
        session.clear()
        return redirect(url_for('auth.login'))
        
    user = user_results[0]
    accounts = execute_query("""
        SELECT a.*, p.name as platform_name, cs.* 
        FROM student_cp_accounts a 
        JOIN cp_platforms p ON a.platform_id = p.id 
        LEFT JOIN cp_current_stats cs ON a.id = cs.account_id
        WHERE a.student_id = %s
    """, (user_id,))
    platforms = execute_query("SELECT * FROM cp_platforms")
    
    return render_template('profile/me.html', user=user, accounts=accounts, platforms=platforms)

@profile_bp.route('/user/<int:user_id>')
def public_profile(user_id):
    user_results = execute_query("""
        SELECT s.*, d.name as dept_name, b.batch_number 
        FROM students s
        JOIN departments d ON s.dept_id = d.id
        JOIN batches b ON s.batch_id = b.id
        WHERE s.id = %s
    """, (user_id,))
    
    if not user_results:
        flash('User not found.', 'danger')
        return redirect(url_for('ranking.global_rankings'))
        
    user = user_results[0]
    accounts = execute_query("""
        SELECT a.*, p.name as platform_name, cs.* 
        FROM student_cp_accounts a 
        JOIN cp_platforms p ON a.platform_id = p.id 
        LEFT JOIN cp_current_stats cs ON a.id = cs.account_id
        WHERE a.student_id = %s
    """, (user_id,))
    
    return render_template('profile/public.html', user=user, accounts=accounts)

@profile_bp.route('/sync')
def sync_stats():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    sync_student_stats(session['user_id'])
    flash('Stats synced successfully!', 'success')
    return redirect(url_for('profile.my_profile'))
