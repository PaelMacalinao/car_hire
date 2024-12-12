import re
from datetime import datetime
from flask import Flask, jsonify, request, g
from http import HTTPStatus
import mysql.connector
import jwt
from functools import wraps
from conn import DB_CONFIG

# JWT Secret Key (should be an environment variable in production)
JWT_SECRET = "paeeel"

app = Flask(__name__)

# Function to establish the database connection
# use this if can't connect in database 
# ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password'; FLUSH PRIVILEGES;

def get_db_connection():
    try:
        return mysql.connector.connect(
            **DB_CONFIG,
            auth_plugin='mysql_native_password'
        )
    except mysql.connector.Error as err:
        raise Exception(f"Database connection error: {err}")

# Validate date format
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# JWT Authentication Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith("Bearer "):
            return jsonify({"success": False, "error": "Token is missing or malformed!"}), HTTPStatus.UNAUTHORIZED
        try:
            token = token.split(" ")[1] 
            g.user = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "error": "Token has expired!"}), HTTPStatus.UNAUTHORIZED
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "error": "Invalid token!"}), HTTPStatus.UNAUTHORIZED
        return f(*args, **kwargs)
    return decorated

# Role-Based Access Control Decorator
def requires_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user.get('role') != role:
                return jsonify({"success": False, "error": "Access denied!"}), HTTPStatus.FORBIDDEN
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# --------------------------------------------
# Login
# --------------------------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "admin123":
        token = jwt.encode({"username": username, "role": "admin"}, JWT_SECRET, algorithm="HS256")
        return jsonify({"success": True, "token": token})
    return jsonify({"success": False, "error": "Invalid credentials!"}), HTTPStatus.UNAUTHORIZED

# index
@app.route("/")
def hello_world():
    return """
    <h1>WELCOME TO MY CAR HIRE SITE!</h1>
    <p>You are currently on the main page of the CARHIRE Database API.</p>
    <ul>
        <li><a href="/api/vehicle">Vehicle</a></li>
    </ul>
    <p>Use the provided routes to interact with the API. Ensure to use valid authentication tokens when necessary.</p>
    """
    
# --------------------------------------------
# Customer Routes with JWT Authentication
# --------------------------------------------

