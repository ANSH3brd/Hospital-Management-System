
-- Doctor Availability Before Scheduling an Appointment
DELIMITER //
CREATE TRIGGER check_doctor_availability
BEFORE INSERT ON Appointment
FOR EACH ROW
BEGIN
    DECLARE doctor_status ENUM('Available', 'Unavailable');
    
    SELECT Availability_Status INTO doctor_status 
    FROM Doctor 
    WHERE Doctor_ID = NEW.Doctor_ID;
    
    IF doctor_status = 'Unavailable' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error: Doctor is unavailable for appointments.';
    END IF;
END;
//
DELIMITER ;


-- Trigger for Deleted Patient Records
DROP TRIGGER Backup_Deleted_Patient;
DELIMITER //
CREATE TRIGGER Backup_Deleted_Patient
BEFORE UPDATE ON Patient
FOR EACH ROW
BEGIN
    INSERT INTO Updated_Patient 
    (Patient_ID, Name, Gender, Date_of_Birth, Age, Contact_Number, Address, Email, Blood_Group, Medical_History, Insurance_Details, Deleted_At)
    VALUES 
    (OLD.Patient_ID, OLD.Name, OLD.Gender, OLD.Date_of_Birth, OLD.Age, OLD.Contact_Number, OLD.Address, OLD.Email, OLD.Blood_Group, OLD.Medical_History, OLD.Insurance_Details, NOW());
END;
//
DELIMITER ;



-- Trigger for Update Doctor Records

DELIMITER //
CREATE TRIGGER Backup_Deleted_Doctor
BEFORE UPDATE ON Doctor
FOR EACH ROW
BEGIN
    INSERT INTO Updated_Doctor 
    (Doctor_ID, Name, Gender, Date_of_Birth, Age, Contact_Number, Address, Email, Specialization, Qualifications, Experience, Availability_Status, Department_ID, Deleted_At)
    VALUES 
    (OLD.Doctor_ID, OLD.Name, OLD.Gender, OLD.Date_of_Birth, OLD.Age, OLD.Contact_Number, OLD.Address, OLD.Email, OLD.Specialization, OLD.Qualifications, OLD.Experience, OLD.Availability_Status, OLD.Department_ID, NOW());
END;
//
DELIMITER ;



-- Trigger for Deleted Staff Records

DELIMITER //
CREATE TRIGGER Backup_Deleted_Staff
AFTER DELETE ON Staff
FOR EACH ROW
BEGIN
    INSERT INTO Deleted_Staff 
    (Staff_ID, Name, Gender, Date_of_Birth, Age, Contact_Number, Address, Email, Staff_Role, Shift_Timing, Deleted_At)
    VALUES 
    (OLD.Staff_ID, OLD.Name, OLD.Gender, OLD.Date_of_Birth, OLD.Age, OLD.Contact_Number, OLD.Address, OLD.Email, OLD.Staff_Role, OLD.Shift_Timing, NOW());
END;
//
DELIMITER ;


-- Check_Bill_Amount
DELIMITER //

CREATE TRIGGER Check_Bill_Amount
BEFORE INSERT ON Billing
FOR EACH ROW
BEGIN
    -- Check if the bill amount is less than or equal to zero
    IF NEW.Total_Amount <= 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error: Bill amount must be positive.';
    END IF;
END;
//

DELIMITER ;







SELECT * FROM Patient;
UPDATE Patient SET Name = 'Vinay Mehta' WHERE Patient_ID = 94;
SELECT * FROM Updated_Patient;



SELECT * FROM Doctor;
UPDATE Doctor SET Name = 'Amresh Kant' WHERE Doctor_ID = 78;
SELECT * FROM Updated_Doctor;



SELECT * FROM Staff;
DELETE FROM Staff WHERE Staff_ID = 505;
SELECT * FROM Deleted_Staff;


INSERT INTO Billing (Patient_ID, Appointment_ID, Total_Amount, Payment_Status, Bill_Date)
VALUES (95, 1001, 10000, 'Completed', '2025-04-01');

INSERT INTO Billing (Patient_ID, Appointment_ID, Total_Amount, Payment_Status, Bill_Date)
VALUES (95, 1001, -500, 'Pending', '2025-04-01');
