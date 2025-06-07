# Hospital Management System

A full-stack web application for managing hospital operations including patients, doctors, appointments, medical records, prescriptions, and billing.

## Features

- **Patient Management**: Register and manage patient information
- **Doctor Management**: Manage doctors and their specializations
- **Appointment Scheduling**: Schedule and track patient appointments
- **Medical Records**: Maintain patient medical history
- **Prescription Management**: Generate and manage prescriptions
- **Billing System**: Create bills and track payments

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python Flask
- **Database**: MySQL
- **Authentication**: Session-based authentication

## Requirements

- Python 3.8+
- MySQL Server
- Web Browser (Chrome, Firefox, Safari, Edge)

## Installation and Setup

1. **Clone the repository**
   ```
   git clone https://github.com/yourusername/hospital-management-system.git
   cd hospital-management-system
   ```

2. **Set up a virtual environment (optional but recommended)**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set up the database**
   - Create a MySQL database named `HospitalManagementSystem`
   - Import the database schema from the SQL file located in the DBMS folder

5. **Configure the application**
   - Open `app.py` and update the MySQL configuration:
     ```python
     app.config['MYSQL_HOST'] = 'localhost'
     app.config['MYSQL_USER'] = 'your_mysql_username'
     app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
     app.config['MYSQL_DB'] = 'HospitalManagementSystem'
     ```

6. **Run the application**
   ```
   python app.py
   ```

7. **Access the application**
   Open your web browser and navigate to `http://localhost:5000`

## Usage

1. **Login to the system**
   - Use a patient ID and password from the Patient_Login table

2. **Navigate the dashboard**
   - View summary statistics and recent activities

3. **Manage patients**
   - Add, view, edit, and delete patient records

4. **Manage doctors**
   - Add, view, edit, and delete doctor records

5. **Schedule appointments**
   - Create and manage patient appointments with doctors

6. **Create and manage medical records**
   - Record patient diagnoses and treatments

7. **Generate prescriptions**
   - Create and manage prescriptions for patients

8. **Process bills**
   - Generate bills for appointments and track payments

## Directory Structure

```
HospitalManagementSystem/
├── models/              # Database models
├── routes/              # Route handlers
├── static/              # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── img/
├── templates/           # HTML templates
├── app.py               # Main application file
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Database Schema

The database consists of the following main tables:
- Patient
- Doctor
- Appointment
- Medical_Record
- Prescription
- Billing

Refer to the SQL files in the DBMS folder for the complete schema.

## License

This project is licensed under the MIT License.

## Contributors

- Ansh


## Acknowledgements

