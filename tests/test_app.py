import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def quote_name(name: str) -> str:
    return quote(name, safe="")


def setup_function():
    # Arrange: save original activities state
    global _original_activities
    _original_activities = copy.deepcopy(activities)


def teardown_function():
    # Assert/Teardown: restore original state after each test
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


def test_get_activities_returns_all_activities():
    # Arrange
    expected = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected in data
    assert isinstance(data[expected]["participants"], list)


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity = "Chess Club"
    email = "teststudent@mergington.edu"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.post(f"/activities/{quote_name(activity)}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_delete_participant_removes_existing_participant():
    # Arrange
    activity = "Programming Class"
    email = "emma@mergington.edu"
    assert email in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{quote_name(activity)}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity]["participants"]

    # Act
    response = client.post(f"/activities/{quote_name(activity)}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_returns_404_for_missing_participant():
    # Arrange
    activity = "Soccer Team"
    email = "missing@mergington.edu"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{quote_name(activity)}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
