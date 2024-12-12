import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from api import app

@pytest.fixture
def client():
    """Flask test client fixture."""
    with app.test_client() as client:
        yield client

@patch("api.get_db_connection")
def test_get_customers_success(mock_db, client):
    """Test fetching all customers with a successful response."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [{"customer_id": 1, "name": "John Doe"}]
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get("/api/customer")
    assert response.status_code == 200
    assert response.json["success"]
    assert len(response.json["data"]) == 1

@patch("api.get_db_connection")
def test_get_customer_not_found(mock_db, client):
    """Test fetching a specific customer that does not exist."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get("/api/customer/999")
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Customer not found" in response.json["error"]

@patch("api.get_db_connection")
def test_create_customer_invalid_payload(mock_db, client):
    """Test creating a customer with invalid payload."""
    response = client.post("/api/customer", json={"email_address": "test@example.com"})
    assert response.status_code == 400
    assert not response.json["success"]
    assert "customer_name" in response.json["error"]

@patch("api.get_db_connection")
def test_create_customer_success(mock_db, client):
    """Test successful creation of a customer."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 123
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post("/api/customer", json={
        "customer_name": "Jane Doe",
        "email_address": "jane@example.com",
        "phone_number": "123456789"
    })
    assert response.status_code == 201
    assert response.json["success"]
    assert response.json["data"]["customer_id"] == 123

@patch("api.get_db_connection")
def test_update_customer_not_found(mock_db, client):
    """Test updating a non-existent customer."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 0
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.put("/api/customer/999", json={
        "customer_name": "Updated Name",
        "email_address": "updated@example.com",
        "phone_number": "987654321"
    })
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Customer not found" in response.json["error"]

@patch("api.get_db_connection")
def test_delete_customer_success(mock_db, client):
    """Test successful deletion of a customer."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 1
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.delete("/api/customer/1")
    assert response.status_code == 200
    assert response.json["success"]

@patch("api.get_db_connection")
def test_delete_customer_not_found(mock_db, client):
    """Test deleting a non-existent customer."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 0
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.delete("/api/customer/999")
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Customer not found" in response.json["error"]

# -----------------------------------
# Vehicle Tests
# -----------------------------------

@patch("api.get_db_connection")
def test_get_vehicles_success(mock_db, client):
    """Test fetching all vehicles with a successful response."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [{"reg_number": "ABC123", "model_code": "SUV2023"}]
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get("/api/vehicle")
    assert response.status_code == 200
    assert response.json["success"]
    assert len(response.json["data"]) == 1

@patch("api.get_db_connection")
def test_get_vehicle_not_found(mock_db, client):
    """Test fetching a specific vehicle that does not exist."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get("/api/vehicle/INVALID")
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Vehicle not found" in response.json["error"]

@patch("api.get_db_connection")
def test_create_vehicle_success(mock_db, client):
    """Test successful creation of a vehicle."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post("/api/vehicle", json={
        "reg_number": "XYZ123",
        "model_code": "SEDAN2023",
        "current_mileage": 12000,
        "engine_size": 2000,
        "vehicle_category_description": "Sedan"
    })
    assert response.status_code == 201
    assert response.json["success"]

@patch("api.get_db_connection")
def test_update_vehicle_not_found(mock_db, client):
    """Test updating a non-existent vehicle."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 0
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.put("/api/vehicle/INVALID", json={
        "model_code": "SEDAN2023",
        "current_mileage": 15000,
        "engine_size": 2500,
        "vehicle_category_description": "Luxury Sedan"
    })
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Vehicle not found" in response.json["error"]
    
@patch("api.get_db_connection")
def test_delete_vehicle_success(mock_db, client):
    """Test successful deletion of a vehicle."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 1  
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.delete("/api/vehicle/XYZ123")
    assert response.status_code == 200
    assert response.json["success"]
    assert "Vehicle with reg_number XYZ123 has been deleted" in response.json["message"]

@patch("api.get_db_connection")
def test_delete_vehicle_not_found(mock_db, client):
    """Test deleting a non-existent vehicle."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 0  
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.delete("/api/vehicle/INVALID")
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Vehicle not found" in response.json["error"]

# -----------------------------------
# Booking Tests
# -----------------------------------

