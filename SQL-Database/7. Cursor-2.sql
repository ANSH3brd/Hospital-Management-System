DELIMITER //

CREATE PROCEDURE Get_Total_Revenue()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE bill_amount DECIMAL(10,2);
    DECLARE total_revenue DECIMAL(10,2) DEFAULT 0;

    -- Cursor to fetch all bill amounts from the Billing table
    DECLARE revenue_cursor CURSOR FOR
    SELECT Total_Amount FROM Billing WHERE Payment_Status = 'Completed';

    -- Error handler for no more rows
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Open cursor
    OPEN revenue_cursor;

    read_loop: LOOP
        FETCH revenue_cursor INTO bill_amount;

        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Add bill amount to total revenue
        SET total_revenue = total_revenue + bill_amount;
    END LOOP;

    -- Close cursor
    CLOSE revenue_cursor;

    -- Display the total revenue collected
    SELECT total_revenue AS Total_Revenue_Collected;
END //

DELIMITER ;


CALL Get_Total_Revenue();
