from flask import Blueprint, render_template, request
from services.rank_algo import get_rankings
from database.db_manager import execute_query

ranking_bp = Blueprint('ranking', __name__)

@ranking_bp.route('/rankings')
def global_rankings():
    dept_id = request.args.get('dept_id', type=int)
    batch_id = request.args.get('batch_id', type=int)
    search_query = request.args.get('q', type=str)
    
    ranks = get_rankings(dept_id=dept_id, batch_id=batch_id, search_query=search_query)
    
    depts = execute_query("SELECT * FROM departments")
    batches = execute_query("SELECT * FROM batches")
    
    return render_template('ranking/global.html', 
                         rankings=ranks, 
                         depts=depts, 
                         batches=batches,
                         selected_dept=dept_id,
                         selected_batch=batch_id,
                         search_query=search_query)
