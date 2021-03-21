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

  -- Attributes
  `stock_name` int(11) NOT NULL,
  `stock_price` int(11) NOT NULL,
  `stock_share` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Company`
--

CREATE TABLE IF NOT EXISTS `Company` (
  -- Foreign Keys
  `stock_id` int(11) NOT NULL,

  -- Attributes
  `company_size` int(11) NOT NULL,
  `num_of_stockholders` int(11) NOT NULL,
  `website` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `User`
--

CREATE TABLE IF NOT EXISTS `User` (
  -- Primary Key
  `user_id` int(11) NOT NULL,

  -- Attributes
  `money_on_account` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Buys`
--

CREATE TABLE IF NOT EXISTS `Buys` (
  -- Primary Key
  `buy_id` int(11) NOT NULL,

  -- Foreign Keys
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,

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

  -- Foreign Keys
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,

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
  `stock_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Transaction`
--

CREATE TABLE IF NOT EXISTS `Transaction` (
  -- Primary Key
  `transaction_id` int(11) NOT NULL,

  -- Foreign Keys
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,

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
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Group_Stock`
--

CREATE TABLE IF NOT EXISTS `Group_Stock` (
  -- Foreign Key
  `group_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Group_Balance`
--

CREATE TABLE IF NOT EXISTS `Group_Balance` (
  -- Foreign Key
  `group_id` int(11) NOT NULL,

  -- Attribute
  `balance` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------
