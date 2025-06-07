DELIMITER //

CREATE PROCEDURE Calculate_Avg_Age_All_Roles()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE role_name VARCHAR(50);
    DECLARE avg_age DECIMAL(5,2);
    
    -- Cursor to iterate through roles (Doctor, Patient, Staff)
    DECLARE role_cursor CURSOR FOR
    SELECT 'Doctor' UNION 
    SELECT 'Patient' UNION 
    SELECT 'Staff';

    -- Error handler for no more rows
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Create a temporary table to store results
    CREATE TEMPORARY TABLE IF NOT EXISTS Avg_Age_By_Role (
        Role VARCHAR(50),
        Avg_Age DECIMAL(5,2)
    );

    -- Open cursor
    OPEN role_cursor;

    read_loop: LOOP
        FETCH role_cursor INTO role_name;

        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Calculate average age for each role
        IF role_name = 'Doctor' THEN
            SELECT COALESCE(AVG(Age), 0) INTO avg_age FROM Doctor;
        ELSEIF role_name = 'Patient' THEN
            SELECT COALESCE(AVG(Age), 0) INTO avg_age FROM Patient;
        ELSEIF role_name = 'Staff' THEN
            SELECT COALESCE(AVG(Age), 0) INTO avg_age FROM Staff;
        END IF;

        -- Insert result into temporary table
        INSERT INTO Avg_Age_By_Role (Role, Avg_Age) 
        VALUES (role_name, avg_age);
    END LOOP;

    -- Close cursor
    CLOSE role_cursor;

    -- Display results
    SELECT * FROM Avg_Age_By_Role;

    -- Drop temporary table after use
    DROP TEMPORARY TABLE IF EXISTS Avg_Age_By_Role;
END //

DELIMITER ;


CALL Calculate_Avg_Age_All_Roles();
