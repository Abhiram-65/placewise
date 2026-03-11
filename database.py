import sqlite3
import hashlib
import os
import datetime
import json

DB_NAME = "users.db"

def init_db():
    """Initialize the database with users and predictions tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT,
            roll_no TEXT,
            leetcode_solved INTEGER DEFAULT 0,
            hackerrank_score INTEGER DEFAULT 0,
            internal_score INTEGER DEFAULT 0
        )
    ''')
    
    # Predictions Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp DATETIME,
            cgpa REAL,
            backlogs INTEGER,
            internships INTEGER,
            coding_rating INTEGER,
            aptitude_score INTEGER,
            predicted_category TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    
    # Companies Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            min_cgpa REAL,
            required_skills TEXT -- Stored as JSON string
        )
    ''')
    
    # Internal Coding Questions Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS internal_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            difficulty TEXT,
            points INTEGER
        )
    ''')

    # Skill Resources Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS skill_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill TEXT NOT NULL,
            week INTEGER NOT NULL,
            topic TEXT NOT NULL,
            resources TEXT -- JSON string with links and descriptions
        )
    ''')
    
    # Student Skills Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS student_skills (
            username TEXT PRIMARY KEY,
            skills TEXT, -- Stored as JSON string
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    
    # Create default admin if not exists
    c.execute("SELECT * FROM users WHERE role='admin'")
    if not c.fetchone():
        create_user("admin", "admin123", "admin", "Administrator", "ADMIN001")
    
    # Migration: Add new columns to users table if they don't exist
    c.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in c.fetchall()]
    if "leetcode_solved" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN leetcode_solved INTEGER DEFAULT 0")
    if "hackerrank_score" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN hackerrank_score INTEGER DEFAULT 0")
    if "internal_score" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN internal_score INTEGER DEFAULT 0")
        
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_user(username, password, role, name=None, roll_no=None):
    """Create a new user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, role, name, roll_no) VALUES (?, ?, ?, ?, ?)",
                  (username, hash_password(password), role, name, roll_no))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    """Verify user credentials."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password, role, name, roll_no FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result and result[0] == hash_password(password):
        return {"role": result[1], "name": result[2], "roll_no": result[3]}
    return None

def update_user_profile(username, name, roll_no, password=None):
    """Update user personal details."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        if password:
            c.execute("UPDATE users SET name=?, roll_no=?, password=? WHERE username=?",
                      (name, roll_no, hash_password(password), username))
        else:
            c.execute("UPDATE users SET name=?, roll_no=? WHERE username=?",
                      (name, roll_no, username))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False
    finally:
        conn.close()

def save_prediction(username, cgpa, backlogs, internships, coding_rating, aptitude_score, predicted_category):
    """Save a prediction record."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.datetime.now()
    c.execute('''
        INSERT INTO predictions (username, timestamp, cgpa, backlogs, internships, coding_rating, aptitude_score, predicted_category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, timestamp, cgpa, backlogs, internships, coding_rating, aptitude_score, predicted_category))
    conn.commit()
    conn.close()

def get_student_history(username):
    """Get prediction history for a specific student."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM predictions WHERE username=? ORDER BY timestamp DESC", (username,))
    cols = [description[0] for description in c.description]
    data = c.fetchall()
    conn.close()
    
    history = []
    for row in data:
        history.append(dict(zip(cols, row)))
    return history

def get_all_student_data():
    """Get all prediction data (latest per student) for admin dashboard."""
    conn = sqlite3.connect(DB_NAME)
    query = '''
    SELECT 
        u.name as Name, 
        u.roll_no as Roll_No,
        u.username,
        p.cgpa as CGPA, 
        p.backlogs as Backlogs, 
        p.internships as Internship_Count, 
        p.coding_rating as Coding_Rating, 
        p.aptitude_score as Aptitude_Score, 
        p.predicted_category as Predicted_Category,
        p.timestamp
    FROM predictions p
    JOIN users u ON p.username = u.username
    '''
    import pandas as pd
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- NEW FUNCTIONS FOR ADVANCED FEATURES ---