@app.route("/api/customer", methods=["GET"])
@token_required
@requires_role("admin")
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
@token_required
@requires_role("admin")
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
@token_required
@requires_role("admin")
def create_customer():
    data = request.get_json()
    if not data or not data.get("customer_name") or not data.get("email_address"):
        return jsonify({"success": False, "error": "customer_name and email_address are required"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customer (customer_name, email_address, phone_number, address) VALUES (%s, %s, %s, %s)",
            (data["customer_name"], data["email_address"], data.get("phone_number", ""), data.get("address", ""))
        )
        conn.commit()
        return jsonify({"success": True, "message": "Customer created successfully"}), HTTPStatus.CREATED
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@app.route("/api/customer/<int:customer_id>", methods=["PUT"])
@token_required
@requires_role("admin")
def update_customer(customer_id):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the customer exists
        cursor.execute("SELECT * FROM customer WHERE customer_id = %s", (customer_id,))
        if not cursor.fetchone():
            return jsonify({"success": False, "error": "Customer not found"}), HTTPStatus.NOT_FOUND

        # Update the customer
        update_fields = []
        values = []

        if "customer_name" in data:
            update_fields.append("customer_name = %s")
            values.append(data["customer_name"])
        if "email_address" in data:
            update_fields.append("email_address = %s")
            values.append(data["email_address"])
        if "phone_number" in data:
            update_fields.append("phone_number = %s")
            values.append(data["phone_number"])
        if "address" in data:
            update_fields.append("address = %s")
            values.append(data["address"])

        if not update_fields:
            return jsonify({"success": False, "error": "No valid fields provided to update"}), HTTPStatus.BAD_REQUEST

        values.append(customer_id)
        update_query = f"UPDATE customer SET {', '.join(update_fields)} WHERE customer_id = %s"
        cursor.execute(update_query, values)
        conn.commit()

        return jsonify({"success": True, "message": f"Customer with ID {customer_id} updated successfully"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()            


@app.route("/api/customer/<int:customer_id>", methods=["DELETE"])
@token_required
@requires_role("admin")
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

# --------------------------------------------
# Booking Routes with JWT Authentication
# --------------------------------------------

@app.route("/api/booking", methods=["GET"])
@token_required
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
@token_required
@requires_role("admin")
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
@token_required
def create_booking():
    data = request.get_json()
    if not data or not data.get("Customer_customer_id") or not data.get("Vehicle_reg_number") or not is_valid_date(data.get("date_from")) or not is_valid_date(data.get("date_to")):
        return jsonify({"success": False, "error": "Invalid booking data"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO booking (Customer_customer_id, Vehicle_reg_number, date_from, date_to, booking_status_code) VALUES (%s, %s, %s, %s, %s)",
            (data["Customer_customer_id"], data["Vehicle_reg_number"], data["date_from"], data["date_to"], data.get("booking_status_code", "PENDING"))
        )
        conn.commit()
        return jsonify({"success": True, "message": "Booking created successfully"}), HTTPStatus.CREATED
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking/<int:booking_id>", methods=["PUT"])
@token_required
def update_booking(booking_id):
    data = request.get_json()
    if not data or not data.get("date_from") or not data.get("date_to") or not is_valid_date(data.get("date_from")) or not is_valid_date(data.get("date_to")):
        return jsonify({"success": False, "error": "Invalid booking data"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE booking SET date_from = %s, date_to = %s, booking_status_code = %s WHERE booking_id = %s",
            (data["date_from"], data["date_to"], data.get("booking_status_code", "PENDING"), booking_id)
        )
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Booking not found"}), HTTPStatus.NOT_FOUND
        conn.commit()
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
@token_required
def delete_booking(booking_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM booking WHERE booking_id = %s", (booking_id,))
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Booking not found"}), HTTPStatus.NOT_FOUND
        conn.commit()
        return jsonify({"success": True, "message": "Booking deleted successfully"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --------------------------------------------
# Booking Status Routes with JWT Authentication
# --------------------------------------------

@app.route("/api/booking_status", methods=["GET"])
@token_required
def get_booking_statuses():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM booking_status")
        statuses = cursor.fetchall()
        return jsonify({"success": True, "data": statuses, "total": len(statuses)}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn: 
            conn.close()
            
@app.route("/api/booking_status/<int:booking_status_code>", methods=["GET"])
@token_required
@requires_role("admin")
def get_booking_status(booking_status_code):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM booking_status WHERE booking_status_code = %s", (booking_status_code,))
        status = cursor.fetchone()
        if not status:
            return jsonify({"success": False, "error": "Booking status not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"success": True, "data": status}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/api/booking_status", methods=["POST"])
@token_required
def create_booking_status():
    data = request.get_json()
    if not data or not data.get("status_code") or not data.get("description"):
        return jsonify({"success": False, "error": "Invalid booking status data"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO booking_status (status_code, description) VALUES (%s, %s)",
            (data["status_code"], data["description"])
        )
        conn.commit()
        return jsonify({"success": True, "message": "Booking status created successfully"}), HTTPStatus.CREATED
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking_status/<string:status_code>", methods=["PUT"])
@token_required
def update_booking_status(status_code):
    data = request.get_json()
    if not data or not data.get("description"):
        return jsonify({"success": False, "error": "Invalid booking status data"}), HTTPStatus.BAD_REQUEST

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE booking_status SET description = %s WHERE status_code = %s",
            (data["description"], status_code)
        )
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Booking status not found"}), HTTPStatus.NOT_FOUND
        conn.commit()
        return jsonify({"success": True, "message": "Booking status updated successfully"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/booking_status/<string:status_code>", methods=["DELETE"])
@token_required
def delete_booking_status(status_code):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM booking_status WHERE status_code = %s", (status_code,))
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Booking status not found"}), HTTPStatus.NOT_FOUND
        conn.commit()
        return jsonify({"success": True, "message": "Booking status deleted successfully"}), HTTPStatus.OK
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --------------------------------------------
# Vehicle Status Routes without JWT Authentication
# --------------------------------------------

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
            
            
if __name__ == "__main__":
    app.run(debug=True)