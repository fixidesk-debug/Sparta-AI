import pytest
from sqlalchemy import text
import os


@pytest.mark.integration
def test_db_connection(db_url=None):
    import sqlalchemy
    db_url = db_url or os.environ.get('TEST_DATABASE_URL', 'postgresql://sparta:sparta_pass@localhost:5433/sparta_test')
    engine = sqlalchemy.create_engine(db_url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1"))
        assert res.scalar() == 1
