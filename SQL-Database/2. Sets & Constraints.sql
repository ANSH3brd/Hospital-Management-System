
-- List of all people (patients, doctors, and staff) in the hospital.
SELECT Name, 'Patient' AS Role FROM Patient  
UNION  
SELECT Name, 'Doctor' AS Role FROM Doctor  
UNION  
SELECT Name, 'Staff' AS Role FROM Staff;


ALTER TABLE Patient  
MODIFY Blood_Group VARCHAR(5) NOT NULL;

ALTER TABLE Staff
RENAME COLUMN Role to Staff_Role;

ALTER TABLE Doctor  
MODIFY Experience INT NOT NULL;

ALTER TABLE Billing  
MODIFY Total_Amount DECIMAL(10,2) NOT NULL;

ALTER TABLE Doctor  
ADD CONSTRAINT Experience CHECK (Experience >= 0);

ALTER TABLE Billing  
ADD CONSTRAINT Total_Amount CHECK (Total_Amount >= 0);

ALTER TABLE Doctor  
MODIFY Availability_Status ENUM('Available', 'Unavailable') DEFAULT 'Available';

ALTER TABLE Billing  
MODIFY Payment_Status ENUM('Pending', 'Completed') DEFAULT 'Pending';