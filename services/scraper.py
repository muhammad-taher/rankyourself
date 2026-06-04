import requests
from bs4 import BeautifulSoup
from database.db_manager import execute_query
import re

class CPScraper:
    @staticmethod
    def fetch_codeforces(username):
        try:
            # Info for rating
            info_url = f"https://codeforces.com/api/user.info?handles={username}"
            info_resp = requests.get(info_url, timeout=10).json()
            
            # Submissions for solved count
            status_url = f"https://codeforces.com/api/user.status?handle={username}"
            status_resp = requests.get(status_url, timeout=10).json()
            
            if info_resp['status'] == 'OK' and status_resp['status'] == 'OK':
                user_data = info_resp['result'][0]
                submissions = status_resp['result']
                
                solved_problems = {} # Use dict to store highest rating for each problem
                for sub in submissions:
                    if sub.get('verdict') == 'OK':
                        problem = sub['problem']
                        p_id = f"{problem.get('contestId', 'gym')}{problem.get('index')}"
                        rating = problem.get('rating', 0)
                        # Store the highest rating if same problem solved multiple times (rare for OK)
                        if p_id not in solved_problems or rating > solved_problems[p_id]:
                            solved_problems[p_id] = rating
                
                # Calculate quality_sum for the new algorithm
                quality_sum = 0.0
                for rating in solved_problems.values():
                    effective_rating = rating if rating > 0 else 800
                    quality_sum += (effective_rating / 1000.0) ** 2
                
                return {
                    'current_rating': user_data.get('rating', 0),
                    'max_rating': user_data.get('maxRating', 0),
                    'total_solved': len(solved_problems),
                    'cf_quality_sum': quality_sum,
                    'contest_count': 0
                }
        except Exception as e:
            print(f"Error fetching Codeforces: {e}")
        return None

    @staticmethod
    def fetch_codechef(username):
        try:
            url = f"https://www.codechef.com/users/{username}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            rating = soup.find('div', class_='rating-number')
            rating_val = 0
            if rating and rating.text.strip():
                # Remove any '?' or non-digit chars if present
                clean_rating = re.sub(r'[^\d]', '', rating.text)
                if clean_rating:
                    rating_val = int(clean_rating)
            
            max_rating = soup.find('small', string=re.compile(r'Highest Rating'))
            max_rating_val = rating_val
            if max_rating:
                match = re.search(r'\d+', max_rating.text)
                if match:
                    max_rating_val = int(match.group())
            
            # CodeChef solved count is often in h3 within this section
            solved_section = soup.find('section', class_=re.compile(r'solved-questions|problems-solved'))
            solved_count = 0
            if solved_section:
                h3 = solved_section.find('h3', string=re.compile(r'Total Problems Solved', re.I))
                if h3:
                    match = re.search(r'\d+', h3.text)
                    if match:
                        solved_count = int(match.group())
                else:
                    # Fallback: just look for any h3 with numbers in the section
                    all_h3 = solved_section.find_all('h3')
                    for h in all_h3:
                        if 'Total Problems Solved' in h.text:
                            match = re.search(r'\d+', h.text)
                            if match:
                                solved_count = int(match.group())
                                break
            
            # Final fallback: search the whole page for "Total Problems Solved"
            if solved_count == 0:
                full_text_search = soup.find(string=re.compile(r'Total Problems Solved:\s*\d+', re.I))
                if full_text_search:
                    match = re.search(r'\d+', full_text_search)
                    if match:
                        solved_count = int(match.group())
            
            return {
                'current_rating': rating_val,
                'max_rating': max_rating_val,
                'total_solved': solved_count,
                'contest_count': 0
            }
        except Exception as e:
            print(f"Error fetching CodeChef: {e}")
        return None

    @staticmethod
    def fetch_leetcode(username):
        try:
            # Using alfa-leetcode-api
            url = f"https://alfa-leetcode-api.onrender.com/{username}/solved"
            response = requests.get(url, timeout=10).json()
            if 'solvedProblem' in response:
                return {
                    'current_rating': 0,
                    'max_rating': 0,
                    'total_solved': response.get('solvedProblem', 0),
                    'lc_easy': response.get('easySolved', 0),
                    'lc_medium': response.get('mediumSolved', 0),
                    'lc_hard': response.get('hardSolved', 0),
                    'contest_count': 0
                }
        except Exception as e:
            print(f"Error fetching LeetCode: {e}")
        return None

    @staticmethod
    def fetch_atcoder(username):
        try:
            # Rating from profile page
            url = f"https://atcoder.jp/users/{username}"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            rating_tag = soup.find('th', string='Rating')
            rating_val = int(rating_tag.find_next_sibling('td').text) if rating_tag else 0
            
            max_rating_tag = soup.find('th', string='Highest Rating')
            max_rating_val = int(max_rating_tag.find_next_sibling('td').text) if max_rating_tag else rating_val
            
            # Solved count from kenkoooo API
            solved_url = f"https://kenkoooo.com/atcoder/atcoder-api/v2/user_info?user={username}"
            solved_resp = requests.get(solved_url, timeout=10).json()
            solved_count = solved_resp.get('accepted_count', 0)
            
            return {
                'current_rating': rating_val,
                'max_rating': max_rating_val,
                'total_solved': solved_count,
                'contest_count': 0
            }
        except Exception as e:
            print(f"Error fetching AtCoder: {e}")
        return None

    @staticmethod
    def fetch_beecrowd(username):
        # Beecrowd uses a numeric ID for profiles
        # Domain: judge.beecrowd.com
        try:
            url = f"https://judge.beecrowd.com/en/profile/{username}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Referer': 'https://judge.beecrowd.com/'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 403:
                print(f"Beecrowd is blocking the scraper (403 Forbidden).")
                return None
                
            if response.status_code != 200:
                print(f"Beecrowd profile not found for ID: {username} (Status: {response.status_code})")
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors as their UI can be tricky
            solved_count = 0
            solved_li = soup.find('li', title='Solved')
            if solved_li:
                solved_span = solved_li.find('span')
                if solved_span:
                    solved_count = int(solved_span.text.replace(',', '').strip())
            else:
                # Fallback: find by text
                solved_label = soup.find(string=re.compile('Solved'))
                if solved_label:
                    # Often the number is in the next element or parent
                    parent = solved_label.parent
                    match = re.search(r'(\d+)', parent.text)
                    if match:
                        solved_count = int(match.group(1))

            return {
                'current_rating': 0,
                'max_rating': 0,
                'total_solved': solved_count,
                'contest_count': 0
            }
        except Exception as e:
            print(f"Error fetching Beecrowd: {e}")
        return None