@patch("api.get_db_connection")
def test_get_bookings_success(mock_db, client):
    """Test fetching all bookings with a successful response."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [{"booking_id": 1, "date_from": "2023-01-01", "date_to": "2023-01-10"}]
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get("/api/booking")
    assert response.status_code == 200
    assert response.json["success"]
    assert len(response.json["data"]) == 1

@patch("api.get_db_connection")
def test_create_booking_success(mock_db, client):
    """Test successful creation of a booking."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 5
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post("/api/booking", json={
        "Customer_customer_id": 1,
        "Vehicle_reg_number": "ABC123",
        "date_from": "2023-01-01",
        "date_to": "2023-01-10",
        "booking_status_booking_status_code": "CONFIRMED"
    })
    assert response.status_code == 201
    assert response.json["success"]

@patch("api.get_db_connection")
def test_get_booking_not_found(mock_db, client):
    """Test fetching a specific booking that does not exist."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get("/api/booking/999")
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Booking not found" in response.json["error"]
    
@patch("api.get_db_connection")
def test_update_booking_success(mock_db, client):
    """Test successful update of a booking."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 1  
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.put("/api/booking/1", json={
        "date_from": "2023-02-01",
        "date_to": "2023-02-10",
        "Customer_customer_id": 1,
        "Vehicle_reg_number": "ABC123",
        "booking_status_booking_status_code": "COMPLETED"
    })
    assert response.status_code == 200
    assert response.json["success"]
    assert "Booking updated successfully" in response.json["message"]

@patch("api.get_db_connection")
def test_update_booking_not_found(mock_db, client):
    """Test updating a non-existent booking."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 0  
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.put("/api/booking/999", json={
        "date_from": "2023-02-01",
        "date_to": "2023-02-10",
        "Customer_customer_id": 1,
        "Vehicle_reg_number": "ABC123",
        "booking_status_booking_status_code": "COMPLETED"
    })
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Booking not found" in response.json["error"]

@patch("api.get_db_connection")
def test_delete_booking_success(mock_db, client):
    """Test successful deletion of a booking."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 1  
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.delete("/api/booking/1")
    assert response.status_code == 200
    assert response.json["success"]
    assert "Booking with ID 1 has been deleted" in response.json["message"]

@patch("api.get_db_connection")
def test_delete_booking_not_found(mock_db, client):
    """Test deleting a non-existent booking."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 0  
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.delete("/api/booking/999")
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Booking not found" in response.json["error"]

# -----------------------------------
# Booking Status Tests
# -----------------------------------

@patch("api.get_db_connection")
def test_get_booking_statuses_success(mock_db, client):
    """Test fetching all booking statuses."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [{"booking_status_code": "CONFIRMED", "description": "Booking Confirmed"}]
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get("/api/booking_status")
    assert response.status_code == 200
    assert response.json["success"]

@patch("api.get_db_connection")
def test_create_booking_status_success(mock_db, client):
    """Test creating a new booking status."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post("/api/booking_status", json={
        "booking_status_code": "PENDING",
        "booking_status_description": "Pending Approval"
    })
    assert response.status_code == 201
    assert response.json["success"]


@patch("api.get_db_connection")
def test_create_booking_status_success(mock_db, client):
    """Test creating a new booking status."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post("/api/booking_status", json={
        "booking_status_code": "PENDING",
        "booking_status_description": "Pending Approval"
    })
    assert response.status_code == 201
    assert response.json["success"]
    assert response.json["data"]["booking_status_code"] == "PENDING"
    assert response.json["data"]["booking_status_description"] == "Pending Approval"

#add update
@patch("api.get_db_connection")
def test_update_booking_status_success(mock_db, client):
    """Test successful update of a booking status."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 1  
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.put("/api/booking_status/CONFIRMED", json={
        "booking_status_description": "Booking Completed"
    })
    assert response.status_code == 200
    assert response.json["success"]
    assert "Booking status updated successfully" in response.json["message"]
    
@patch("api.get_db_connection")
def test_update_booking_status_not_found(mock_db, client):
    """Test updating a non-existent booking status."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 0  
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.put("/api/booking_status/INVALID", json={
        "booking_status_description": "Invalid Status"
    })
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Booking status not found" in response.json["error"]

#add delete

@patch("api.get_db_connection")
def test_delete_booking_status_success(mock_db, client):
    """Test successful deletion of a booking status."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 1 
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.delete("/api/booking_status/CONFIRMED")
    assert response.status_code == 200
    assert response.json["success"]
    assert "Booking status with code CONFIRMED has been deleted" in response.json["message"]

@patch("api.get_db_connection")
def test_delete_booking_status_not_found(mock_db, client):
    """Test deleting a non-existent booking status."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 0  
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.delete("/api/booking_status/INVALID")
    assert response.status_code == 404
    assert not response.json["success"]
    assert "Booking status not found" in response.json["error"]

if __name__ == "__main__":
    pytest.main()