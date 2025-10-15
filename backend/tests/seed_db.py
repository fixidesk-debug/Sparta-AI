# Simple DB seeder for integration tests
import os
import time
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.exc import OperationalError


DATABASE_URL = os.environ.get('TEST_DATABASE_URL', 'postgresql://sparta:sparta_pass@localhost:5433/sparta_test')
ADMIN_DATABASE_URL = os.environ.get('TEST_ADMIN_DATABASE_URL', 'postgresql://sparta:sparta_pass@localhost:5433/postgres')


def ensure_database_exists(target_db_url: str, admin_db_url: str, timeout: int = 60):
    """Ensure the target database exists by connecting to the admin DB and creating it if needed."""
    # Parse target db name
    from urllib.parse import urlparse

    parsed = urlparse(target_db_url)
    target_db_name = parsed.path.lstrip('/')

    admin_engine = sqlalchemy.create_engine(admin_db_url)
    start = time.time()
    while True:
        try:
            with admin_engine.connect() as conn:
                # Check if database exists
                res = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :name"), {'name': target_db_name})
                if res.scalar() is None:
                    conn.execute(text(f"CREATE DATABASE \"{target_db_name}\""))
                return
        except OperationalError:
            if time.time() - start > timeout:
                raise
            time.sleep(1)


def seed():
    # Ensure database exists
    ensure_database_exists(DATABASE_URL, ADMIN_DATABASE_URL)

    engine = sqlalchemy.create_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT);"))
        conn.execute(text("INSERT INTO users (username, password_hash) VALUES ('seeduser', 'hash') ON CONFLICT DO NOTHING;"))


if __name__ == '__main__':
    seed()
