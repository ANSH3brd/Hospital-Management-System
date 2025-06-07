CREATE TABLE Patient (
    Patient_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Gender ENUM('Male', 'Female', 'Other') NOT NULL,
    Date_of_Birth DATE NOT NULL,
    Age INT,
    Contact_Number VARCHAR(15) UNIQUE NOT NULL,
    Address TEXT,
    Email VARCHAR(100) UNIQUE,
    Blood_Group VARCHAR(5),
    Medical_History TEXT,
    Insurance_Details TEXT
);


CREATE TABLE Doctor (
    Doctor_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Gender ENUM('Male', 'Female', 'Other') NOT NULL,
    Date_of_Birth DATE NOT NULL,
    Age INT,
    Contact_Number VARCHAR(15) UNIQUE NOT NULL,
    Address TEXT,
    Email VARCHAR(100) UNIQUE,
    Specialization VARCHAR(100) NOT NULL,
    Qualifications TEXT,
    Experience INT,
    Availability_Status ENUM('Available', 'Unavailable') NOT NULL,
    Department_ID INT
);


CREATE TABLE Staff (
    Staff_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Gender ENUM('Male', 'Female', 'Other') NOT NULL,
    Date_of_Birth DATE NOT NULL,
    Age INT,
    Contact_Number VARCHAR(15) UNIQUE NOT NULL,
    Address TEXT,
    Email VARCHAR(100) UNIQUE,
    Role VARCHAR(100) NOT NULL,
    Shift_Timing VARCHAR(50)
);


CREATE TABLE Appointment (
    Appointment_ID INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID INT,
    Doctor_ID INT,
    Appointment_Date DATE NOT NULL,
    Appointment_Time TIME NOT NULL,
    Status ENUM('Scheduled', 'Completed', 'Cancelled') NOT NULL,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID),
    FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID)
);

CREATE TABLE Medical_Record (
    Record_ID INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID INT,
    Doctor_ID INT,
    Diagnosis TEXT,
    Treatment_Details TEXT,
    Visit_Date DATE NOT NULL,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID),
    FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID)
);


CREATE TABLE Prescription (
    Prescription_ID INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID INT,
    Doctor_ID INT,
    Medicine_Name TEXT NOT NULL,
    Dosage VARCHAR(50) NOT NULL,
    Frequency VARCHAR(50) NOT NULL,
    Prescription_Date DATE NOT NULL,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID),
    FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID)
);


CREATE TABLE Billing (
    Bill_ID INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID INT,
    Appointment_ID INT,
    Total_Amount DECIMAL(10,2) NOT NULL,
    Payment_Status ENUM('Pending', 'Completed') NOT NULL,
    Bill_Date DATE NOT NULL,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID),
    FOREIGN KEY (Appointment_ID) REFERENCES Appointment(Appointment_ID)
);

-- Backup table for deleted Patients
CREATE TABLE Updated_Patient (
    Patient_ID INT PRIMARY KEY,
    Name VARCHAR(100),
    Gender ENUM('Male', 'Female', 'Other'),
    Date_of_Birth DATE,
    Age INT,
    Contact_Number VARCHAR(15),
    Address TEXT,
    Email VARCHAR(100),
    Blood_Group VARCHAR(5),
    Medical_History TEXT,
    Insurance_Details TEXT,
    Deleted_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE Deleted_Patient;
DROP TABLE Deleted_Doctor;

-- Backup table for deleted Doctors
CREATE TABLE Updated_Doctor (
    Doctor_ID INT PRIMARY KEY,
    Name VARCHAR(100),
    Gender ENUM('Male', 'Female', 'Other'),
    Date_of_Birth DATE,
    Age INT,
    Contact_Number VARCHAR(15),
    Address TEXT,
    Email VARCHAR(100),
    Specialization VARCHAR(100),
    Qualifications TEXT,
    Experience INT,
    Availability_Status ENUM('Available', 'Unavailable'),
    Department_ID INT,
    Deleted_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Backup table for deleted Staff members
CREATE TABLE Deleted_Staff (
    Staff_ID INT PRIMARY KEY,
    Name VARCHAR(100),
    Gender ENUM('Male', 'Female', 'Other'),
    Date_of_Birth DATE,
    Age INT,
    Contact_Number VARCHAR(15),
    Address TEXT,
    Email VARCHAR(100),
    Staff_Role VARCHAR(100),
    Shift_Timing VARCHAR(50),
    Deleted_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);





CREATE INDEX idx_patient_contact ON Patient(Contact_Number);
CREATE INDEX idx_doctor_contact ON Doctor(Contact_Number);
CREATE INDEX idx_staff_contact ON Staff(Contact_Number);


SELECT * FROM hospital_db.appointment;

SELECT * FROM hospital_db.billing;

SELECT * FROM hospital_db.doctor;

SELECT * FROM hospital_db.medical_record;

SELECT * FROM hospital_db.patient;

SELECT * FROM hospital_db.prescription;

SELECT * FROM hospital_db.staff;

SELECT * FROM hospital_db.deleted_staff;

SELECT * FROM hospital_db.updated_doctor;

SELECT * FROM hospital_db.updated_patient;