DELIMITER //

CREATE PROCEDURE Count_Scheduled_Doctor_Appointments()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE doc_id INT;
    DECLARE doc_name VARCHAR(100);
    DECLARE total_appointments INT;
    
    -- Cursor to fetch all doctors
    DECLARE doctor_cursor CURSOR FOR
    SELECT Doctor_ID, Name FROM Doctor;

    -- Error handler for no more rows
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Create a temporary table to store results
    CREATE TEMPORARY TABLE IF NOT EXISTS Doctor_Appointment_Count (
        Doctor_Name VARCHAR(100),
        Total_Scheduled_Appointments INT
    );

    -- Open cursor
    OPEN doctor_cursor;

    read_loop: LOOP
        FETCH doctor_cursor INTO doc_id, doc_name;

        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Count only scheduled appointments for the current doctor
        SELECT COUNT(*) INTO total_appointments 
        FROM Appointment 
        WHERE Doctor_ID = doc_id AND Status = 'Scheduled';

        -- Insert result into temporary table
        INSERT INTO Doctor_Appointment_Count (Doctor_Name, Total_Scheduled_Appointments) 
        VALUES (doc_name, total_appointments);
    END LOOP;

    -- Close cursor
    CLOSE doctor_cursor;

    -- Display results
    SELECT * FROM Doctor_Appointment_Count;

    -- Drop temporary table after use
    DROP TEMPORARY TABLE IF EXISTS Doctor_Appointment_Count;
END //

DELIMITER ;


DROP PROCEDURE IF EXISTS Count_Scheduled_Doctor_Appointments;

CALL Count_Scheduled_Doctor_Appointments; 
