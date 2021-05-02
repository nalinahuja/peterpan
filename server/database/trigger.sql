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

IF @type = 1 THEN
    UPDATE User_Stock
	SET shares = amount + @amount
	WHERE stock_id = new.stock_id AND user_id = new.user_id
ELSE
    UPDATE User_Stock
	SET shares = amount - @amount
	WHERE stock_id = new.stock_id AND user_id = new.user_id
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

IF @type = 1 THEN
    UPDATE Group_Stock
	SET shares = shares + @amount
	WHERE stock_id = new.stock_id AND group_id = new.group_id
ELSE
    UPDATE Group_Stock
	SET shares = shares - @amount
	WHERE stock_id = new.stock_id AND group_id = new.group_id
END IF;

END //
DELIMITER ;