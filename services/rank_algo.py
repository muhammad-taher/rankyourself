from database.db_manager import execute_query

import math

class UnifiedRankingEngine:
    def __init__(self):
        # Asymptotic tuning parameters (k-constants) 
        self.K_CF_SOLVES = 300.0  # Decays smoothly around 300+ high-tier solves
        self.K_LC_WEIGHTS = 1000.0 # Decays smoothly around 1000 points
        self.K_AC_SOLVES = 200.0  # AtCoder problem density
        self.K_CC_SOLVES = 400.0  # CodeChef problem density
        self.K_BC_SOLVES = 500.0  # Beecrowd problem density

        # Maximum capped thresholds for ratings
        self.CF_MAX_RATING = 2400.0  # Grandmaster cap
        self.CC_MAX_RATING = 2200.0  # 5-6 Star cap

    def calculate_codeforces(self, quality_sum, peak_rating):
        """Codeforces: Max 35 Points."""
        # s_solves: Max 25
        s_solves = 25.0 * (1.0 - math.exp(-float(quality_sum) / self.K_CF_SOLVES))
        # s_rating: Max 10
        s_rating = 10.0 * min(1.0, float(peak_rating) / self.CF_MAX_RATING)
        return round(s_solves + s_rating, 2)

    def calculate_leetcode(self, easy, medium, hard):
        """LeetCode: Max 25 Points."""
        weighted_score = (int(easy) * 1) + (int(medium) * 3) + (int(hard) * 6)
        s_lc = 25.0 * (1.0 - math.exp(-weighted_score / self.K_LC_WEIGHTS))
        return round(s_lc, 2)

    def calculate_atcoder(self, solved):
        """AtCoder: Max 20 Points."""
        s_ac = 20.0 * (1.0 - math.exp(-int(solved) / self.K_AC_SOLVES))
        return round(s_ac, 2)

    def calculate_codechef(self, solved, peak_rating):
        """CodeChef: Max 12 Points."""
        s_solves = 9.0 * (1.0 - math.exp(-int(solved) / self.K_CC_SOLVES))
        s_rating = 3.0 * min(1.0, float(peak_rating) / self.CC_MAX_RATING)
        return round(s_solves + s_rating, 2)

    def calculate_beecrowd(self, solved):
        """Beecrowd: Max 8 Points."""
        s_bc = 8.0 * (1.0 - math.exp(-int(solved) / self.K_BC_SOLVES))
        return round(s_bc, 2)

def get_rankings(dept_id=None, batch_id=None, search_query=None):
    # Fetch all raw stats for all accounts of students
    query = """
        SELECT s.id as user_id, s.name, s.student_id, d.short_code as dept, b.batch_number,
               p.name as platform_name, cs.*
        FROM students s
        JOIN departments d ON s.dept_id = d.id
        JOIN batches b ON s.batch_id = b.id
        LEFT JOIN student_cp_accounts sca ON s.id = sca.student_id
        LEFT JOIN cp_current_stats cs ON sca.id = cs.account_id
        LEFT JOIN cp_platforms p ON sca.platform_id = p.id
    """
    
    where_clauses = []
    params = []
    
    if dept_id:
        where_clauses.append("s.dept_id = %s")
        params.append(dept_id)
    if batch_id:
        where_clauses.append("s.batch_id = %s")
        params.append(batch_id)
    if search_query:
        where_clauses.append("(s.name LIKE %s OR s.student_id LIKE %s)")
        params.append(f"%{search_query}%")
        params.append(f"%{search_query}%")
        
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
        
    results = execute_query(query, tuple(params))
    
    if not results:
        return []

    engine = UnifiedRankingEngine()
    
    # Aggregate stats by user
    users = {}
    for row in results:
        uid = row['user_id']
        if uid not in users:
            users[uid] = {
                'user_id': uid,
                'name': row['name'],
                'student_id': row['student_id'],
                'dept': row['dept'],
                'batch_number': row['batch_number'],
                'total_solved': 0,
                'peak_rating': 0,
                'score': 0.0
            }
        
        if row['platform_name']:
            platform = row['platform_name']
            solved = int(row['total_solved'] or 0)
            curr_rating = int(row['current_rating'] or 0)
            peak_rating = int(row['max_rating'] or 0)
            
            # Global display stats
            users[uid]['total_solved'] += solved
            users[uid]['peak_rating'] = max(users[uid]['peak_rating'], peak_rating)
            
            # Platform specific scoring
            if platform == 'Codeforces':
                users[uid]['score'] += engine.calculate_codeforces(row.get('cf_quality_sum', 0), peak_rating)
            elif platform == 'LeetCode':
                users[uid]['score'] += engine.calculate_leetcode(
                    int(row['lc_easy'] or 0), 
                    int(row['lc_medium'] or 0), 
                    int(row['lc_hard'] or 0)
                )
            elif platform == 'AtCoder':
                users[uid]['score'] += engine.calculate_atcoder(solved)
            elif platform == 'CodeChef':
                users[uid]['score'] += engine.calculate_codechef(solved, peak_rating)
            elif platform == 'Beecrowd':
                users[uid]['score'] += engine.calculate_beecrowd(solved)
                
    for uid in users:
        users[uid]['score'] = min(100.0, round(users[uid]['score'], 2))
    
    sorted_users = sorted(users.values(), key=lambda x: x['score'], reverse=True)
    return sorted_users
