import os
import ui
import time
import yaml
import globl
import random
import datetime
import mysql.connector

from datetime import timedelta
from collections import defaultdict
from multiprocessing import Process
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import make_response

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_access_cookies
from flask_jwt_extended import verify_jwt_in_request

# End Imports---------------------------------------------------------------------------------------------------------------------------------------------------------

# Transaction Constants
BUY, SELL = 1, 0

# Maximum Price Change
MAXIMUM_PRICE_CHANGE = 20

# Server Constants----------------------------------------------------------------------------------------------------------------------------------------------------

# Load Database Configuration
dbconf = yaml.load(open(os.environ["DATABASE_CONFIG"]), yaml.Loader)

# Establish Database Connection
cnx = mysql.connector.connect(user = dbconf['mysql_user'], password = dbconf['mysql_password'], host = dbconf['mysql_host'], database = dbconf['mysql_db'])

# End Database Connector----------------------------------------------------------------------------------------------------------------------------------------------

# Queries For Database
get_stock = """
            SELECT stock_id, name, price, share
            FROM Stock;
            """

user_account_money = """
                     SELECT balance
                     FROM User
                     Where user_id = %s;
                     """


get_stock_by_stock_name = """
                          SELECT stock_id,price,share
                          FROM Stock
                          WHERE name = %s;
                          """

get_stock_by_stock_id = """
                        SELECT name,price,share
                        FROM Stock
                        WHERE stock_id = %s;
                        """

get_user_balance = """
                   SELECT balance
                   FROM User
                   WHERE user_id = %s;
                   """

get_group_balance = """
                   SELECT balance
                   FROM Group_Info
                   WHERE group_id = %s;
                   """

get_watchlist = """
                SELECT stock_id
                FROM Watchlist
                WHERE user_id = %s AND stock_id = %s;
                """

get_transaction_number = """
                         SELECT COUNT(*)
                         FROM Transaction;
                         """

get_amount_bought = """
                    SELECT SUM(t.amount)
                    FROM Transaction t, User_Transaction ut
                    WHERE t.transaction_id = ut.transaction_id AND ut.type = 1 AND stock_id = %s AND user_id = %s;
                    """

get_amount_sold =  """
                   SELECT SUM(t.amount)
                   FROM Transaction t, User_Transaction ut
                   WHERE t.transaction_id = ut.transaction_id AND ut.type = 0 AND stock_id = %s AND user_id = %s;
                   """

get_transactions = """
                   SELECT U.stock_id, S.name, T.amount, U.type AS transaction_type, T.price, T.date
                   FROM User_Transaction AS U JOIN Transaction AS T ON U.transaction_id = T.transaction_id
                   JOIN Stock AS S ON U.stock_id = S.stock_id
                   WHERE U.user_id = {};
                   """

get_max_update_id = """
                    SELECT MAX(update_id)
                    FROM Stock_Update;
                    """

get_number_of_stock = """
                      SELECT MAX(stock_id)
                      FROM Stock;
                      """

update_stock_share = """
                     UPDATE Stock
                     SET share = {}
                     WHERE stock_id = {};
                     """

update_user_balance = """
                      UPDATE User
                      SET balance = {}
                      WHERE user_id = {};
                      """

update_group_balance = """
                       UPDATE Group_Info
                       SET balance = {}
                       WHERE group_id = {};
                       """

insert_user_transaction = """
                          INSERT INTO User_Transaction (transaction_id, type, user_id, stock_id)
                          VALUES (%d,%d,%s,%d);
                          """

insert_transaction = """
                     INSERT INTO Transaction (transaction_id, amount, date, price)
                     VALUES (%d,%d,%s,%f);
                     """

insert_watchlist = """
                   INSERT INTO Watchlist (user_id,stock_id)
                   VALUES (%s, %s);
                   """

repeatable_read = "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;"

committed_read = "SET TRANSACTION ISOLATION LEVEL READ COMMITTED;"

serializable = "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;"

transaction_start = "START TRANSACTION;"

transaction_commit = "COMMIT;"

# End SQL Queries-----------------------------------------------------------------------------------------------------------------------------------------------------

# Create Flask Application
app = Flask(__name__)

# Configure Flask Key
app.config['SECRET_KEY'] = '537e3275e714ff299e49'

# Configure JWT Authentication
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days = 10)

# Configure ORM Database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:' + dbconf['mysql_password'] + '@localhost/' + dbconf['mysql_db']

# End Server Initialization----------------------------------------------------------------------------------------------------------------------------------------------------

# Intiialize ORM Database
db = SQLAlchemy(app)

# Verify SQL_ALCHEMY_DB
if (db is None):
    raise ValueError("Could not initialize ORM: db is None")

# Set ORM Database Reference
globl.SQL_ALCHEMY_DB = db

# Import All Tables From ORM Module
from orm import *

# End ORM Initialization----------------------------------------------------------------------------------------------------------------------------------------------------

# Set JWT Token Location
JWT_TOKEN_LOCATION = ['cookies']

# Configure JWT Manager
jwt = JWTManager(app)

# Unauthorized Page Access Handler
@jwt.unauthorized_loader
def unauthorized(callback):
    return (render_template('401.html', navbar = ui.navbar(request)))

# End Authentication Initialization------------------------------------------------------------------------------------------------------------------------------------------------------