def sync_student_stats(student_id):
    accounts = execute_query("""
        SELECT a.*, p.name as platform_name 
        FROM student_cp_accounts a 
        JOIN cp_platforms p ON a.platform_id = p.id 
        WHERE a.student_id = %s
    """, (student_id,))

    for acc in accounts:
        stats = None
        platform = acc['platform_name']
        username = acc['username']
        
        if platform == 'Codeforces':
            stats = CPScraper.fetch_codeforces(username)
        elif platform == 'CodeChef':
            stats = CPScraper.fetch_codechef(username)
        elif platform == 'LeetCode':
            stats = CPScraper.fetch_leetcode(username)
        elif platform == 'AtCoder':
            stats = CPScraper.fetch_atcoder(username)
        elif platform == 'Beecrowd':
            stats = CPScraper.fetch_beecrowd(username)
        
        if stats:
            execute_query("""
                INSERT INTO cp_current_stats (account_id, total_solved, current_rating, max_rating, contest_count, lc_easy, lc_medium, lc_hard, cf_quality_sum)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                total_solved=VALUES(total_solved), current_rating=VALUES(current_rating), 
                max_rating=VALUES(max_rating), contest_count=VALUES(contest_count),
                lc_easy=VALUES(lc_easy), lc_medium=VALUES(lc_medium), lc_hard=VALUES(lc_hard),
                cf_quality_sum=VALUES(cf_quality_sum)
            """, (acc['id'], stats['total_solved'], stats['current_rating'], stats['max_rating'], 
                  stats['contest_count'], stats.get('lc_easy', 0), stats.get('lc_medium', 0), stats.get('lc_hard', 0),
                  stats.get('cf_quality_sum', 0)), commit=True)
            
            execute_query("""
                INSERT INTO cp_history (account_id, total_solved, current_rating, max_rating, contest_count, lc_easy, lc_medium, lc_hard, cf_quality_sum)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (acc['id'], stats['total_solved'], stats['current_rating'], stats['max_rating'], 
                  stats['contest_count'], stats.get('lc_easy', 0), stats.get('lc_medium', 0), stats.get('lc_hard', 0),
                  stats.get('cf_quality_sum', 0)), commit=True)
