-- REMOVE FOR PRODUCTION RELEASE


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
-- Table structure for table `Company`
--

CREATE TABLE IF NOT EXISTS `Company` (
  -- Attributes
  `name` varchar(50) NOT NULL,
  `stock_id` int(11) NOT NULL,
  `website` varchar(50) NOT NULL,
  `company_size` int(11) NOT NULL,
  `shareholders` int(11) NOT NULL,

  -- Keys
  PRIMARY KEY (`name`),
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

  -- Keys
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Transaction`
--

CREATE TABLE IF NOT EXISTS `Transaction` (
  -- Attributes
  `transaction_id` int(11) NOT NULL,
  `amount` DECIMAL(12, 10) NOT NULL,
  `quantity` int(11) NOT NULL,
  `date` int(11) NOT NULL,

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
  PRIMARY KEY (`transaction_id`, `user_id`, `stock_id`),
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
  FOREIGN KEY (`transaction_id`) REFERENCES Transaction(`transaction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Watchlist`
--

CREATE TABLE IF NOT EXISTS `Watchlist` (
  -- Attributes
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,

  -- Keys
  PRIMARY KEY (`user_id`, `stock_id`)
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
  PRIMARY KEY (`group_id`, `user_id`),
  FOREIGN KEY (`group_id`) REFERENCES Groups(`group_id`),
  FOREIGN KEY (`user_id`) REFERENCES User(`user_id`)
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
  PRIMARY KEY (`group_id`, `stock_id`),
  FOREIGN KEY (`group_id`) REFERENCES Groups(`group_id`),
  FOREIGN KEY (`stock_id`) REFERENCES Stock(`stock_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------
