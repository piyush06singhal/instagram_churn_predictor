import sqlite3
import hashlib
import json
from datetime import datetime
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path='database/instagram_churn.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Engagement data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS engagement_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                followers_count INTEGER,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                saves INTEGER,
                reach INTEGER,
                impressions INTEGER,
                engagement_rate REAL,
                posting_gap_days INTEGER,
                follower_change INTEGER,
                competitor_avg_engagement REAL,
                post_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                churn_probability REAL,
                risk_category TEXT,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password):
        """Create new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return {'success': True, 'user_id': user_id, 'message': 'User created successfully'}
        except sqlite3.IntegrityError as e:
            conn.close()
            return {'success': False, 'message': 'Username or email already exists'}
        except Exception as e:
            conn.close()
            return {'success': False, 'message': str(e)}
    
    def authenticate_user(self, username, password):
        """Authenticate user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute(
            'SELECT user_id, username, email FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'success': True,
                'user_id': user[0],
                'username': user[1],
                'email': user[2]
            }
        else:
            return {'success': False, 'message': 'Invalid credentials'}
    
    def save_engagement_data(self, user_id, data):
        """Save engagement data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO engagement_data 
                (user_id, followers_count, likes, comments, shares, saves, reach, 
                impressions, engagement_rate, posting_gap_days, follower_change, 
                competitor_avg_engagement, post_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('followers_count'),
                data.get('likes'),
                data.get('comments'),
                data.get('shares'),
                data.get('saves'),
                data.get('reach'),
                data.get('impressions'),
                data.get('engagement_rate'),
                data.get('posting_gap_days'),
                data.get('follower_change'),
                data.get('competitor_avg_engagement'),
                data.get('post_type')
            ))
            conn.commit()
            data_id = cursor.lastrowid
            conn.close()
            return {'success': True, 'data_id': data_id}
        except Exception as e:
            conn.close()
            return {'success': False, 'message': str(e)}
    
    def save_prediction(self, user_id, churn_probability, risk_category):
        """Save prediction result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO predictions (user_id, churn_probability, risk_category)
                VALUES (?, ?, ?)
            ''', (user_id, churn_probability, risk_category))
            conn.commit()
            conn.close()
            return {'success': True}
        except Exception as e:
            conn.close()
            return {'success': False, 'message': str(e)}
    
    def get_user_engagement_history(self, user_id):
        """Get user's engagement history"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT * FROM engagement_data WHERE user_id = ? ORDER BY created_at DESC',
            conn,
            params=(user_id,)
        )
        conn.close()
        return df
    
    def get_user_predictions(self, user_id):
        """Get user's prediction history"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT * FROM predictions WHERE user_id = ? ORDER BY prediction_date DESC',
            conn,
            params=(user_id,)
        )
        conn.close()
        return df

if __name__ == "__main__":
    # Test database
    db = DatabaseManager()
    
    # Test user creation
    result = db.create_user('testuser', 'test@example.com', 'password123')
    print(result)