def update_stock():
    db.engine.execute(serializable)
    db.engine.execute(transaction_start)
    cursor = cnx.cursor()
    print ("update started")
    #get maximum number of update id
    cursor.execute(get_max_update_id)
    max_update_id = 0
    for cur in cursor:
        max_update_id = cur
    max_update_id = max_update_id[0]
    max_update_id += 1

    #get total number of stocks in stock table
    cursor.execute(get_number_of_stock)
    num_of_stock = 0
    for cur in cursor:
        num_of_stock = cur
    num_of_stock = num_of_stock[0]

    #loop through all of the stocks
    for i in range(num_of_stock):
        #generate a random number for price change
        id = int(random.randint(0, 1))
        delta = float(random.random() * MAXIMUM_PRICE_CHANGE) * (-1 if (id == 0) else 1)

        #get stock information
        input_token = (i,)
        cursor.execute(get_stock_by_stock_id,input_token)
        stock_name = ""
        stock_price,stock_share = 0,0
        for name,price,share in cursor:
            stock_name,stock_price,stock_share  = name,price,share
        new_price = stock_price + delta
        #if the new price is negative or zero, then just do nothing
        if(new_price <= 0) : continue

        #update the stock price using ORM
        stock_spec = Stock.query.filter_by(stock_id=i).first()
        stock_spec.price = new_price
        db.session.commit()
        new_update = Stock_Update(update_id=max_update_id, stock_id = i, price_change = delta)
        db.session.add(new_update)
        db.session.commit()
        #update the stock change using ORM
    print("update ended")
    cursor.close()
    db.engine.execute(transaction_commit)

# # Initialize Background Scheduler
# scheduler = BackgroundScheduler()
#
# # Create New Job
# scheduler.add_job(update_stock, 'interval', minutes = 5)
#
# # Start Scheduler
# scheduler.start()

# End Internal Functions----------------------------------------------------------------------------------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    # Return 404 page
    return (render_template('404.html', navbar = ui.navbar(request))), 404

@app.route("/", methods = ['GET', 'POST'])
def index():
    # Check For POST Method
    if (request.method == 'POST'):
        # Fetch User Form Data
        user_data = request.form

        # Determine Redirect
        if (user_data.get("search")):
            return (redirect(str('/search/' + user_data["search_info"])))
        elif (user_data.get("buy")):
            return (redirect('/buy'))
        elif (user_data.get("sell")):
            return (redirect('/sell'))
        elif (user_data.get("register")):
            return (redirect('/register'))
        elif (user_data.get("transactions")):
            return (redirect("/transactions"))

    # Open Database Cursor
    cursor = cnx.cursor()

    # Initialize Stock Data
    num_stocks = num_shares = 0

    # Query To Fetch Number Of Stocks In Market
    query = """
            SELECT COUNT(*) AS result
            FROM Stock;
            """

    # Execute Query
    cursor.execute(query)

    # Fetch Data From Cursor
    for result in (cursor):
        num_stocks = int(result[0])

    # Query To Fetch Number Of Shares In Market
    query = """
            SELECT SUM(share) AS result
            FROM Stock;
            """

    # Execute Query
    cursor.execute(query)

    # Fetch Data From Cursor
    for result in (cursor):
        if (result[0] is not None):
            num_shares = int(result[0])

    # Initialize Stock Market Data
    transaction_cnt = avg_buy_price = avg_sell_price = None

    # Query To Fetch Number Of Transactions In Last 24hr
    query = """
            SELECT COUNT(*) AS result
            FROM Transaction
            WHERE 86400 <= UNIX_TIMESTAMP() - date;
            """

    # Execute Query
    cursor.execute(query)

    # Fetch Data From Cursor
    for result in (cursor):
        transaction_cnt = int(result[0])

    # Query To Fetch Average Transaction Prices In The Last 24hrs
    query = """
            SELECT type, AVG(price)
            FROM Transaction JOIN User_Transaction ON Transaction.transaction_id = User_Transaction.transaction_id
            WHERE 86400 <= UNIX_TIMESTAMP() - date
            GROUP BY type
            UNION
            SELECT type, AVG(price)
            FROM Transaction JOIN Group_Transaction ON Transaction.transaction_id = Group_Transaction.transaction_id
            WHERE 86400 <= UNIX_TIMESTAMP() - date
            GROUP BY type;
            """

    # Execute Query
    cursor.execute(query)

    # Format Price Data
    avg_buy_price = "{:,.2f}".format(sum(t[1] for t in cursor if (t[0] == BUY)))
    avg_sell_price = "{:,.2f}".format(sum(t[1] for t in cursor if (t[0] == SELL)))

    # Get Oldest Historical Stock Prices
    query = """
            SELECT stock_id, price_change
            FROM Stock_Update
            WHERE update_id = 0
            """

    # Execute Query
    cursor.execute(query)

    # Initialize Stock Dictionary
    stocks = defaultdict(int)

    # Extract Data From Cursor
    for result in (cursor):
        stocks[int(result[0])] = float(result[1])

    # Get Newest Historical Stock Prices
    query = """
            SELECT stock_id, price_change
            FROM Stock_Update
            WHERE update_id = (SELECT MAX(update_id) FROM Stock_Update)
            """

    # Execute Query
    cursor.execute(query)

    # Calculate Average Price
    for result in (cursor):
        stocks[int(result[0])] = ((stocks[int(result[0])] + float(result[1])) / 2)

    # Get Top Two Stocks Ranked By Decreasing Historical Average Price
    stock_rank = sorted(stocks.items(), key = lambda x : x[1], reverse = True)[:2]

    # Initialize Data Lists
    namelist, datalists = [], []

    # Iterate Over Stock Ranks
    for stock_id, _ in (stock_rank):
        # Query To Get All Price Changes Of A Stock ID
        query = """
                SELECT price_change
                FROM Stock_Update
                WHERE stock_id = {};
                """

        # Execute Query
        cursor.execute(query.format(stock_id))

        # Fetch Data From Cursor
        datalist = [pc[0] for pc in (cursor)]

        # Append Data To List
        datalists.append(datalist)

        # Query To Get Stock Name Of a Stock ID
        query = """
                SELECT name
                FROM Stock
                WHERE stock_id = {};
                """

        # Execute Query
        cursor.execute(query.format(stock_id))

        # Fetch Data From Cursor
        for result in (cursor):
            namelist.append(str(result[0]))

    # Close Cursor
    cursor.close()

    # Format Data
    num_stocks = "{:,d}".format(num_stocks)
    num_shares = "{:,d}".format(num_shares)
    transaction_cnt = "{:,d}".format(transaction_cnt)

    # Error Correct Stock Data
    if (not(namelist)):
        namelist = [None, None]
    if (not(datalists)):
        datalists = [[], []]

    # Render Index Template
    return (render_template('index.html', navbar = ui.navbar(request), num_stocks = num_stocks, num_shares = num_shares, \
                            transaction_cnt = transaction_cnt, avg_buy_price = avg_buy_price, avg_sell_price = avg_sell_price, \
                            stock_name_1 = namelist[0], stock_name_2 = namelist[1], price_arr_1 = str(datalists[0]), price_arr_2 = str(datalists[1])))

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        # Fetch User Input Data
        user_data = request.form
        input_user_id = user_data["user_id"]
        input_password = user_data["password"]

        # Get User Object Using ORM
        obj = User.query.filter_by(user_id = input_user_id, password = input_password).first()

        # Verify Return From Database
        if (obj is None):
            # Update View
            return (render_template('login.html', navbar = ui.navbar(request), error = True))

        # Create Response
        response = make_response(redirect('/portfolio'.format(obj.user_id)))

        # Create Access Token
        access_token = create_access_token(identity = input_user_id)

        # Set Access Cookies In Response
        set_access_cookies(response, access_token)

        # Return Response To Client
        return (response)

    # Render Default Login Page
    return (render_template('login.html', navbar = ui.navbar(request), error = False))

