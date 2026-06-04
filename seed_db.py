from database.db_manager import execute_query

def seed_data():
    print("Seeding Departments...")
    depts = [
        ('Computer Science and Engineering', 'CSE'),
        ('Information and Communication Technology', 'ICT'),
        ('Textile Engineering', 'TE'),
        ('Software Engineering', 'SE'),
        ('Electrical and Electronic Engineering', 'EEE')
    ]
    for name, code in depts:
        execute_query("INSERT IGNORE INTO departments (name, short_code) VALUES (%s, %s)", (name, code), commit=True)

    print("Seeding Batches...")
    batches = [15, 16, 17, 18, 19, 20]
    for b in batches:
        execute_query("INSERT IGNORE INTO batches (batch_number) VALUES (%s)", (b,), commit=True)
        
    print("Seeding CP Platforms...")
    platforms = [
        ('Codeforces', 'https://codeforces.com/api/'),
        ('CodeChef', 'https://www.codechef.com/'),
        ('AtCoder', 'https://atcoder.jp/'),
        ('LeetCode', 'https://leetcode.com/'),
        ('Beecrowd', 'https://www.beecrowd.com.br/')
    ]
    for name, url in platforms:
        execute_query("INSERT IGNORE INTO cp_platforms (name, api_base_url) VALUES (%s, %s)", (name, url), commit=True)

    print("Seeding complete!")

if __name__ == "__main__":
    seed_data()
