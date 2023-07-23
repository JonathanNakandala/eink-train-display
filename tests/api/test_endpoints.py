"""
Test Endpoints
"""
import json
from datetime import timedelta
from starlette.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_update_dashboard():
    """
    Test Update Dashboard
    """
    response = client.post("/schedule/update")
    assert response.status_code == 200
    assert response.json() == {"message": "Dashboard update scheduled"}


def test_update_config():
    """
    Test Update Frequency
    """
    new_config = {"interval_minutes": 10}
    response = client.post("/schedule/config", data=json.dumps(new_config))
    assert response.status_code == 200
    expected_response = {
        "message": "Dashboard update frequency updated",
        "current_interval": timedelta(minutes=10),  # replace with initial value
        "new_interval": 10,
    }
    assert response.json() == expected_response


def test_departures_to_dashboard():
    """
    Test HTML Output Endpoint
    """
    response = client.get("/departures_to_dashboard")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "date" in response.json()
    assert "nationalRail" in response.json()
    assert "weather" in response.json()