@app.route("/logoff", methods = ['GET', 'POST'])
@jwt_required(locations = ['cookies'])
def logoff():
    # Fetch User Access Token
    response = make_response(redirect('/login'))

    # Revoke Access Cookies
    unset_access_cookies(response)

    # Send Response
    return (response)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    # Open Database cursor
    cursor = cnx.cursor()
    if (request.method == 'POST'):
        db.engine.execute(serializable)
        db.engine.execute(transaction_start)
        # Fetch User Input Data
        user_data = request.form
        input_user_id = user_data["user_id"]
        input_password = user_data["password"]
        confirm_password = user_data["confirm_password"]

        # Verify Both Password Inputs Match
        if(input_password != confirm_password):
            return (render_template('register.html', navbar = ui.navbar(request), error = True, msg = "Passwords do not match, please try again."))

        # Initialize Cursor Input
        cursor_input = (input_user_id,)
        # Execute Query
        cursor.execute(get_user_balance, cursor_input)

        # Check If User Id Already Exists
        balance = -9999

        # Extract Data From Cursor
        for cur in (cursor):
            balance = cur

        if(balance != -9999):
            return (render_template('register.html', navbar = ui.navbar(request), error = True, msg = "User ID exists, please choose a different one."))

        # Use ORM to Add New User
        user_query = """
                     INSERT INTO User (user_id, balance, password)
                     VALUES ({}, {}, {});
                     """

        # Execute Query
        cursor.execute(user_query.format(input_user_id, 2500000, input_password))
        cnx.commit()

        # Get User Object Using ORM
        obj = User.query.filter_by(user_id = input_user_id, password = input_password).first()

        # Verify Return From Database
        if (obj is None):
            # Update View
            return (render_template('register.html', navbar = ui.navbar(request), error = True, msg = "Sorry, we could not create an account for you at this time."))

        # Create Response
        response = make_response(render_template('register_success.html', navbar = ui.navbar(request)))

        # Create Access Token
        access_token = create_access_token(identity = input_user_id)

        # Set Access Cookies In Response
        set_access_cookies(response, access_token)

        # Return Response To Client
        db.engine.execute(transaction_commit)
        return (response)

    # Close Cursor
    cursor.close()

    # Return Response To Client
    return (render_template('register.html', navbar = ui.navbar(request)))

@app.route("/search/<stock_name>", methods = ['GET', 'POST'])
def search(stock_name):
    return (redirect("/stocks/" + stock_name))

@app.route("/stocks", methods = ["GET", "POST"])
def multi_stock():
    # Open Database Cursor
    cursor = cnx.cursor()

    # Query To Get Stock Data By Name
    query = """
            SELECT name, price, share
            FROM Stock;
            """

    # Get Stock Data By Name
    cursor.execute(query)

    # Initialize Stock Data
    stock_data = []

    # Extract Data From Cursor
    for row in (cursor):
        # Set Stock Data
        stock_data.append(row)

    # Determine Stock Existence
    if(not(len(stock_data))):
        # Return Response To User
        return (render_template("error.html", navbar = ui.navbar(request), msg = "We could not find any stocks"))
    else:
        # Return Response To User
        return (render_template("stock_multi.html", navbar = ui.navbar(request), stock_data = stock_data))

