import uuid
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


INITIAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture()
def client():
    app_module.activities = deepcopy(INITIAL_ACTIVITIES)
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_seed_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_participant(client):
    activity_name = "Chess Club"
    email = f"student-{uuid.uuid4().hex}@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity_name]["participants"]


def test_duplicate_signup_returns_bad_request(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_existing_participant(client):
    activity_name = "Chess Club"
    email = f"student-{uuid.uuid4().hex}@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    unregister_response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity_name]["participants"]


def test_unregister_missing_participant_returns_not_found(client):
    activity_name = "Chess Club"
    email = f"missing-{uuid.uuid4().hex}@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found for this activity"
