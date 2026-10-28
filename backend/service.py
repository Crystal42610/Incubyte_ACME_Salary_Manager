"""Domain services separated from HTTP concerns for straightforward testing."""
import sqlite3
from backend.db import connect
from backend.money import format_salary, parse_salary
from backend.seed import COUNTRIES, DEPARTMENTS


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


CURRENCY_CODES = sorted({country[1] for country in COUNTRIES})
SORT_COLUMNS = {"employee_code": "employee_code", "full_name": "full_name", "salary": "salary_minor", "department": "department", "country": "country_code"}


def employee_out(row):
    data = dict(row)
    data["salary"] = format_salary(data.pop("salary_minor"))
    return data


def get_employee(employee_id: int):
    with connect() as conn:
        row = conn.execute("SELECT * FROM employees WHERE id=?", (employee_id,)).fetchone()
    if row is None:
        raise NotFound("Employee not found")
    return employee_out(row)


def directory(q: str = "", country: str = "", department: str = "", page: int = 1, page_size: int = 25, sort: str = "employee_code", direction: str = "asc"):
    criteria, params = [], []
    if q.strip():
        criteria.append("(full_name LIKE ? OR email LIKE ? OR employee_code LIKE ?)")
        like = f"%{q.strip()[:100]}%"
        params.extend([like] * 3)
    if country:
        criteria.append("country_code = ?")
        params.append(country)
    if department:
        criteria.append("department = ?")
        params.append(department)
    where = " WHERE " + " AND ".join(criteria) if criteria else ""
    order = SORT_COLUMNS[sort]
    order_dir = "ASC" if direction == "asc" else "DESC"
    with connect() as conn:
        count = conn.execute("SELECT count(*) FROM employees" + where, params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM employees{where} ORDER BY {order} {order_dir}, id ASC LIMIT ? OFFSET ?",
            (*params, page_size, (page - 1) * page_size),
        ).fetchall()
    return {"items": [employee_out(row) for row in rows], "total": count, "page": page, "page_size": page_size}


def edit_salary(employee_id: int, salary: str, reason: str, expected_version: int, actor: str):
    minor = parse_salary(salary)
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            row = conn.execute("SELECT * FROM employees WHERE id=?", (employee_id,)).fetchone()
            if row is None:
                raise NotFound("Employee not found")
            if row["version"] != expected_version:
                raise Conflict("Salary changed since you opened this record. Refresh and review the latest value.")
            if row["salary_minor"] == minor:
                conn.commit()  # No-op: do not create redundant audit events.
                return employee_out(row)
            conn.execute("""UPDATE employees SET salary_minor=?,version=version+1,
                   updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?""", (minor, employee_id))
            conn.execute("""INSERT INTO salary_changes
                (employee_id,old_salary_minor,new_salary_minor,currency,reason,changed_by)
                VALUES (?,?,?,?,?,?)""",
                (employee_id, row["salary_minor"], minor, row["currency"], reason.strip(), actor))
            updated = conn.execute("SELECT * FROM employees WHERE id=?", (employee_id,)).fetchone()
            conn.commit()
            return employee_out(updated)
        except Exception:
            conn.rollback()
            raise


def history(employee_id: int):
    with connect() as conn:
        if conn.execute("SELECT id FROM employees WHERE id=?", (employee_id,)).fetchone() is None:
            raise NotFound("Employee not found")
        rows = conn.execute("""SELECT id,old_salary_minor,new_salary_minor,currency,reason,changed_by,changed_at
            FROM salary_changes WHERE employee_id=? ORDER BY id DESC LIMIT 100""", (employee_id,)).fetchall()
    return [{"id": r["id"], "old_salary": format_salary(r["old_salary_minor"]),
             "new_salary": format_salary(r["new_salary_minor"]), "currency": r["currency"],
             "reason": r["reason"], "changed_by": r["changed_by"], "changed_at": r["changed_at"]} for r in rows]


def _round_ratio(total: int, count: int) -> int:
    """Half-up rounding to the closest minor unit, without any float conversion."""
    return (2 * total + count) // (2 * count)


def _median_minor(sorted_amounts: list[int]) -> int:
    n = len(sorted_amounts)
    return sorted_amounts[n // 2] if n % 2 else (sorted_amounts[n // 2 - 1] + sorted_amounts[n // 2] + 1) // 2


def _group(conn, column, currency):
    rows = conn.execute(f"""SELECT {column} AS label, COUNT(*) AS headcount,
                 SUM(salary_minor) AS salary_sum FROM employees
                 WHERE currency=? GROUP BY {column} ORDER BY headcount DESC, label ASC""", (currency,)).fetchall()
    return [{"label": r["label"], "headcount": r["headcount"],
             "average": format_salary(_round_ratio(r["salary_sum"], r["headcount"]))} for r in rows]


def analytics(currency: str):
    with connect() as conn:
        salaries = [r[0] for r in conn.execute("SELECT salary_minor FROM employees WHERE currency=? ORDER BY salary_minor", (currency,)).fetchall()]
        by_country = _group(conn, "country_code", currency)
        by_department = _group(conn, "department", currency)
    n = len(salaries)
    return {"currency": currency, "headcount": n,
            "average": format_salary(_round_ratio(sum(salaries), n)) if n else None,
            "median": format_salary(_median_minor(salaries)) if n else None,
            "minimum": format_salary(salaries[0]) if n else None,
            "maximum": format_salary(salaries[-1]) if n else None,
            "by_country": by_country, "by_department": by_department}


def metadata():
    with connect() as conn:
        count = conn.execute("SELECT count(*) FROM employees").fetchone()[0]
    return {"countries": sorted({c[0] for c in COUNTRIES}), "departments": list(DEPARTMENTS),
            "currencies": CURRENCY_CODES, "total": count}
