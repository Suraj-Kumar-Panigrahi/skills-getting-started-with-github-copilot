from src.app import activities


class TestRootAndActivities:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        request_options = {"follow_redirects": False}

        # Act
        response = client.get("/", **request_options)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_static_index_is_available(self, client):
        # Arrange
        path = "/static/index.html"

        # Act
        response = client.get(path)

        # Assert
        assert response.status_code == 200
        assert "Mergington High School" in response.text

    def test_get_activities_returns_activity_details(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert expected_activity in response.json()
        assert response.json()[expected_activity]["participants"] == [
            "michael@mergington.edu",
            "daniel@mergington.edu",
        ]


class TestSignup:
    def test_signup_adds_participant(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "student@example.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in activities[activity_name]["participants"]

    def test_duplicate_signup_is_rejected(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "student@example.com"
        client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        assert activities[activity_name]["participants"].count(email) == 1

    def test_signup_for_unknown_activity_returns_not_found(self, client):
        # Arrange
        activity_name = "Unknown Activity"
        email = "student@example.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_without_email_returns_validation_error(self, client):
        # Arrange
        activity_name = "Art Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422


class TestUnregister:
    def test_unregister_removes_participant(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "student@example.com"
        activities[activity_name]["participants"].append(email)

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in activities[activity_name]["participants"]

    def test_unregister_from_unknown_activity_returns_not_found(self, client):
        # Arrange
        activity_name = "Unknown Activity"
        email = "student@example.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregistering_nonparticipant_returns_not_found(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "student@example.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Student is not signed up for this activity"
        )

    def test_unregister_without_email_returns_validation_error(self, client):
        # Arrange
        activity_name = "Art Club"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422
