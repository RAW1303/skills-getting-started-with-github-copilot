import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state after each test"""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


class TestGetActivities:
    def test_get_activities_success(self, client):
        # Arrange - client fixture provides TestClient

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "description" in data["Chess Club"]
        assert "participants" in data["Chess Club"]


class TestSignup:
    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]


class TestDeleteSignup:
    def test_delete_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        # First sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert email not in activities[activity_name]["participants"]

    def test_delete_signup_activity_not_found(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_delete_signup_not_signed_up(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notsignedup@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]


# Parametrized tests for multiple activities
@pytest.mark.parametrize("activity_name", ["Chess Club", "Programming Class", "Gym Class"])
class TestSignupParametrized:
    def test_signup_success_parametrized(self, client, activity_name):
        # Arrange
        email = "paramtest@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]