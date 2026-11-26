
import sqlite3
from pathlib import Path
from contextlib import contextmanager


# ==========================================
# DATABASE PATHS
# ==========================================

# Backend root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Knowledge Base directory
KB_DIR = BASE_DIR / "knowledge_base"
UPLOAD_DIR = KB_DIR / "uploads"

# Existing SQLite database
DB_PATH = KB_DIR / "knowledge.db"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# DATABASE CONNECTION
# ==========================================

@contextmanager
def get_db():
    """
    Provides a database connection.
    Automatically commits changes and closes the connection.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def initialize_database():
    """
    Creates the Knowledge Base table if it doesn't exist.
    Existing records are preserved.
    """

    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


# Initialize database
initialize_database()
