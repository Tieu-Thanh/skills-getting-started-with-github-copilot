import copy
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


def setup_function():
    # Backup activities state before each test
    app_module._activities_backup = copy.deepcopy(app_module.activities)


def teardown_function():
    # Restore activities state after each test
    app_module.activities = app_module._activities_backup
    del app_module._activities_backup


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity checks
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_duplicate():
    email = "tester@example.com"
    activity = "Chess Club"

    # Sign up first time
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    j = resp.json()
    assert "Signed up" in j["message"]

    # Signing up again should fail with 400
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister():
    email = "to_remove@example.com"
    activity = "Programming Class"

    # Ensure the user is signed up first
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200

    # Now unregister
    resp2 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp2.status_code == 200
    assert resp2.json()["message"].startswith("Unregistered")

    # Trying to unregister again should return 404
    resp3 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp3.status_code == 404
