DROP TABLE IF EXISTS Company;
DROP TABLE IF EXISTS Buys;
DROP TABLE IF EXISTS Sells;
DROP TABLE IF EXISTS Watchlist;
DROP TABLE IF EXISTS User_Information;
DROP TABLE IF EXISTS Stock_Price;
DROP TABLE IF EXISTS Transaction;

-- --------------------------------------------------------

--
-- Table structure for table `Company`
--


CREATE TABLE IF NOT EXISTS `Company` (
  `stock_id` int(11) NOT NULL,
  `company_size` int(11) NOT NULL,
  `num_of_stockholders` int(11) NOT NULL,
  `website` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Buys`
--

CREATE TABLE IF NOT EXISTS `Buys` (
  `buy_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `purchase_price` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `sells`
--

CREATE TABLE IF NOT EXISTS `Sells` (
  `sell_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `sell_price` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Watchlist`
--

CREATE TABLE IF NOT EXISTS `Watchlist` (
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `User_Information`
--

CREATE TABLE IF NOT EXISTS `User_Information` (
  `user_id` int(11) NOT NULL,
  `money_on_account` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Stock_Price`
--

CREATE TABLE IF NOT EXISTS `Stock_Price` (
  `stock_id` int(11) NOT NULL,
  `stock_name` int(11) NOT NULL,
  `stock_price` int(11) NOT NULL,
  `stock_share` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
