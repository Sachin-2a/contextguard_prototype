import sqlite3
import os

def get_db_path():
    # Ensures database is created safely relative to backend path
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    return os.path.join(os.path.dirname(__file__), 'audit.db')

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS token_vault (token TEXT PRIMARY KEY, real_value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, original TEXT, secured TEXT, actions TEXT, context TEXT)''')
    conn.commit()
    conn.close()

def save_to_vault(token: str, real_value: str):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO token_vault VALUES (?, ?)", (token, real_value))
    conn.commit()
    conn.close()
    
def log_audit(original: str, secured: str, actions: list, context: dict):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("INSERT INTO audit_log (original, secured, actions, context) VALUES (?, ?, ?, ?)", 
              (original, secured, str(actions), str(context)))
    conn.commit()
    conn.close()

# Initialize on import
init_db()
