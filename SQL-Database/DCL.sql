CREATE USER 'admin_user'@'localhost' IDENTIFIED BY 'admin_pass';
CREATE USER 'doctor_user'@'localhost' IDENTIFIED BY 'doc_pass';
CREATE USER 'receptionist_user'@'localhost' IDENTIFIED BY 'rec_pass';



-- Admin – Full Access
GRANT ALL PRIVILEGES ON hospital_db.* TO 'admin_user'@'localhost';


-- Doctor – Read Patient, Write Prescription
GRANT SELECT ON hospital_db.Patient TO 'doctor_user'@'localhost';
GRANT SELECT, INSERT ON hospital_db.Prescription TO 'doctor_user'@'localhost';


--  Receptionist – Manage Appointments and Billing
GRANT SELECT, INSERT, UPDATE ON hospital_db.Appointment TO 'receptionist_user'@'localhost';
GRANT SELECT, INSERT ON hospital_db.Billing TO 'receptionist_user'@'localhost';


FLUSH PRIVILEGES;



SELECT user, host FROM mysql.user;

SHOW GRANTS FOR 'doctor_user'@'localhost';
SHOW GRANTS FOR 'admin_user'@'localhost';
SHOW GRANTS FOR 'receptionist_user'@'localhost';


REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'doctor_user'@'localhost';


DROP USER 'doctor_user'@'localhost';


DROP USER 'admin_user'@'localhost';


DROP USER 'receptionist_user'@'localhost';

