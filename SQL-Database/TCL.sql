-- Manually Stopping Auto-Commit
SET autocommit = 0;


-- Start a new transaction
START TRANSACTION;

INSERT INTO Patient
VALUES (100, 'John Doe', 'Male', '1985-06-15', 40, '1234567890', '123 Main St', 'john.doe@example.com', 'A+', 'None', 'None');

SELECT * FROM hospital_db.patient;

-- First Savepoint sp1
SAVEPOINT sp1;

DELETE FROM Billing
WHERE Bill_ID = 209;

SELECT * FROM hospital_db.billing;

-- Second Savepoint sp2
SAVEPOINT sp2;

UPDATE Doctor
SET Availability_Status = 'Unavailable'
WHERE Doctor_ID = 69;

SELECT * FROM hospital_db.doctor;


-- Rollback Commands 
ROLLBACK;

ROLLBACK TO sp1;

ROLLBACK TO sp2;


COMMIT;


SET autocommit = 1;
