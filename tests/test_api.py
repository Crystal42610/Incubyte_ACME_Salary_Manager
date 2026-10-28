from tests.conftest import get_first


def test_public_health_but_private_hr_data(api):
    assert api.get("/api/health").status_code == 200
    assert api.get("/api/employees", auth=None).status_code == 401
    assert api.get("/api/analytics?currency=EUR", auth=("wrong", "wrong")).status_code == 401


def test_seed_and_directory_search_pagination(api):
    data = api.get("/api/employees?page=1&page_size=25").json()
    assert data["total"] == 120
    assert len(data["items"]) == 25
    second = api.get("/api/employees?page=2&page_size=25").json()
    assert not set(x["employee_code"] for x in data["items"]) & set(x["employee_code"] for x in second["items"])
    found = api.get("/api/employees?q=EMP-00042").json()
    assert found["total"] == 1
    assert found["items"][0]["employee_code"] == "EMP-00042"


def test_filtering_and_sorting_are_allowlisted(api):
    assert api.get("/api/employees?sort=employee_code%3Bdelete%20from%20employees").status_code == 422
    filtered = api.get("/api/employees?country=HU&department=Engineering").json()
    assert all(x["country_code"] == "HU" and x["department"] == "Engineering" for x in filtered["items"])


def test_salary_change_is_audited_and_versioned(api):
    employee = get_first(api)
    new_salary = "82000.75"
    saved = api.patch(f"/api/employees/{employee['id']}/salary", json={
        "salary": new_salary, "reason": "Approved compensation adjustment", "expected_version": employee["version"]
    })
    assert saved.status_code == 200, saved.text
    assert saved.json()["salary"] == new_salary
    assert saved.json()["version"] == employee["version"] + 1
    history = api.get(f"/api/employees/{employee['id']}/history").json()
    assert len(history) == 1
    assert history[0]["old_salary"] == employee["salary"]
    assert history[0]["new_salary"] == new_salary
    assert history[0]["reason"] == "Approved compensation adjustment"
    assert history[0]["changed_by"] == "test-hr"


def test_stale_edit_returns_conflict_without_extra_audit(api):
    employee = get_first(api)
    url = f"/api/employees/{employee['id']}/salary"
    body = {"salary": "43000.00", "reason": "Annual review", "expected_version": employee["version"]}
    assert api.patch(url, json=body).status_code == 200
    assert api.patch(url, json={**body, "salary": "44000.00"}).status_code == 409
    assert len(api.get(f"/api/employees/{employee['id']}/history").json()) == 1


def test_invalid_salary_and_reason_are_rejected(api):
    employee = get_first(api)
    url = f"/api/employees/{employee['id']}/salary"
    for value in ["0", "-10", "10.999", "NaN", "1e3", "", "100000000000000000000"]:
        resp = api.patch(url, json={"salary": value, "reason": "Annual review", "expected_version": employee["version"]})
        assert resp.status_code == 422, (value, resp.text)
    assert api.patch(url, json={"salary": "50000.00", "reason": "", "expected_version": employee["version"]}).status_code == 422
    assert api.get(f"/api/employees/{employee['id']}/history").json() == []


def test_repeat_salary_value_is_idempotent(api):
    employee = get_first(api)
    body = {"salary": employee["salary"], "reason": "Checked with finance", "expected_version": employee["version"]}
    response = api.patch(f"/api/employees/{employee['id']}/salary", json=body)
    assert response.status_code == 200
    assert response.json()["version"] == employee["version"]
    assert api.get(f"/api/employees/{employee['id']}/history").json() == []


def test_analytics_are_currency_scoped(api):
    data = api.get("/api/analytics?currency=EUR").json()
    assert data["currency"] == "EUR"
    assert data["headcount"] >= 1
    assert data["headcount"] == sum(x["headcount"] for x in data["by_country"])
    assert data["headcount"] == sum(x["headcount"] for x in data["by_department"])
    assert float(data["minimum"]) <= float(data["median"]) <= float(data["maximum"])
    assert api.get("/api/analytics?currency=INVALID").status_code == 422


def test_unknown_employee_returns_404(api):
    assert api.get("/api/employees/999999").status_code == 404
    assert api.patch("/api/employees/999999/salary", json={"salary":"100.00","reason":"Annual review","expected_version":1}).status_code == 404
