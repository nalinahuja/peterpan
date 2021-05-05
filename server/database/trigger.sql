DROP TRIGGER IF EXISTS update_user_shares;

DELIMITER //

CREATE TRIGGER update_user_shares
AFTER INSERT ON User_Transaction
FOR EACH ROW

BEGIN

SET @type = (SELECT type
                FROM User_Transaction
                WHERE transaction_id = new.transaction_id);
SET @amount = (SELECT amount
                FROM Transaction
                WHERE transaction_id = new.transaction_id);

IF @type = 1
THEN
    INSERT INTO User_Stock (user_id, stock_id, amount)
    VALUES (new.user_id, new.stock_id, @amount)
    ON DUPLICATE KEY UPDATE amount = (amount + @amount);
ElSE
    INSERT INTO User_Stock (user_id, stock_id, amount)
    VALUES (new.user_id, new.stock_id, @amount)
    ON DUPLICATE KEY UPDATE amount = (amount - @amount);

    SET @new_amount = (SELECT amount
                       FROM User_Stock
                       WHERE stock_id = new.stock_id AND user_id = new.user_id);

    IF @new_amount = 0
    THEN
      DELETE FROM User_Stock
      WHERE stock_id = new.stock_id AND user_id = new.user_id;
    END IF;
END IF;

END //
DELIMITER ;

DROP TRIGGER IF EXISTS update_group_shares;

DELIMITER //

CREATE TRIGGER update_group_shares
AFTER INSERT ON Group_Transaction
FOR EACH ROW

BEGIN

    SET @type = (SELECT type
                    FROM Group_Transaction
                    WHERE transaction_id = new.transaction_id);
    SET @amount = (SELECT amount
                    FROM Transaction
                    WHERE transaction_id = new.transaction_id);

    IF @type = 1
    THEN
        INSERT INTO Group_Stock (group_id, stock_id, amount)
        VALUES(new.group_id, new.stock_id, @amount)
        ON DUPLICATE KEY UPDATE amount = (amount + @amount);
    ELSE
        INSERT INTO Group_Stock (group_id, stock_id, amount)
        VALUES(new.group_id, new.stock_id, @amount)
        ON DUPLICATE KEY UPDATE amount = (amount - @amount);

        SET @new_amount = (SELECT amount
                           FROM Group_Stock
                           WHERE stock_id = new.stock_id AND group_id = new.group_id);

        IF @new_amount = 0
        THEN
          DELETE FROM Group_Stock
          WHERE stock_id = new.stock_id AND group_id = new.group_id;
        END IF;
    END IF;

END //
DELIMITER ;
