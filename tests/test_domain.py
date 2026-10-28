import pytest
from backend.money import parse_salary, format_salary
from backend.seed import seed_database
from backend.db import connect, init_db


@pytest.mark.parametrize("value,minor", [("1",100),("1.20",120),("123456.78",12345678)])
def test_valid_salary_exact_integer_minor_units(value, minor):
    assert parse_salary(value) == minor
    assert parse_salary(format_salary(minor)) == minor


@pytest.mark.parametrize("value", ["0", "-1", "1.234", "1e3", "nan", "1 000", "", "9999999999999"])
def test_invalid_salary_values(value):
    with pytest.raises(ValueError):
        parse_salary(value)


def test_seed_is_deterministic_and_idempotent(tmp_path):
    path = tmp_path / "seed.db"
    init_db(path)
    assert seed_database(path, count=100) == 100
    with connect(path) as conn:
        before = conn.execute("SELECT employee_code,full_name,salary_minor FROM employees ORDER BY id").fetchall()
    assert seed_database(path, count=100) == 0
    with connect(path) as conn:
        after = conn.execute("SELECT employee_code,full_name,salary_minor FROM employees ORDER BY id").fetchall()
    assert [tuple(x) for x in before] == [tuple(x) for x in after]
