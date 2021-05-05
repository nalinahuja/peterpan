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
                   SELECT U.stock_id, S.name, T.amount, U.type AS transaction_type, T.price
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
                     SET share = %s
                     WHERE stock_id = %s;
                     """

update_user_balance = """
                      UPDATE User
                      SET balance = %s
                      WHERE user_id = %s;
                      """

insert_user_transaction = """
                          INSERT INTO User_Transaction (transaction_id, type, user_id, stock_id)
                          VALUES (%s,%s,%s,%s);
                          """

insert_transaction = """
                     INSERT INTO Transaction (transaction_id, amount, date, price)
                     VALUES (%s,%s,%s,%s);
                     """

insert_watchlist = """
                   INSERT INTO Watchlist (user_id,stock_id)
                   VALUES (%s, %s);
                   """

repeatable_read = "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;"

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

def search_function(search_word, cursor):
    #check if the user
    input_token = (search_word,)
    result = []
    stock_id = -1
    stock_name = ""
    stock_price = -1
    stock_share = -1
    if(search_word.isnumeric()):
        #if the user inputs the stock id
        cursor.execute(get_stock_by_stock_id,input_token)
        for name,price,share in cursor:
            stock_price = price
            stock_share = share
            stock_name = name
        #stock exists
        if(stock_price != -1):
            result.append(search_word)
            result.append(stock_name)
            result.append(stock_price)
            result.append(stock_share)
            return result
    else:
        #if the user inputs the stock name
        cursor.execute(get_stock_by_stock_name,input_token)
        for id,price,share in cursor:
            stock_id = id
            stock_share = share
            stock_price = price
        #stock exists
        if(stock_id != -1):
            result.append(stock_id)
            result.append(search_word)
            result.append(stock_price)
            result.append(stock_share)
            return result
    return -1

# TODO: Fix Function
def update_stock():
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
    avg_buy_price = "{:.2f}".format(sum(t[1] for t in cursor if (t[0] == BUY)))
    avg_sell_price = "{:.2f}".format(sum(t[1] for t in cursor if (t[0] == SELL)))

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
        new_user = User(user_id = input_user_id,balance = 25000, password = input_password)
        db.session.add(new_user)
        db.session.commit()

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

@app.route("/stocks/<name>", methods = ["GET", "POST"])
def single_stock(name):
    # Open Database Cursor
    cursor = cnx.cursor()

    # Query To Get Stock Data By Name
    query = """
            SELECT price, share
            FROM Stock
            WHERE name = "{}";
            """

    # Get Stock Data By Name
    cursor.execute(query.format(name))

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
    cursor.execute(query.format(name))

    # Get Result From Cursor
    si = [si[0] for si in (cursor)]

    # Determine Stock Existence
    if((stock_price is None) or (stock_share is None)):
        # Return Response To User
        return (render_template("error.html", navbar = ui.navbar(request), msg = "That stock does not exist, please try another stock."))
    else:
        # Format Stock Data As Tuple
        stock_info = [name, stock_price, stock_share]

        # Return Response To User
        return (render_template("stock_single.html", stock_history = si, data = stock_info, navbar = ui.navbar(request)))

@app.route('/buy', methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def buy():
    # Get Current User ID
    curr_user_id = get_jwt_identity()

    # Create Database Cursor
    cursor = cnx.cursor()

    # Set Transaction Level
    db.engine.execute(repeatable_read)
    db.engine.execute(transaction_start)

    # Detect If Post Method
    if (request.method == 'POST'):
        #if a user clicks on buy button,record his response
        userDetails = request.form
        stock_id = userDetails["stock_id"]
        number = userDetails["number"]
        data = (int(stock_id),)

        #get stock price for the stock user want to buy
        cursor.execute(get_stock_by_stock_id, data)
        stock_price = 0
        stock_share = 0
        stock_name = ""
        for name,price,share in cursor:
            #print(price)
            stock_name = name
            stock_price = price
            stock_share = share
        #if there is no stock price
        if(stock_price == 0):
            return (render_template("error.html", navbar = ui.navbar(request), msg = "Invalid stock ID. Please Go back and try again!"))

        #get user balance
        cur_info = (curr_user_id,)
        cursor.execute(get_user_balance,cur_info)
        balance = -5
        for user_balance in cursor:
            balance = user_balance[0]
        spent = stock_price * int(number)
        remaining = balance - spent
        #if user does not have enough balance
        if(remaining < 0):
            return (render_template("error.html", navbar = ui.navbar(request), msg = "Not Enough Balance!"))

        #increase stock share after user buys it
        stock_share = stock_share + int(number)
        update_info = (stock_share,stock_id)
        cursor.execute(update_stock_share,update_info)
        cnx.commit()

        #update user_balance
        update_info = (remaining,curr_user_id)
        cursor.execute(update_user_balance,update_info)
        cnx.commit()

        #update Watchlist
        get_info = (curr_user_id,stock_id)
        cursor.execute(get_watchlist,get_info)
        check = -1
        for id in cursor:
            check = id
        #there is no same (stock_id,user_id) in watchlist
        if(check == -1):
            cursor.execute(insert_watchlist,get_info)
            cnx.commit()

        #update transaction
        #get tranaction_id
        cursor.execute(get_transaction_number)
        transaction_id = 0
        for x in cursor:
            transaction_id = x[0]
        transaction_id += 1
        #update transaction table
        #update the stock schema in order to make this query work
        today = datetime.date.today()
        insert_info = (transaction_id,int(number),today,stock_price)
        cursor.execute(insert_transaction,insert_info)
        cnx.commit()

        #update user_transaction
        insert_info = (transaction_id,1,curr_user_id,stock_id)
        cursor.execute(insert_user_transaction,insert_info)
        cnx.commit()

        #print confirmation table into /templates/confirmation.html
        confirmation_info = [number,stock_id,stock_name,spent,remaining]

        db.engine.execute(transaction_commit)
        return render_template("confirmation_buy.html", data = confirmation_info, navbar = ui.navbar(request))

    #initialize purchase page
    stock_info = []

    #execute the query for getting all stock information
    cursor.execute(get_stock)

    #display stock in the UI interface
    for stock_id, name, price, share in cursor:
        stock_info.append((stock_id,name,price,share))

    cursor.close()

    #copy all of the code inside buy_template.html into buy.html
    db.engine.execute(transaction_commit)
    return render_template("buy.html", data = stock_info, navbar = ui.navbar(request))

@app.route('/sell', methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def sell():
    # Get Current User ID
    curr_user_id = get_jwt_identity()

    # TODO
    return ""

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
                 WHERE u.user_id = %s;
                 """

    # Execute Query
    cursor.execute(user_query, user_id)

    # Initialize User Info List
    user_info = list()

    # Fetch Results From Cursor
    for stock_id, stock_name, stock_price, stock_shares in (cursor):
        user_info.append((stock_id, stock_name, stock_price, stock_shares))

    # Return Response To Caller
    return (render_template("user.html", data = user_info, navbar = ui.navbar(request)))

