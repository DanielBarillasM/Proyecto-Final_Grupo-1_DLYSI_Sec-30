import pytest

from text2sql.sql_safety import UnsafeSQL, validate_read_only_sql


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("```sql\nSELECT id FROM users\n```", "SELECT id FROM users;"),
        (
            "SQL: WITH x AS (SELECT 1 AS n) SELECT n FROM x;",
            "WITH x AS (SELECT 1 AS n) SELECT n FROM x;",
        ),
    ],
)
def test_accepts_single_read_only_query(raw: str, expected: str) -> None:
    assert validate_read_only_sql(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "DELETE FROM users;",
        "DROP TABLE users; SELECT id FROM users;",
        "SELECT id FROM users; DROP TABLE users;",
        "UPDATE users SET name = 'x';",
        "SELECT FROM users;",
        "No puedo responder.",
    ],
)
def test_rejects_unsafe_output(raw: str) -> None:
    with pytest.raises(UnsafeSQL):
        validate_read_only_sql(raw)
