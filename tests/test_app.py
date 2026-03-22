"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test cases for GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test successful retrieval of all activities"""
        response = client.get("/activities")

        assert response.status_code == 200
        data = response.json()

        # Verify we get a dictionary with activity names as keys
        assert isinstance(data, dict)
        assert len(data) > 0

        # Check that we have some expected activities
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in data

        # Verify structure of activity data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # Use an activity that exists
        activity_name = "Chess Club"
        email = "test@example.com"

        # Get initial participant count
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data[activity_name]["participants"])

        # Sign up
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify participant was added
        response = client.get("/activities")
        updated_data = response.json()
        updated_count = len(updated_data[activity_name]["participants"])
        assert updated_count == initial_count + 1
        assert email in updated_data[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistentActivity/signup",
            params={"email": "test@example.com"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self, client):
        """Test signup when student is already signed up"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # This email is already in the participants

        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]


class TestRemoveParticipant:
    """Test cases for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant_success(self, client):
        """Test successful removal of a participant"""
        activity_name = "Gym Class"
        email = "john@mergington.edu"  # This email exists in participants

        # Get initial participant count
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data[activity_name]["participants"])

        # Remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify participant was removed
        response = client.get("/activities")
        updated_data = response.json()
        updated_count = len(updated_data[activity_name]["participants"])
        assert updated_count == initial_count - 1
        assert email not in updated_data[activity_name]["participants"]

    def test_remove_participant_activity_not_found(self, client):
        """Test removal from non-existent activity"""
        response = client.delete(
            "/activities/NonExistentActivity/participants",
            params={"email": "test@example.com"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_remove_participant_not_found(self, client):
        """Test removal of participant not in activity"""
        activity_name = "Chess Club"
        email = "nonexistent@example.com"

        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Student not found in activity" in data["detail"]


class TestRootEndpoint:
    """Test cases for GET / endpoint"""

    def test_root_endpoint_exists(self, client):
        """Test that root endpoint exists"""
        response = client.get("/")

        # The endpoint should return some successful response
        # (may be 200 if static file is served, or redirect status)
        assert response.status_code in [200, 301, 302, 307, 308]