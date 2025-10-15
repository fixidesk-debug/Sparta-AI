import pytest

from app.services.exec import execute_code_safely
from app.services.code_executor import execute_code


def test_execute_code_basic():
    # Use the synchronous convenience wrapper from code_executor
    res = execute_code('print("done")')
    assert isinstance(res, dict)
    output = res.get('output', '') or ''
    assert 'done' in output


@pytest.mark.asyncio
async def test_execute_code_safely_basic():
    # Async safe executor should run simple python code and capture output
    # db is unused when file_id is None; silence type check with type: ignore
    res = await execute_code_safely('print("hello_async")', language='python', file_id=None, user_id=0, db=None)  # type: ignore
    assert isinstance(res, dict)
    assert 'hello_async' in (res.get('output') or '')
