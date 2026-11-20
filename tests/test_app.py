import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    activities = {
        "Robotics Club": {
            "description": "Build and program robots",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 12,
            "participants": ["existing@school.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == {
        "Robotics Club": {
            "description": "Build and program robots",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 12,
            "participants": ["existing@school.edu"],
        }
    }


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Robotics Club/signup",
        params={"email": "new@school.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new@school.edu for Robotics Club"
    }
    assert client.get("/activities").json()["Robotics Club"]["participants"] == [
        "existing@school.edu",
        "new@school.edu",
    ]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Robotics Club/signup",
        params={"email": "existing@school.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new@school.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Robotics Club/participants",
        params={"email": "existing@school.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@school.edu from Robotics Club"
    }
    assert client.get("/activities").json()["Robotics Club"]["participants"] == []


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        "/activities/Robotics Club/participants",
        params={"email": "missing@school.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not registered for this activity"
    }


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "existing@school.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