# End Navbar Functions--------------------------------------------------------------------------------------------------------------------------------------------------------

# Page to display the transaciton history
@app.route("/transactions", methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def transaction():
    # Get Current User ID
    user_id = get_jwt_identity()

    # Creating the cursor
    cursor = cnx.cursor()

    #transaction list
    t_list = []

    #executing the query to get the transaction info
    cursor.execute(get_transactions.format(user_id))
    for stock_id, name, amount, transaction_type, price in cursor:
        s_id = stock_id
        t_type = transaction_type
        s_name = stock_id
        t_amount = amount
        total_cost = amount * price

        t_list.append((s_id, t_type, s_name, t_amount, total_cost))

    cursor.close()

    return render_template("transactions.html", data = t_list, navbar = ui.navbar(request))

@app.route('/group_transaction_history/<group_id>')
@jwt_required(locations = ['cookies'])
def transaction_history(group_id):
    cursor = cnx.cursor()
    transaction_query = """
                        SELECT g.stock_id, s.name, t.amount, g.type, t.price, t.date
                        FROM Transaction t
                        JOIN Group_Transaction g
                        ON t.transaction_id = g.transaction_id
                        JOIN Stock s
                        ON g.stock_id = s.stock_id
                        WHERE g.group_id = %s;
                        """
    cursor.execute(transaction_query, group_id)
    group_transaction = list()
    for stock_id, stock_name, amount, transaction_type, price, date in cursor:
        total_cost = amount * price
        group_transaction.append((stock_id, stock_name, transaction_type, amount, price, total_cost, date))
    return render_template("group_transactions.html", data = group_transaction, navbar = ui.navbar(request))

@app.route('/watchlist', methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def watchlist():
    # Get Current User ID
    user_id = get_jwt_identity()

    # Open Database Cursor
    cursor = cnx.cursor()

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

    watch_info = list()
    for stock_id, stock_name, stock_price, stock_shares in cursor:
        watch_info.append((stock_id, stock_name, stock_price, stock_shares))

    return (render_template("watchlist.html", data = watch_info, navbar = ui.navbar(request)))

# End External Functions----------------------------------------------------------------------------------------------------------------------------------------------------

# Start Server
if __name__ == "__main__":
    # Start Flask App
    app.run(debug=True)
