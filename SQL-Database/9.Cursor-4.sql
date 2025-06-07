DELIMITER //
-- DROP PROCEDURE Calculate_Avg_Expense_Per_Customer;
-- 
CREATE PROCEDURE Calculate_Avg_Expense_Per_Customer()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE p_id INT;
    DECLARE avg_expense DECIMAL(10,2);

    -- Cursor to fetch all distinct patients who have bills
    DECLARE patient_cursor CURSOR FOR
    SELECT DISTINCT Patient_ID FROM Billing;

    -- Error handler for no more rows
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Create a temporary table to store results
    CREATE TEMPORARY TABLE IF NOT EXISTS Avg_Expense_Per_Customer (
        Patient_ID INT,
        Avg_Expense DECIMAL(10,2)
    );

    -- Open cursor
    OPEN patient_cursor;

    read_loop: LOOP
        FETCH patient_cursor INTO p_id;

        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Calculate average expense for the current patient
        SELECT COALESCE(AVG(Total_Amount), 0) INTO avg_expense 
        FROM Billing
        WHERE Patient_ID = p_id;

        -- Insert result into temporary table
        INSERT INTO Avg_Expense_Per_Customer (Patient_ID, Avg_Expense) 
        VALUES (p_id, avg_expense);
    END LOOP;

    -- Close cursor
    CLOSE patient_cursor;

    -- Display results
    SELECT * FROM Avg_Expense_Per_Customer;

    -- Drop temporary table after use
    DROP TEMPORARY TABLE IF EXISTS Avg_Expense_Per_Customer;
END //

DELIMITER ;


CALL Calculate_Avg_Expense_Per_Customer();
