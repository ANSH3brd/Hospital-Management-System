
-- Doctor Availability & Specialization
CREATE VIEW Available_Doctors AS
SELECT Doctor_ID, Name, Specialization, Availability_Status
FROM Doctor
WHERE Availability_Status = 'Available';

SELECT * FROM Available_Doctors;



-- All Members While Hiding Sensitive Data

CREATE VIEW All_Members_Public AS
SELECT Patient_ID AS ID, Name, Age, Gender, Date_of_Birth, 'Patient' AS Role
FROM Patient
UNION
SELECT Doctor_ID AS ID, Name, Age, Gender, Date_of_Birth, 'Doctor' AS Role
FROM Doctor
UNION
SELECT Staff_ID AS ID, Name, Age, Gender, Date_of_Birth, 'Staff' AS Role
FROM Staff;

SELECT * FROM All_Members_Public;



-- Patient Basic Details & Diagnosed Disease
CREATE VIEW Patient_Diagnosis AS
SELECT P.Patient_ID, P.Name, P.Age, P.Gender, P.Date_of_Birth, P.Contact_Number, MR.Diagnosis
FROM Patient P
INNER JOIN Medical_Record MR ON P.Patient_ID = MR.Patient_ID;

SELECT * FROM Patient_Diagnosis;


-- To view what medicine is prescribed by the doctor to the patient
CREATE VIEW Prescription_Details AS
SELECT 
    p.Name AS Patient_Name,
    d.Name AS Doctor_Name,
    mr.Diagnosis AS Disease_Diagnosed,
    pr.Medicine_Name AS Prescription_Given
FROM Prescription pr
JOIN Patient p ON pr.Patient_ID = p.Patient_ID
JOIN Doctor d ON pr.Doctor_ID = d.Doctor_ID
JOIN Medical_Record mr ON pr.Patient_ID = mr.Patient_ID AND pr.Doctor_ID = mr.Doctor_ID;

SELECT * FROM Prescription_Details;



-- Combines patients, doctors, and their appointments
CREATE VIEW Patient_Doctor_Appointments AS
SELECT 
    p.Name AS Patient_Name,
    d.Name AS Doctor_Name,
    a.Appointment_Date,
    a.Appointment_Time,
    a.Status
FROM Appointment a
JOIN Patient p ON a.Patient_ID = p.Patient_ID
JOIN Doctor d ON a.Doctor_ID = d.Doctor_ID
WHERE a.Status = 'Scheduled';

SELECT * FROM Patient_Doctor_Appointments;