@app.route("/stocks/<stock_name>", methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def single_stock(stock_name):
    # Get Current User ID
    user_id = get_jwt_identity()

    # Open Database Cursor
    db.engine.execute(committed_read)
    db.engine.execute(transaction_start)
    cursor = cnx.cursor()

    # Query To Get Stock Data By Name
    query = """
            SELECT price, share
            FROM Stock
            WHERE name = "{}";
            """

    # Get Stock Data By Name
    cursor.execute(query.format(stock_name))

    # Initialize Stock Data
    stock_price, stock_share = None, None

    # Extract Data From Cursor
    for price, share in (cursor):
        # Set Stock Data
        stock_price, stock_share = price, share

    # Query To Get Stock History Data
    query = """
            SELECT price_change
            FROM Stock_Update
            WHERE stock_id = (SELECT stock_id FROM Stock WHERE name = "{}");
            """

    # Get Stock Data By Name
    cursor.execute(query.format(stock_name))

    # Get Result From Cursor
    si = [si[0] for si in (cursor)]
    db.engine.execute(transaction_commit)

    # Initialize Stock Watch Field
    stock_watch = None

    # Query To Get Stock ID From Name
    query = """
            SELECT stock_id
            FROM Watchlist
            WHERE stock_id = (SELECT stock_id FROM Stock WHERE name = "{}");
            """

    # Execute Query
    cursor.execute(query.format(stock_name))

    # Read Result From Cursor
    for result in (cursor):
        stock_watch = result

    # Determine Stock Existence
    if((stock_price is None) or (stock_share is None)):
        # Return Response To User
        return (render_template("error.html", navbar = ui.navbar(request), msg = "That stock does not exist, please try another stock."))
    else:
        # Format Stock Data As Tuple
        stock_info = [stock_name, stock_price, stock_share, (stock_watch is not None)]

        # Return Response To User
        return (render_template("stock_single.html", stock_history = si, data = stock_info, navbar = ui.navbar(request)))

@app.route('/buy', methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def buy():
    # Get Current User ID
    user_id = get_jwt_identity()

    # Open Database Cursor
    cursor = cnx.cursor()

    # Detect For Post Method
    if (request.method == "POST"):
        # Get User Data From Form
        db.engine.execute(repeatable_read)
        db.engine.execute(transaction_start)
        userDetails = request.form
        stock_id = userDetails["stock_id"]
        stock_number = userDetails["number"]
        data = (int(stock_id),)

        # Get Stock Price
        cursor.execute(get_stock_by_stock_id, data)

        # Initialize Stock Data
        stock_price = None
        stock_share = None
        stock_name = ""

        # Fetch Data From Cursor
        for name, price, share in (cursor):
            stock_name = name
            stock_price = price
            stock_share = share

            # Verify Stock ID
            if(not(stock_price)):
                return (render_template("error.html", navbar = ui.navbar(request), msg = "Invalid stock ID. Please Go back and try again!"))

        # Get User Balance
        cur_info = (user_id,)

        # Execute Query
        cursor.execute(get_user_balance, cur_info)

        # Initalize User Balance
        balance = None

        # Fetch User Data From Cursor
        for user_balance in (cursor):
            balance = user_balance[0]

        # Calculate Spent Money
        spent = stock_price * int(stock_number)

        # Calculate Remaining Funds
        remaining_funds = balance - spent

        # Verify Remaining Funds
        if(remaining_funds < 0):
            return (render_template("error.html", navbar = ui.navbar(request), msg = "Not Enough Balance!"))

        # Decrease Stock Share After Purchase
        stock_share = stock_share - int(stock_number)
        update_info = (stock_share,stock_id)
        cursor.execute(update_stock_share.format(stock_share, stock_id))
        cnx.commit()

        # Update User Balance
        cursor.execute(update_user_balance.format(remaining_funds, user_id))
        cnx.commit()

        # Get Transaction Number
        cursor.execute(get_transaction_number)

        # Initialize Transaction ID
        transaction_id = 0

        # Fetch Data From Cursor
        for x in cursor:
            transaction_id = x[0]

        # Increment Transaction ID
        transaction_id += 1

        # Update The Transaction Table
        today = datetime.date.today()
        nt = Transaction(transaction_id = transaction_id,amount = int(stock_number),date = today,price = stock_price)
        db.session.add(nt)
        db.session.commit()

        # Query To Insert User Transaction
        query = """
                INSERT INTO User_Transaction (transaction_id, type, user_id, stock_id)
                VALUES ({}, {}, {}, {});
                """

        # Execute Query
        cursor.execute(query.format(transaction_id, BUY, user_id, stock_id))

        # Commit Data To Database
        cnx.commit()

        # Format Confirmation Data
        confirmation_info = [stock_number,stock_id,stock_name,spent,remaining_funds]

        # Commit Data To Database
        db.engine.execute(transaction_commit)

        # Return Response To user
        return (render_template("confirmation_buy.html", data = confirmation_info, navbar = ui.navbar(request)))
    else:
        # Initialize Stock Data List
        stock_info = []

        # Execute Query To Get All Stock
        cursor.execute(get_stock)

        # Fetch Stock Data From Cursor
        for stock_id, name, price, share in (cursor):
            stock_info.append((stock_id,name,price,share))

        # Close Cursor
        cursor.close()

        # Return Response To User
        return (render_template("buy.html", data = stock_info, navbar = ui.navbar(request)))

@app.route('/sell', methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def sell():
    # Get Current User ID
    user_id = get_jwt_identity()

    # Open Database Cursor
    cursor = cnx.cursor()

    # Detect For Post Method
    if (request.method == "POST"):
        # Start Transaction
        db.engine.execute(repeatable_read)
        db.engine.execute(transaction_start)

        # Get User Details From POST Request
        userDetails = request.form
        stock_id = int(userDetails["stock_id"])
        sale_amount = int(userDetails["number"])

        # Query To Get User Stock By Stock ID
        query = """
                SELECT us.stock_id, st.share, st.name, st.price
                FROM User_Stock us JOIN Stock st ON us.stock_id = st.stock_id
                WHERE us.user_id = {} AND us.stock_id = {};
                """

        # Execute Query
        cursor.execute(query.format(user_id, stock_id))

        # Initialize Stock Data
        stock_name = stock_price = stock_shares = None

        # Fetch Data From Cursor
        for _, shares, name, price in (cursor):
            stock_shares = int(shares)
            stock_price = float(price)
            stock_name = str(name)

        # Verify Remaining Funds
        if (not(stock_name)):
            return (render_template("error.html", navbar = ui.navbar(request), msg = "You Don't Own That Stock!"))

        # Update Market Share Amount
        stock_shares += int(sale_amount)

        # Increase Stock Shares After Purchase
        cursor.execute(update_stock_share.format(stock_shares,stock_id))
        cnx.commit()

        # Query To Get User Balace
        query = """
                SELECT balance
                FROM User
                WHERE user_id = {};
                """

        # Execute Query
        cursor.execute(query.format(user_id))

        # Initialize User Balance
        user_balance = None

        # Fetch Data From Cursor
        for balance in (cursor):
            user_balance = float(balance[0])

        # Calculate Earnings
        earnings = stock_price * sale_amount

        # Update User Balance
        user_balance += earnings

        # Update User Balance
        cursor.execute(update_user_balance.format(user_balance, user_id))
        cnx.commit()

        # Get Transaction Number
        cursor.execute(get_transaction_number)

        # Initialize Transaction ID
        transaction_id = 0

        # Fetch Data From Cursor
        for x in cursor:
            transaction_id = x[0]

        # Increment Transaction ID
        transaction_id += 1

        # Update The Transaction Table
        today = datetime.date.today()
        nt = Transaction(transaction_id = transaction_id,amount = int(sale_amount),date = today,price = stock_price)
        db.session.add(nt)
        db.session.commit()

        # Query To Insert User Transaction
        query = """
                INSERT INTO User_Transaction (transaction_id, type, user_id, stock_id)
                VALUES ({}, {}, {}, {});
                """

        # Execute Query
        cursor.execute(query.format(transaction_id, SELL, user_id, stock_id))

        # Commit Data To Database
        cnx.commit()

        # End Transaction
        db.engine.execute(transaction_commit)

        # Close Cursor
        cursor.close()

        # Form Confirmation Info
        confirmation_info = [sale_amount, stock_id, stock_name, earnings, user_balance]

        # Return Response To user
        return (render_template("confirmation_sell.html", data = confirmation_info, navbar = ui.navbar(request)))
    else:
        # Initialize Stock Data List
        stock_info = []

        # Get Stocks In User Possession
        query = """
                SELECT us.stock_id, st.name, amount, price, share
                FROM User_Stock us JOIN Stock st ON us.stock_id = st.stock_id
                WHERE us.user_id = {};
                """

        # Execute Query To Get All Stock
        cursor.execute(query.format(user_id))

        # Fetch Stock Data From Cursor
        for stock_id, name, amount, price, share in (cursor):
            stock_info.append((stock_id, name, amount, price, share))

        # Close Cursor
        cursor.close()

        # Return Response To User
        return (render_template("sell.html", navbar = ui.navbar(request), data = stock_info))

@app.route('/portfolio')
@jwt_required(locations = ['cookies'])
def portfolio():
    # Get Current User ID
    user_id = get_jwt_identity()

    # Create Cursor
    cursor = cnx.cursor()

    # Query To Get All User Information
    user_query = """
                 SELECT s.stock_id, s.name, s.price, us.amount
                 FROM User u
                 JOIN User_Stock us
                 ON u.user_id = us.user_id
                 JOIN Stock s
                 ON us.stock_id = s.stock_id
                 WHERE u.user_id = {};
                 """

    # Execute Query
    cursor.execute(user_query.format(user_id))

    # Initialize Stock Info List
    stock_info = list()

    # Fetch Results From Cursor
    for stock_id, stock_name, stock_price, stock_shares in (cursor):
        stock_info.append((stock_id, stock_name, stock_price, stock_shares))

    # Query To Get User Balance
    user_query = """
                 SELECT balance
                 FROM User
                 WHERE user_id = {};
                 """

    # Execute Query
    cursor.execute(user_query.format(user_id))

    # Initialize User Balance
    balance = 0

    # Get Data From Cursor
    for result in (cursor):
        balance = float(result[0])

    # Format User Balance
    balance = "{:,.2f}".format(balance)

    # Query To Get User Shares
    user_query = """
                 SELECT SUM(amount)
                 FROM User_Stock
                 WHERE user_id = {};
                 """

    # Execute Query
    cursor.execute(user_query.format(user_id))

    # Initialize User Balance
    stocks_owned = 0

    # Get Data From Cursor
    for result in (cursor):
        if (result[0] is not None):
            stocks_owned = int(result[0])

    # Get user's group_id
    group_query = """
                  SELECT group_id
                  FROM User u
                  JOIN Group_Users gu
                  ON u.user_id = gu.user_id
                  WHERE u.user_id = {};
                  """

    # Execute Query
    cursor.execute(group_query.format(user_id))

    # Initialize Group ID
    group_id = -1

    # Get Data from Cursor
    for result in (cursor):
        if (result[0] is not None):
            group_id = int(result[0])

    # Return Response To Caller
    return (render_template("portfolio.html", user_id = user_id, group_id = group_id, balance = balance, \
                                              stocks_owned = stocks_owned, stock_data = stock_info, navbar = ui.navbar(request)))

@app.route('/join_group',methods = ['GET','POST'])
@jwt_required(locations = ['cookies'])
def join_group():
    user_id = get_jwt_identity()
    cursor = cnx.cursor()

    if(request.method == "POST"):
        user_data = request.form
        input_group_id = user_data["group_id"]
        input_money = user_data["enter_money"]

        #if the user enters negative or zero
        if(int(input_money) <= 0):
            return (render_template("error.html", navbar = ui.navbar(request), msg = "you are required to give money to group"))

        #check if the user already in the group
        group_query = """
                      SELECT group_id
                      FROM User u
                      JOIN Group_Users gu
                      ON u.user_id = gu.user_id
                      WHERE u.user_id = {};
                      """

        cursor.execute(group_query.format(user_id))

        group_id = None

        # Get Data from Cursor
        for result in cursor:
            group_id = int(result[0])

        if (group_id is not None):
            print(group_id)
            return (render_template("error.html", navbar = ui.navbar(request), msg = "you already belong to a group, be loyal!"))

        group = None

        group_id = input_group_id

        query = """
                SELECT COUNT(*)
                FROM Group_Info
                WHERE group_id = {};
                """

        cursor.execute(query.format(group_id))

        for result in (cursor):
            group = True

        #get user balance
        input_token = (user_id,)
        balance = 0
        cursor.execute(get_user_balance,input_token)
        for user_balance in cursor:
            balance = int(user_balance[0])

        #if balance is not enough
        input_money = int(input_money)
        if(balance < input_money):
            db.session.commit()
            return (render_template("error.html", navbar = ui.navbar(request), msg = "Not enough money"))

        if (not(group)):
            query = """
                    INSERT INTO Group_Info (group_id, balance)
                    VALUES ({}, {});
                    """

            cursor.execute(query.format(group_id, input_money))
            cnx.commit()
        else:
            query = """
                    UPDATE Group_Info
                    SET balance = balance + {}
                    WHERE group_id = {};
                    """

            cursor.execute(query.format(input_money, group_id))
            cnx.commit()

        #update a group's balance using ORM
        input_token = (group_id,)
        group_balance = None
        cursor.execute(get_group_balance,input_token)
        for cur in cursor:
            group_balance = int(cur[0])

        #if the group_id does not exist
        if(group_balance is None):
            db.session.commit()
            return (render_template("error.html", navbar = ui.navbar(request), msg = "Invalid group id"))
        group_balance += input_money
        spec_group = Group_Info.query.filter_by(group_id = group_id).first()
        spec_group.balance = group_balance
        db.session.commit()

        #update a user's Balance using ORM
        balance -= input_money
        spec_user = User.query.filter_by(user_id = user_id).first()
        spec_user.balance = balance
        db.session.commit()

        query = """
                INSERT INTO Group_Users (group_id, user_id)
                VALUES ({}, {});
                """
                
        cursor.execute(query.format(group_id, user_id))
        cnx.commit()

        # new_group_member = Group_Users(group_id = group_id,user_id = user_id)
        # db.session.add(new_group_member)
        # db.session.commit()

        cursor.close()
        return render_template("group_join_success.html",navbar = ui.navbar(request))
    cursor.close()
    db.session.commit()
    return render_template("group_join.html",navbar = ui.navbar(request))

@app.route('/group_portfolio/<group_id>')
@jwt_required(locations = ['cookies'])
def group_portfolio(group_id):
    # Create Cursor
    cursor = cnx.cursor()

    # Query To Get All User Information
    group_query = """
                 SELECT s.stock_id, s.name, s.price, gs.amount
                 FROM Group_Info g
                 JOIN Group_Stock gs
                 ON g.group_id = gs.group_id
                 JOIN Stock s
                 ON gs.stock_id = s.stock_id
                 WHERE g.group_id = {};
                 """

    # Execute Query
    cursor.execute(group_query.format(group_id))

    # Initialize Stock Info List
    stock_info = list()

    # Fetch Results From Cursor
    for stock_id, stock_name, stock_price, stock_shares in (cursor):
        stock_info.append((stock_id, stock_name, stock_price, stock_shares))

    # Query To Get User Balance
    group_query = """
                 SELECT balance
                 FROM Group_Info
                 WHERE group_id = {};
                 """

    # Execute Query
    cursor.execute(group_query.format(group_id))

    # Initialize User Balance
    balance = 0

    # Get Data From Cursor
    for result in (cursor):
        balance = float(result[0])

    # Format User Balance
    balance = "{:,.2f}".format(balance)

    # Query To Get User Shares
    group_query = """
                 SELECT SUM(amount)
                 FROM Group_Stock
                 WHERE group_id = {};
                 """

    # Execute Query
    cursor.execute(group_query.format(group_id))

    # Initialize User Balance
    stocks_owned = 0

    # Get Data From Cursor
    for result in (cursor):
        if (result[0] is not None):
            stocks_owned = int(result[0])

    # Return Response To Caller
    return (render_template("group_portfolio.html", group_id = group_id, balance = balance, stocks_owned = stocks_owned, stock_data = stock_info, navbar = ui.navbar(request)))

@app.route('/group_buy/<group_id>', methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def group_buy(group_id):
    # Get Current User ID
    #user_id = get_jwt_identity()

    # Open Database Cursor
    cursor = cnx.cursor()

    # Detect For Post Method
    if (request.method == "POST"):
        # Get Group Data From Form
        db.engine.execute(repeatable_read)
        db.engine.execute(transaction_start)
        groupDetails = request.form
        stock_id = groupDetails["stock_id"]
        stock_number = groupDetails["number"]
        data = (int(stock_id),)

        # Get Stock Price
        cursor.execute(get_stock_by_stock_id, data)

        # Initialize Stock Data
        stock_price = None
        stock_share = None
        stock_name = ""

        # Fetch Data From Cursor
        for name, price, share in (cursor):
            stock_name = name
            stock_price = price
            stock_share = share

            # Verify Stock ID
            if(not(stock_price)):
                return (render_template("error.html", navbar = ui.navbar(request), msg = "Invalid stock ID. Please Go back and try again!"))

        # Get Group Balance
        cur_info = (group_id,)

        # Execute Query
        cursor.execute(get_group_balance, cur_info)

        # Initalize Group Balance
        balance = None

        # Fetch Group Data From Cursor
        for group_balance in (cursor):
            balance = group_balance[0]

        # Calculate Spent Money
        spent = stock_price * int(stock_number)

        # Calculate Remaining Funds
        remaining_funds = balance - spent

        # Verify Remaining Funds
        if(remaining_funds < 0):
            return (render_template("error.html", navbar = ui.navbar(request), msg = "Not Enough Balance!"))

        # Decrease Stock Share After Purchase
        stock_share = stock_share - int(stock_number)
        cursor.execute(update_stock_share.format(stock_share,stock_id))
        cnx.commit()

        # Update Group Balance
        cursor.execute(update_group_balance.format(remaining_funds,group_id))
        cnx.commit()

        # Get Transaction Number
        cursor.execute(get_transaction_number)

        # Initialize Transaction ID
        transaction_id = 0

        # Fetch Data From Cursor
        for x in cursor:
            transaction_id = x[0]

        # Increment Transaction ID
        transaction_id += 1

        # Update The Transaction Table
        today = datetime.date.today()
        nt = Transaction(transaction_id = transaction_id,amount = int(stock_number),date = today,price = stock_price)
        db.session.add(nt)
        db.session.commit()

        # Query To Insert Group Transaction
        query = """
                INSERT INTO Group_Transaction (transaction_id, type, group_id, stock_id)
                VALUES ({}, {}, {}, {});
                """

        # Execute Query
        cursor.execute(query.format(transaction_id, BUY, group_id, stock_id))

        # Commit Data To Database
        cnx.commit()

        # Format Confirmation Data
        confirmation_info = [stock_number,stock_id,stock_name,spent,remaining_funds]

        # Commit Data To Database
        db.engine.execute(transaction_commit)

        # Return Response To user
        return (render_template("confirmation_buy.html", data = confirmation_info, navbar = ui.navbar(request)))
    else:
        # Initialize Stock Data List
        stock_info = []

        # Execute Query To Get All Stock
        cursor.execute(get_stock)

        # Fetch Stock Data From Cursor
        for stock_id, name, price, share in (cursor):
            stock_info.append((stock_id,name,price,share))

        # Close Cursor
        cursor.close()

        # Return Response To User
        return (render_template("group_buy.html", group_id = group_id, data = stock_info, navbar = ui.navbar(request)))

@app.route('/group_sell/<group_id>', methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def group_sell(group_id):
    # Get Current User ID
    #user_id = get_jwt_identity()

    # Open Database Cursor
    cursor = cnx.cursor()

    # Detect For Post Method
    if (request.method == "POST"):
        # Start Transaction
        db.engine.execute(repeatable_read)
        db.engine.execute(transaction_start)

        # Get Group Details From POST Request
        groupDetails = request.form
        stock_id = int(groupDetails["stock_id"])
        sale_amount = int(groupDetails["number"])

        # Query To Get Group Stock By Stock ID
        query = """
                SELECT gs.stock_id, gs.amount, st.name, st.price
                FROM Group_Stock gs JOIN Stock st ON gs.stock_id = st.stock_id
                WHERE gs.group_id = {} AND gs.stock_id = {};
                """

        # Execute Query
        cursor.execute(query.format(group_id, stock_id))

        # Initialize Stock Data
        stock_name = stock_price = stock_shares = None

        # Fetch Data From Cursor
        for _, shares, name, price in (cursor):
            stock_shares = int(shares)
            stock_price = float(price)
            stock_name = str(name)

        # Verify Remaining Funds
        if (not(stock_name)):
            return (render_template("error.html", navbar = ui.navbar(request), msg = "You Don't Own That Stock!"))

        # Update Market Share Amount
        stock_shares += int(sale_amount)

        # Increase Stock Shares After Purchase
        cursor.execute(update_stock_share.format(stock_shares,stock_id))
        cnx.commit()

        # Query To Get Group Balace
        query = """
                SELECT balance
                FROM Group_Info
                WHERE group_id = {};
                """

        # Execute Query
        cursor.execute(query.format(group_id))

        # Initialize group Balance
        group_balance = None

        # Fetch Data From Cursor
        for balance in (cursor):
            group_balance = float(balance[0])

        # Calculate Earnings
        earnings = stock_price * sale_amount

        # Update Group Balance
        group_balance += earnings

        # Update Group Balance
        cursor.execute(update_group_balance.format(group_balance,group_id))
        cnx.commit()

        # Get Transaction Number
        cursor.execute(get_transaction_number)

        # Initialize Transaction ID
        transaction_id = 0

        # Fetch Data From Cursor
        for x in cursor:
            transaction_id = x[0]

        # Increment Transaction ID
        transaction_id += 1

        # Update The Transaction Table
        today = datetime.date.today()
        nt = Transaction(transaction_id = transaction_id,amount = int(sale_amount),date = today,price = stock_price)
        db.session.add(nt)
        db.session.commit()

        # Query To Insert User Transaction
        query = """
                INSERT INTO Group_Transaction (transaction_id, type, group_id, stock_id)
                VALUES ({}, {}, {}, {});
                """

        # Execute Query
        cursor.execute(query.format(transaction_id, SELL, group_id, stock_id))

        # Commit Data To Database
        cnx.commit()

        # End Transaction
        db.engine.execute(transaction_commit)

        # Close Cursor
        cursor.close()

        # Form Confirmation Info
        confirmation_info = [sale_amount, stock_id, stock_name, earnings, group_balance]

        # Return Response To user
        return (render_template("confirmation_sell.html", data = confirmation_info, navbar = ui.navbar(request)))
    else:
        # Initialize Stock Data List
        stock_info = []

        # Get Stocks In User Possession
        query = """
                SELECT gs.stock_id, st.name, amount, price, share
                FROM Group_Stock gs JOIN Stock st ON gs.stock_id = st.stock_id
                WHERE gs.group_id = {};
                """

        # Execute Query To Get All Stock
        cursor.execute(query.format(group_id))

        # Fetch Stock Data From Cursor
        for stock_id, name, amount, price, share in (cursor):
            stock_info.append((stock_id, name, amount, price, share))

        # Close Cursor
        cursor.close()

        # Return Response To User
        return (render_template("group_sell.html", group_id = group_id, navbar = ui.navbar(request), data = stock_info))

# End Navbar Functions--------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/watchlist', methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def watchlist():
    # Get Current User ID
    user_id = get_jwt_identity()

    # Open Database Cursor
    cursor = cnx.cursor()

    if (request.method == 'POST'):
        # Fetch User Input Data
        user_data = request.form
        watch_input = user_data["watch_input"]

        # Get Data From Input
        update_type, stock_name = watch_input.split(" ")

        # Define Watchlist Query
        update_query = None

        # Determine Query Type
        if (update_type == "Watch"):
            update_query = """
                           INSERT INTO Watchlist (user_id, stock_id)
                           VALUES ({}, (SELECT stock_id FROM Stock WHERE name = "{}"));
                           """
        else:
            update_query = """
                           DELETE FROM Watchlist
                           WHERE user_id = {} AND stock_id = (SELECT stock_id FROM Stock WHERE name = "{}");
                           """

        # Execute Query
        cursor.execute(update_query.format(user_id, stock_name))

    # Query To Get Watchlist Items
    watchlist_query = """
                      SELECT s.stock_id, s.name, s.price, s.share
                      FROM Watchlist w
                      JOIN Stock s
                      ON w.stock_id = s.stock_id
                      WHERE w.user_id = {};
                      """

    # Execute Query
    cursor.execute(watchlist_query.format(user_id))

    # Initialize Data List
    watch_info = []

    # Fetch Data From Cursor
    for stock_id, stock_name, stock_price, stock_shares in cursor:
        watch_info.append((stock_id, stock_name, stock_price, stock_shares))

    # Return Response To User
    return (render_template("watchlist.html", data = watch_info, navbar = ui.navbar(request)))

@app.route("/user_transactions", methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def user_transactions():
    # Get Current User ID
    user_id = get_jwt_identity()

    # Creating the cursor
    cursor = cnx.cursor()

    #transaction list
    t_list = []

    # Execute The Query To Get User Transactions
    cursor.execute(get_transactions.format(user_id))

    # Get Data From Cursor
    for stock_id, name, amount, transaction_type, price, date in (cursor):
        # Add Transactions To List
        t_list.append((stock_id, name, transaction_type, amount, price, amount * price, date))

    # Close Cursor
    cursor.close()

    # Return Reponse To User
    return (render_template("transactions_user.html", data = t_list, navbar = ui.navbar(request)))

@app.route('/group_transactions/<group_id>')
@jwt_required(locations = ['cookies'])
def group_transactions(group_id):
    cursor = cnx.cursor()
    transaction_query = """
                        SELECT g.stock_id, s.name, t.amount, g.type, t.price, t.date
                        FROM Transaction t
                        JOIN Group_Transaction g
                        ON t.transaction_id = g.transaction_id
                        JOIN Stock s
                        ON g.stock_id = s.stock_id
                        WHERE g.group_id = {};
                        """
    cursor.execute(transaction_query.format(group_id))
    group_transaction = list()
    for stock_id, stock_name, amount, transaction_type, price, date in cursor:
        total_cost = amount * price
        group_transaction.append((stock_id, stock_name, transaction_type, amount, price, total_cost, date))
    return render_template("transactions_group.html", data = group_transaction, navbar = ui.navbar(request))

# End Portfolio Functions----------------------------------------------------------------------------------------------------------------------------------------------------

# Start Server
if __name__ == "__main__":
    # Start Flask App
    app.run(debug = True)