def add_company(name, min_cgpa, skills_dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO companies (company_name, min_cgpa, required_skills) VALUES (?, ?, ?)",
              (name, min_cgpa, json.dumps(skills_dict)))
    conn.commit()
    conn.close()

def get_all_companies():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM companies")
    cols = [d[0] for d in c.description]
    data = c.fetchall()
    conn.close()
    
    companies = []
    for row in data:
        company = dict(zip(cols, row))
        company['required_skills'] = json.loads(company['required_skills'])
        companies.append(company)
    return companies

def delete_company(company_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM companies WHERE id=?", (company_id,))
    conn.commit()
    conn.close()

def save_student_skills(username, skills_dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO student_skills (username, skills) VALUES (?, ?)",
              (username, json.dumps(skills_dict)))
    conn.commit()
    conn.close()

def get_student_skills(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT skills FROM student_skills WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}

def get_leaderboard_data():
    """Calculates placement readiness score for leaderboard."""
    conn = sqlite3.connect(DB_NAME)
    
    # Get latest prediction per student
    query = '''
    SELECT 
        u.name, 
        u.username,
        p.cgpa, 
        p.coding_rating, 
        p.aptitude_score
    FROM users u
    JOIN predictions p ON u.username = p.username
    WHERE p.id IN (SELECT MAX(id) FROM predictions GROUP BY username)
    AND u.role = 'student'
    '''
    import pandas as pd
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        conn.close()
        return df

    # Simple Score Calculation: (CGPA * 10) + (Coding * 10) + Aptitude
    # Max possible: 100 + 50 + 100 = 250 -> Scale to 100
    df['Readiness_Score'] = ((df['cgpa'] * 10) + (df['coding_rating'] * 10) + df['aptitude_score']) / 2.5
    df = df.sort_values(by='Readiness_Score', ascending=False)
    
    conn.close()
    return df

def update_student_coding_stats(username, leetcode, hackerrank):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET leetcode_solved=?, hackerrank_score=? WHERE username=?",
              (leetcode, hackerrank, username))
    conn.commit()
    conn.close()

def update_internal_score(username, points):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET internal_score = internal_score + ? WHERE username=?",
              (points, username))
    conn.commit()
    conn.close()

def get_student_coding_data(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT leetcode_solved, hackerrank_score, internal_score FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"leetcode": row[0], "hackerrank": row[1], "internal": row[2]}
    return {"leetcode": 0, "hackerrank": 0, "internal": 0}

def add_internal_question(title, description, difficulty, points):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO internal_questions (title, description, difficulty, points) VALUES (?, ?, ?, ?)",
              (title, description, difficulty, points))
    conn.commit()
    conn.close()

def get_internal_questions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM internal_questions")
    cols = [d[0] for d in c.description]
    data = c.fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in data]

def add_skill_resource(skill, week, topic, resources_json):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO skill_resources (skill, week, topic, resources) VALUES (?, ?, ?, ?)",
              (skill, week, topic, resources_json))
    conn.commit()
    conn.close()

def get_skill_resources(skill):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM skill_resources WHERE skill=? ORDER BY week ASC", (skill,))
    cols = [d[0] for d in c.description]
    data = c.fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in data]

def delete_skill_resource(resource_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM skill_resources WHERE id=?", (resource_id,))
    conn.commit()
    conn.close()

def get_skill_averages():
    """Calculates average scores for each skill across all students."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT skills FROM student_skills")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return {}
    
    total_skills = {}
    count = len(rows)
    
    for row in rows:
        skills = json.loads(row[0])
        for skill, val in skills.items():
            total_skills[skill] = total_skills.get(skill, 0) + val
            
    averages = {skill: round(val / count, 1) for skill, val in total_skills.items()}
    return averages

