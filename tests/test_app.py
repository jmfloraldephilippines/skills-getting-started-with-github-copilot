import uuid

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_existing_participant():
    activity_name = "Chess Club"
    email = f"student-{uuid.uuid4().hex}@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    unregister_response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity_name]["participants"]


def test_unregister_missing_participant_returns_not_found():
    activity_name = "Chess Club"
    email = f"missing-{uuid.uuid4().hex}@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found for this activity"
