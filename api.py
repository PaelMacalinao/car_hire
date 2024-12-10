import re
from datetime import datetime
from flask import Flask, jsonify, request
from http import HTTPStatus
import mysql.connector
from conn import DB_CONFIG

app = Flask(__name__)

# Function to establish the database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# My Customer CRUD
@app.route("/api/customer", methods=["GET"])
def get_customers():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customer")
        customers = cursor.fetchall()
        return jsonify({"success": True, "data": customers, "total": len(customers)}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/customer/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customer WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"success": False, "error": "Customer not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "data": customer}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/customer", methods=["POST"])
def create_customer():
    data = request.get_json()

    if not data or not data.get("customer_name") or not data.get("email_address") or not data.get("phone_number"):
        return jsonify({"success": False, "error": "customer_name, email_address, and phone_number are required"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customer (customer_name, email_address, phone_number, address) VALUES (%s, %s, %s, %s)",
            (data["customer_name"], data["email_address"], data["phone_number"], data.get("address", ""))
        )
        conn.commit()
        new_customer_id = cursor.lastrowid
        return jsonify({"success": True, "data": {"customer_id": new_customer_id, **data}}), HTTPStatus.CREATED
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/customer/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customer SET customer_name = %s, email_address = %s, phone_number = %s, address = %s WHERE customer_id = %s",
            (data["customer_name"], data["email_address"], data["phone_number"], data.get("address", ""), customer_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Customer not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "message": "Customer updated successfully"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/customer/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customer WHERE customer_id = %s", (customer_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Customer not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "message": f"Customer with ID {customer_id} has been deleted"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# My Vehicle CRUD
@app.route("/api/vehicle", methods=["GET"])
def get_vehicles():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vehicle")
        vehicles = cursor.fetchall()
        return jsonify({"success": True, "data": vehicles, "total": len(vehicles)}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/vehicle/<string:reg_number>", methods=["GET"])
def get_vehicle(reg_number):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vehicle WHERE reg_number = %s", (reg_number,))
        vehicle = cursor.fetchone()
        if not vehicle:
            return jsonify({"success": False, "error": "Vehicle not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "data": vehicle}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/vehicle", methods=["POST"])
def create_vehicle():
    data = request.get_json()

    if not data or not data.get("reg_number") or not data.get("model_code") or not data.get("vehicle_category_description"):
        return jsonify({"success": False, "error": "reg_number, model_code, and vehicle_category_description are required"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vehicle (reg_number, model_code, current_mileage, engine_size, vehicle_category_description) VALUES (%s, %s, %s, %s, %s)",
            (data["reg_number"], data["model_code"], data.get("current_mileage", 0), data.get("engine_size", 0), data["vehicle_category_description"])
        )
        conn.commit()
        return jsonify({"success": True, "data": data}), HTTPStatus.CREATED
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/api/vehicle/<string:reg_number>", methods=["PUT"])
def update_vehicle(reg_number):
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE vehicle SET model_code = %s, vehicle_category_description = %s, current_mileage = %s, engine_size = %s WHERE reg_number = %s",
            (data["model_code"], data["vehicle_category_description"], data["current_mileage"], data["engine_size"], reg_number)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Vehicle not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "message": "Vehicle updated successfully"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/vehicle/<string:reg_number>", methods=["DELETE"])
def delete_vehicle(reg_number):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vehicle WHERE reg_number = %s", (reg_number,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Vehicle not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "message": f"Vehicle with reg_number {reg_number} has been deleted"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# My Booking CRUD
@app.route("/api/booking", methods=["GET"])
def get_bookings():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM booking")
        bookings = cursor.fetchall()
        return jsonify({"success": True, "data": bookings, "total": len(bookings)}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking/<int:booking_id>", methods=["GET"])
def get_booking(booking_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM booking WHERE booking_id = %s", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            return jsonify({"success": False, "error": "Booking not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "data": booking}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking", methods=["POST"])
def create_booking():
    data = request.get_json()
    if not data or not data.get("Customer_customer_id") or not data.get("Vehicle_reg_number") or not data.get("date_from") or not data.get("date_to") or not data.get("booking_status_status_code"):
        return jsonify({"success": False, "error": "Customer_customer_id, Vehicle_reg_number, date_from, date_to, and booking_status_status_code are required"}), HTTPStatus.BAD_REQUEST

    if not is_valid_date(data["date_from"]) or not is_valid_date(data["date_to"]):
        return jsonify({"success": False, "error": "Invalid date format. Expected YYYY-MM-DD"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO booking (date_from, date_to, Customer_customer_id, booking_status_status_code, Vehicle_reg_number) VALUES (%s, %s, %s, %s, %s)",
            (data["date_from"], data["date_to"], data["Customer_customer_id"], data["booking_status_status_code"], data["Vehicle_reg_number"])
        )
        conn.commit()
        new_booking_id = cursor.lastrowid
        return jsonify({"success": True, "data": {"booking_id": new_booking_id, **data}}), HTTPStatus.CREATED
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking/<int:booking_id>", methods=["PUT"])
def update_booking(booking_id):
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE booking SET date_from = %s, date_to = %s, Customer_customer_id = %s, booking_status_status_code = %s, Vehicle_reg_number = %s WHERE booking_id = %s",
            (data["date_from"], data["date_to"], data["Customer_customer_id"], data["booking_status_status_code"], data["Vehicle_reg_number"], booking_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Booking not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "message": "Booking updated successfully"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking/<int:booking_id>", methods=["DELETE"])
def delete_booking(booking_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM booking WHERE booking_id = %s", (booking_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Booking not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "message": f"Booking with ID {booking_id} has been deleted"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
# Booking Status CRUD
@app.route("/api/booking_status", methods=["GET"])
def get_booking_statuses():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM booking_status")
        booking_statuses = cursor.fetchall()
        return jsonify({"success": True, "data": booking_statuses, "total": len(booking_statuses)}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking_status/<string:booking_status_code>", methods=["GET"])
def get_booking_status(booking_status_code):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM booking_status WHERE booking_status_code = %s", (booking_status_code,))
        booking_status = cursor.fetchone()
        if not booking_status:
            return jsonify({"success": False, "error": "Booking status not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "data": booking_status}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking_status", methods=["POST"])
def create_booking_status():
    data = request.get_json()

    if not data or not data.get("booking_status_code") or not data.get("booking_status_description"):
        return jsonify({"success": False, "error": "booking_status_code and booking_status_description are required"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO booking_status (booking_status_code, booking_status_description) VALUES (%s, %s)",
            (data["booking_status_code"], data["booking_status_description"])
        )
        conn.commit()
        return jsonify({"success": True, "data": data}), HTTPStatus.CREATED
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking_status/<string:booking_status_code>", methods=["PUT"])
def update_booking_status(booking_status_code):
    data = request.get_json()

    if not data or not data.get("booking_status_description"):
        return jsonify({"success": False, "error": "booking_status_description is required"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE booking_status SET booking_status_description = %s WHERE booking_status_code = %s",
            (data["booking_status_description"], booking_status_code)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Booking status not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "message": "Booking status updated successfully"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking_status/<string:booking_status_code>", methods=["DELETE"])
def delete_booking_status(booking_status_code):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM booking_status WHERE booking_status_code = %s", (booking_status_code,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Booking status not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "message": f"Booking status with code {booking_status_code} has been deleted"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
