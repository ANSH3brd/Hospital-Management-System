
-- Appointment Details with Patient and Doctor Names
SELECT A.Appointment_ID, P.Name AS Patient_Name, D.Name AS Doctor_Name, 
       A.Appointment_Date, A.Appointment_Time, A.Status
FROM Appointment A
INNER JOIN Patient P ON A.Patient_ID = P.Patient_ID
INNER JOIN Doctor D ON A.Doctor_ID = D.Doctor_ID;


-- All Patients with Their Doctors and Bills
SELECT P.Name AS Patient_Name, D.Name AS Doctor_Name, 
       B.Bill_ID, B.Total_Amount, B.Payment_Status
FROM Patient P
INNER JOIN Appointment A ON P.Patient_ID = A.Patient_ID
INNER JOIN Doctor D ON A.Doctor_ID = D.Doctor_ID
INNER JOIN Billing B ON A.Appointment_ID = B.Appointment_ID;


-- Complete Medical Records with Patient and Doctor Information
SELECT MR.Record_ID, P.Name AS Patient_Name, D.Name AS Doctor_Name, 
       MR.Diagnosis, MR.Treatment_Details, MR.Visit_Date
FROM Medical_Record MR
INNER JOIN Patient P ON MR.Patient_ID = P.Patient_ID
INNER JOIN Doctor D ON MR.Doctor_ID = D.Doctor_ID;


-- List All Persons with Age & Date of Birth
SELECT P.Patient_ID AS ID, P.Name, P.Age, P.Date_of_Birth, 'Patient' AS Role
FROM Patient P
UNION
SELECT D.Doctor_ID AS ID, D.Name, D.Age, D.Date_of_Birth, 'Doctor' AS Role
FROM Doctor D
UNION
SELECT S.Staff_ID AS ID, S.Name, S.Age, S.Date_of_Birth, 'Staff' AS Role
FROM Staff S;

