## Installation
Add the following dependencies to your requirements.txt file:

plaintext
Copy code
Flask==3.1.0
Flask-Bcrypt==0.7.1
mysql-connector-python==8.2.0
PyJWT==2.7.0
pytest==8.3.3
pytest-mock==3.10.0
Install them using:

bash
Copy code
pip install -r requirements.txt
## Configuration
Set the following environment variable:

carhire.db: The URL for the database connection.
API Endpoints
Below is a list of the API endpoints available in the system:

Endpoint	Method	Descriptio
## API Endpoints

| **Endpoint**                     | **Method** | **Description**                                   |
|-----------------------------------|------------|---------------------------------------------------|
| `/api/customer`                  | GET        | List all customers                               |
| `/api/customer/{id}`             | GET        | Retrieve a specific customer                     |
| `/api/customer`                  | POST       | Create a new customer                            |
| `/api/customer/{id}`             | PUT        | Update an existing customer                      |
| `/api/customer/{id}`             | DELETE     | Delete a customer                                |
| `/api/vehicle`                   | GET        | List all vehicles                                |
| `/api/vehicle/{reg_number}`      | GET        | Retrieve a specific vehicle                      |
| `/api/vehicle`                   | POST       | Create a new vehicle                             |
| `/api/vehicle/{reg_number}`      | PUT        | Update an existing vehicle                       |
| `/api/vehicle/{reg_number}`      | DELETE     | Delete a vehicle                                 |
| `/api/booking`                   | GET        | List all bookings                                |
| `/api/booking/{id}`              | GET        | Retrieve a specific booking                      |
| `/api/booking`                   | POST       | Create a new booking                             |
| `/api/booking/{id}`              | PUT        | Update an existing booking                       |
| `/api/booking/{id}`              | DELETE     | Delete a booking                                 |
| `/api/booking_status`            | GET        | List all booking statuses                        |
| `/api/booking_status/{code}`     | GET        | Retrieve a specific booking status               |
| `/api/booking_status`            | POST       | Create a new booking status                      |
| `/api/booking_status/{code}`     | PUT        | Update an existing booking status                |
| `/api/booking_status/{code}`     | DELETE     | Delete a booking status                          |
| `/api/login`                     | POST       | Login to generate a JWT token                    |

## Testing
Prerequisites:
Install all dependencies using pip install -r requirements.txt.
Ensure that the database is running and the required tables are created.
Set the environment variables like DATABASE_URL for database connectivity.
Steps:
Navigate to the project directory where your test files are located.
Run the tests using pytest:
bash
Copy code
pytest --cov=api.py
Verify the output for successful test execution and check code coverage.
Git Commit Guidelines
Follow these standardized commit message formats for clarity and consistency:

## Type	Description	Example
feat	Introduce a new feature	feat: add JWT authentication
fix	Fix a bug or issue	fix: resolve database error
docs	Update documentation	docs: update API endpoints
test	Add or update tests	test: add booking endpoint tests
