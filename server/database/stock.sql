-- REMOVE FOR PRODUCTION RELEASE

DROP TABLE IF EXISTS `Stock`;
DROP TABLE IF EXISTS `Stock_Update`;

DROP TABLE IF EXISTS `User`;
DROP TABLE IF EXISTS `Watchlist`;

DROP TABLE IF EXISTS `Transaction`;
DROP TABLE IF EXISTS `User_Transaction`;
DROP TABLE IF EXISTS `Group_Transaction`;

DROP TABLE IF EXISTS `Groups`;
DROP TABLE IF EXISTS `Group_Users`;
DROP TABLE IF EXISTS `Group_Stock`;

-- --------------------------------------------------------

--
-- Table structure for table `Stock`
--

CREATE TABLE IF NOT EXISTS `Stock` (
  -- Attributes
  `stock_id` int(11) NOT NULL,
  `name` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `share` int(11) NOT NULL,

  -- Keys
  PRIMARY KEY (`stock_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Stock_Update`
--

CREATE TABLE IF NOT EXISTS `Stock_Update` (
  -- Attributes
  `update_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,
  `price_change` DECIMAL(12, 10) NOT NULL,

  -- Keys
  PRIMARY KEY (`update_id`, `stock_id`),
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `User`
--

CREATE TABLE IF NOT EXISTS `User` (
  -- Attributes
  `user_id` int(11) NOT NULL,
  `balance` DECIMAL(12, 10) NOT NULL,
  `password` DECIMAL(12,10) NOT NULL,

  -- Keys
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Watchlist`
--

CREATE TABLE IF NOT EXISTS `Watchlist` (
  -- Attributes
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,
  /*`purchase_price` int(11) NOT NULL,
  `stock_remaining` int(11) NOT NULL,*/

  -- Keys
  PRIMARY KEY (`user_id`, `stock_id`),
  FOREIGN KEY (`user_id`) REFERENCES User(`user_id`),
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Transaction`
--

CREATE TABLE IF NOT EXISTS `Transaction` (
  -- Attributes
  `transaction_id` int(11) NOT NULL,
  `amount` DECIMAL(12, 10) NOT NULL,
  `date`  DECIMAL(12,10) NOT NULL,

  -- Keys
  PRIMARY KEY (`transaction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `User_Transaction`
-- type - (0 => SELL), (1 => BUY)
--

CREATE TABLE IF NOT EXISTS `User_Transaction` (
  -- Attributes
  `transaction_id` int(11) NOT NULL,
  `type` BIT NOT NULL,
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,

  -- Keys
  PRIMARY KEY (`transaction_id`),
  FOREIGN KEY (`user_id`) REFERENCES User(`user_id`),
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`),
  FOREIGN KEY (`transaction_id`) REFERENCES Transaction(`transaction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Group_Transaction`
-- type - (0 => SELL), (1 => BUY)
--

CREATE TABLE IF NOT EXISTS `Group_Transaction` (
  -- Attributes
  `transaction_id` int(11) NOT NULL,
  `type` BIT NOT NULL,
  `group_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,

  -- Keys
  PRIMARY KEY (`transaction_id`, `group_id`, `stock_id`),
  FOREIGN KEY (`group_id`) REFERENCES Group(`group_id`),
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`),
  FOREIGN KEY (`transaction_id`) REFERENCES Transaction(`transaction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Groups`
--

CREATE TABLE IF NOT EXISTS `Groups` (
  -- Attributes
  `group_id` int(11) NOT NULL,
  `balance` DECIMAL(12, 10) NOT NULL,

  -- Keys
  PRIMARY KEY (`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Group_Users`
--

CREATE TABLE IF NOT EXISTS `Group_Users` (
  -- Attributes
  `group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,

  -- Keys
  PRIMARY KEY (`group_id`, `user_id`)
  FOREIGN KEY (`user_id`) REFERENCES User(`user_id`),
  FOREIGN KEY (`group_id`) REFERENCES Groups(`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Group_Stock`
--

CREATE TABLE IF NOT EXISTS `Group_Stock` (
  -- Attributes
  `group_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,

  -- Keys
  PRIMARY KEY (`group_id`, `stock_id`)
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`),
  FOREIGN KEY (`group_id`) REFERENCES Groups(`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------
