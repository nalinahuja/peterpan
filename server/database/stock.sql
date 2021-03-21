-- REMOVE FOR PRODUCTION RELEASE

DROP TABLE IF EXISTS Stock;
DROP TABLE IF EXISTS Company;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Buys;
DROP TABLE IF EXISTS Sells;
DROP TABLE IF EXISTS Watchlist;
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Groups;
DROP TABLE IF EXISTS Group_Stock;
DROP TABLE IF EXISTS Group_Balance;

-- --------------------------------------------------------

--
-- Table structure for table `Stock`
--

CREATE TABLE IF NOT EXISTS `Stock` (
  -- Primary Key
  `stock_id` int(11) NOT NULL,
  PRIMARY KEY (`stock_id`),

  -- Attributes
  `name` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `share` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Company`
--

CREATE TABLE IF NOT EXISTS `Company` (
  -- Primary Key
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`name`),

  -- Foreign Keys
  `stock_id` int(11) NOT NULL,
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`),

  -- Attributes
  `website` varchar(50) NOT NULL,
  `company_size` int(11) NOT NULL,
  `shareholders` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `User`
--

CREATE TABLE IF NOT EXISTS `User` (
  -- Primary Key
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`),

  -- Attributes
  `balance` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Buys`
--

CREATE TABLE IF NOT EXISTS `Buys` (
  -- Primary Key
  `buy_id` int(11) NOT NULL,
  PRIMARY KEY (`buy_id`),

  -- Foreign Keys
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,
  FOREIGN KEY (`user_id`) REFERENCES User(`user_id`),
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`),

  -- Attributes
  `amount` int(11) NOT NULL,
  `purchase_price` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `sells`
--

CREATE TABLE IF NOT EXISTS `Sells` (
  -- Primary Key
  `sell_id` int(11) NOT NULL,
  PRIMARY KEY (`sell_id`),

  -- Foreign Keys
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,
  FOREIGN KEY (`user_id`) REFERENCES User(`user_id`),
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`),

  -- Attributes
  `amount` int(11) NOT NULL,
  `sell_price` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Watchlist`
--

CREATE TABLE IF NOT EXISTS `Watchlist` (
  -- Primary Key
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`, `stock_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Transaction`
--

CREATE TABLE IF NOT EXISTS `Transaction` (
  -- Primary Key
  `transaction_id` int(11) NOT NULL,
  PRIMARY KEY (`transaction_id`)

  -- Foreign Keys
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,
  FOREIGN KEY (`user_id`) REFERENCES User(`user_id`),
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`),

  -- Attributes
  `amount` int(11) NOT NULL,
  `date` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Groups`
--

CREATE TABLE IF NOT EXISTS `Groups` (
  -- Primary Key
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`group_id`)

  -- Attributes
  `balance` DECIMAL(12, 10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Group_Users`
--

CREATE TABLE IF NOT EXISTS `Group_Users` (
  -- Primary Key
  `group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`group_id`, `user_id`),

  -- Foreign Key
  FOREIGN KEY (`group_id`) REFERENCES Groups(`group_id`),
  FOREIGN KEY (`user_id`) REFERENCES User(`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Group_Stock`
--

CREATE TABLE IF NOT EXISTS `Group_Stock` (
  -- Primary Key
  `group_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,
  PRIMARY KEY (`group_id`, `stock_id`),

  -- Foreign Key
  FOREIGN KEY (`group_id`) REFERENCES Groups(`group_id`),
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------
