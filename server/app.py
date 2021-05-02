import os
import ui
import time
import yaml
import globl
import random
import datetime
import mysql.connector

from collections import defaultdict
from multiprocessing import Process
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, redirect, render_template, make_response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, set_access_cookies, unset_access_cookies

# End Imports---------------------------------------------------------------------------------------------------------------------------------------------------------

# Maximum Price Change
MAXIMUM_PRICE_CHANGE = 20

# Transaction Constants
BUY, SELL = 1, 0

# Server Constants----------------------------------------------------------------------------------------------------------------------------------------------------

# Load Database Configuration
dbconf = yaml.load(open(os.environ["DATABASE_CONFIG"]), yaml.Loader)

# Establish Database Connection
cnx = mysql.connector.connect(user = dbconf['mysql_user'], password = dbconf['mysql_password'],
                              host = dbconf['mysql_host'], database = dbconf['mysql_db'])

# End Database Connector----------------------------------------------------------------------------------------------------------------------------------------------

# Query for getting all current stock information
get_stock = "SELECT stock_id, name, price, share FROM Stock;"
user_account_money = "SELECT balance FROM User Where user_id = %s;"
get_stock_by_stock_name = "SELECT stock_id,price,share FROM Stock Where name = %s;"
get_stock_by_stock_id = "SELECT name,price,share FROM Stock Where stock_id = %s;"
get_user_balance = "SELECT balance FROM User Where user_id = %s;"
get_watchlist = "SELECT stock_id FROM Watchlist Where user_id = %s AND stock_id = %s;"
get_transaction_number = "SELECT COUNT(*) FROM User_Transaction"
get_amount_bought = "SELECT SUM(t.amount) FROM Transaction t, User_Transaction ut WHERE t.transaction_id = ut.transaction_id AND ut.type = 1 AND stock_id = %s AND user_id = %s;"
get_amount_sold =  "SELECT SUM(t.amount) FROM Transaction t, User_Transaction ut WHERE t.transaction_id = ut.transaction_id AND ut.type = 0 AND stock_id = %s AND user_id = %s;"
get_transactions = """
                   SELECT U.stock_id, S.name, T.amount, U.type AS transaction_type, T.price
                   FROM User_Transaction AS U JOIN Transaction AS T ON U.transaction_id = T.transaction_id
                   JOIN Stock AS S
                   ON U.stock_id = S.stock_id
                   WHERE U.user_id = {}
                   """
get_max_update_id = "SELECT MAX(update_id) FROM Stock_Update"
get_number_of_stock = "SELECT MAX(stock_id) FROM Stock"
update_stock_share = "UPDATE Stock SET share = %s WHERE stock_id = %s;"
update_user_balance = "UPDATE User SET balance = %s WHERE user_id = %s;"
insert_user_transaction = "INSERT INTO User_Transaction (transaction_id,type,user_id,stock_id) VALUES (%s,%s,%s,%s);"
insert_transaction = "INSERT INTO Transaction (transaction_id,amount,date,price) VALUES (%s,%s,%s,%s);"
insert_watchlist = "INSERT INTO Watchlist (user_id,stock_id) VALUES (%s, %s);"

# End SQL Queries-----------------------------------------------------------------------------------------------------------------------------------------------------

# Create Flask Application
app = Flask(__name__)

# Configure Flask Application
app.config['SECRET_KEY'] = '537e3275e714ff299e49'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:' + dbconf['mysql_password'] + '@localhost/' + dbconf['mysql_db']
app.config.setdefault('JWT_ACCESS_COOKIE_NAME', 'access_token_cookie')

# End Server Initialization----------------------------------------------------------------------------------------------------------------------------------------------------

# Intiialize ORM Database
db = SQLAlchemy(app)

# Verify SQL_ALCHEMY_DB
if (db is None):
    raise ValueError("db is None")

# Set ORM Database Reference
globl.SQL_ALCHEMY_DB = db

# Import ORM Module
import orm

# Import Tables From ORM
from orm import User
from orm import Stock
from orm import Stock_Update

# End ORM Initialization----------------------------------------------------------------------------------------------------------------------------------------------------

def change_stock_tables():
    # update_stock_every_5_minutes()
    pass

#update the stock every 5 minutes in background
#!!!IMPORTANT
#Warning: This scheduler will run twice if debug mode is ON.
#The Werkzeug reloader spawns a child process so that it can restart that process each time your code changes."
#Werkzeug is the library that supplies Flask with the development server

scheduler = BackgroundScheduler()
scheduler.add_job(change_stock_tables, 'interval', minutes = 1)
scheduler.start()

# End Server Jobs-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Set JWT Token Location
JWT_TOKEN_LOCATION = ['cookies']

# Configure JWT Manager
jwt = JWTManager(app)

@jwt.unauthorized_loader
def unauthorized(callback):
    return (render_template('401.html', navbar = ui.navbar(request)))

# End Authentication Initialization------------------------------------------------------------------------------------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    # Return 404 page
    return (render_template('404.html', navbar = ui.navbar(request))), 404

@app.route("/", methods=['GET', 'POST'])
def home():
    if (request.method == 'POST'):
        # Fetch user's input data
        user_data = request.form
        #if a user clicks on buy stock
        if user_data.get("search"):
            search_info = user_data["search_info"]
            url = '/search/' + search_info
            return redirect(url)
        if user_data.get("buy"):
            return redirect('/buy')
        #if a user clicks on sell stock
        if user_data.get("sell"):
            return redirect('/sell')
        #if a user wants to register
        if user_data.get("register"):
            return redirect('/register')
        #if a user wants to view the transaction
        if (user_data.get("transactions")):
            return (redirect("/transactions"))

    # Stock Data
    num_stocks = num_shares = 0

    # Open Database Cursor
    cursor = cnx.cursor()

    # Query To Fetch Number Of Stocks In Market
    query = """
            SELECT COUNT(*) AS result
            FROM Stock;
            """

    # Execute Query
    cursor.execute(query)

    # Fetch Data
    for result in (cursor):
        num_stocks = int(result[0])

    # Query To Fetch Number Of Stocks In Market
    query = """
            SELECT SUM(share) AS result
            FROM Stock;
            """

    # Execute Query
    cursor.execute(query)

    # Fetch Data
    for result in (cursor):
        num_shares = int(result[0])

    # Stock Market Data
    transaction_cnt = avg_buy_price = avg_sell_price = None

    # Query To Fetch Number Of Transactions In 24hr
    query = """
            SELECT COUNT(*) AS result
            FROM Transaction
            WHERE 86400 <= UNIX_TIMESTAMP() - date;
            """

    # Execute Query
    cursor.execute(query)

    # Fetch Data
    for result in (cursor):
        transaction_cnt = int(result[0])

    # Query To Fetch Number Of Stocks In Market
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

    # Format Prices
    avg_buy_price = "{:.2f}".format(sum(t[1] for t in cursor if (t[0] == BUY)))
    avg_sell_price = "{:.2f}".format(sum(t[1] for t in cursor if (t[0] == SELL)))

    # Get Newest Historical Stock Prices
    query = """
            SELECT stock_id, price_change AS avg_price
            FROM Stock_Update WHERE update_id = 0
            GROUP BY stock_id
            UNION
            SELECT stock_id, price_change AS avg_price
            FROM Stock_Update WHERE update_id = 49
            GROUP BY stock_id;
            """

    # Execute Query
    cursor.execute(query)

    stocks = defaultdict(int)

    for result in (cursor):
        if (not(result[0] in stocks)):
            stocks[result[0]] = result[1]
        else:
            stocks[result[0]] += result[1]
            stocks[result[0]] /= 2

    # Get Stocks Ranked By Growth
    stock_rank = sorted(stocks.items(), key = lambda x : x[1], reverse = True)

    # Initialize Name List
    namelist = []

    # Initialize Data Lists
    datalists = []
    for stock_id, _ in (stock_rank[:2]):
        query = """
                SELECT price_change
                FROM Stock_Update
                WHERE stock_id = {}
                """
        cursor.execute(query.format(stock_id))
        datalist = [pc[0] for pc in cursor]
        datalists.append(datalist)

        query = """
                SELECT name
                FROM Stock
                WHERE stock_id = {}
                """

        cursor.execute(query.format(stock_id))

        # Fetch Data
        for result in (cursor):
            namelist.append(str(result[0]))

    # Close Cursor
    cursor.close()

    # Render Index Template
    return (render_template('index.html', navbar = ui.navbar(request), num_stocks = num_stocks, num_shares = num_shares, \
                            transaction_cnt = transaction_cnt, avg_buy_price = avg_buy_price, avg_sell_price = avg_sell_price, \
                            stock_name_1 = namelist[0], stock_name_2 = namelist[1], price_arr_1 = str(datalists[0]), price_arr_2 = str(datalists[1])))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        # Fetch user's input data
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
        response = make_response(redirect('/users/{}'.format(obj.user_id)))

        # Create Access Token
        access_token = create_access_token(identity = input_user_id)

        # Set Access Cookies In Response
        set_access_cookies(response, access_token)

        # Return Response To Client
        return (response)

    # Render Default Login Page
    return (render_template('login.html', navbar = ui.navbar(request), error = False))

@app.route("/logoff", methods=['GET', 'POST'])
@jwt_required(locations = ['cookies'])
def logoff():
    # Fetch User Access Token
    response = make_response(redirect('/login'))

    # Revoke Access Cookies
    unset_access_cookies(response)

    # Send Response
    return (response)

@app.route("/register", methods=['GET', 'POST'])
def register():
    cursor = cnx.cursor()
    if (request.method == 'POST'):
        # Fetch user's input data
        user_data = request.form
        input_user_id = user_data["user_id"]
        input_password = user_data["password"]
        confirm_password = user_data["confirm_password"]
        #check if password equals confirm_password
        if(input_password != confirm_password):
            return "Password doesn't match!"
        cursor_input = (input_user_id,)
        cursor.execute(get_user_balance,cursor_input)
        #check if the user id has already existed
        balance = -9999
        for cur in cursor:
            balance = cur
        if(balance != -9999):
            return "User ID exists"
        #use ORM to add users
        new_user = User(user_id = input_user_id,balance = 25000, password = input_password)
        db.session.add(new_user)
        db.session.commit()

        # Get User Object Using ORM
        obj = User.query.filter_by(user_id = input_user_id, password = input_password).first()

        # Verify Return From Database
        if (obj is None):
            # Update View
            return (render_template('login.html', navbar = ui.navbar(request), error = True))

        # Create Response
        response = make_response(render_template('register_success.html', navbar = ui.navbar(request)))

        # Create Access Token
        access_token = create_access_token(identity = input_user_id)

        # Set Access Cookies In Response
        set_access_cookies(response, access_token)

        # Return Response To Client
        return (response)

    cursor.close()
    return (render_template('register.html', navbar = ui.navbar(request)))

@app.route("/search/<search_info>", methods=['GET', 'POST'])
def search(search_info):
    cursor = cnx.cursor()
    data = search_function(search_info,cursor)
    if(data == -1):
        return "Stock not found"
    cursor.close()
    return render_template("search.html",data = data, navbar = ui.navbar(request))

@app.route("/stock/<name>", methods = ["GET", "POST"])
@app.route("/stock", methods = ["GET", "POST"])
def stock():
    # todo, list top 10 stocks, all stocks
    return "hello"

# Page to display the transaciton history
@app.route("/transactions", methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def transaction():
    # Creating the cursor
    cursor = cnx.cursor()

    #user details (FOR now)
    user_id = 0

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

# Page to display when user clicks buy stock
@app.route('/buy', methods = ["GET", "POST"])
@jwt_required(locations = ['cookies'])
def buy():
    # Create Database Cursor
    cursor = cnx.cursor()

    if(request.method == 'POST'):
        #if a user clicks on buy button,record his response
        userDetails = request.form
        stock_id = userDetails["stock_id"]
        number = userDetails["number"]
        data = (int(stock_id),)

        #get stock price for the stock user want to buy
        cursor.execute(get_stock_by_stock_id,data)
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
            return "Invalid stock ID. Please Go back and try again"

        #get user balance
        #TODO in the cur_info below, we should input the current user_id instead of 0
        cur_info = (0,)
        cursor.execute(get_user_balance,cur_info)
        balance = -5
        for user_balance in cursor:
            balance = user_balance[0]
        spent = stock_price * int(number)
        remaining = balance - spent
        #if user does not have enough balance
        if(remaining < 0):
            return "Not enough balance"

        #increase stock share after user buys it
        stock_share = stock_share + int(number)
        update_info = (stock_share,stock_id)
        cursor.execute(update_stock_share,update_info)
        cnx.commit()

        #update user_balance
        #TODO update the current user_id here
        update_info = (remaining,0)
        cursor.execute(update_user_balance,update_info)
        cnx.commit()

        #update Watchlist
        #TODO put current user_id instead of 0
        get_info = (0,stock_id)
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

        #update transaction table
        insert_info = (transaction_id,int(number),0,stock_price)
        cursor.execute(insert_transaction,insert_info)
        cnx.commit()


        #update user_transaction
        #TODO update into current user_id below
        insert_info = (transaction_id,1,0,stock_id)
        cursor.execute(insert_user_transaction,insert_info)
        cnx.commit()

        #print confirmation table into /templates/confirmation.html
        confirmation_info = [number,stock_id,stock_name,spent,remaining];


        return render_template("confirmation.html", data = confirmation_info, navbar = ui.navbar(request))


    #initialize purchase page
    stock_info = []

    #execute the query for getting all stock information
    cursor.execute(get_stock)

    #display stock in the UI interface
    for stock_id, name, price, share in cursor:
        stock_info.append((stock_id,name,price,share))

    cursor.close()
    #copy all of the code inside buy_template.html into buy.html
    #cursor.close()
    return render_template("buy.html", data = stock_info, navbar = ui.navbar(request))

@app.route('/sell')
@jwt_required(locations = ['cookies'])
def sell():
    return (render_template('sell.html', navbar = ui.navbar(request)))

@app.route('/transaction_history/<user_id>')
@jwt_required(locations = ['cookies'])
def transaction_history(user_id):
    cursor = cnx.cursor()
    transaction_query = """
                        SELECT *
                        FROM Transaction t
                        JOIN User_Transaction u
                        ON t.transaction_id = u.transaction_id
                        WHERE u.user_id = %s;
                        """
    cursor.execute(transaction_query, user_id)
    return 0

@app.route('/user/<user_id>')
@jwt_required(locations = ['cookies'])
def user_info(user_id):
    cursor = cnx.cursor()
    user_query = "SELECT * FROM User u WHERE u.user_id = %s;"
    cursor.execute(user_query, user_id)
    return 0

@app.route('/watchlist/<user_id>')
@jwt_required(locations = ['cookies'])
def watchlist(user_id):
    cursor = cnx.cursor()
    watchlist_query = """
                        SELECT *
                        FROM Watchlist w
                        JOIN Stock s
                        ON w.stock_id = s.stock_id
                        WHERE w.user_id = %s;
                        """
    cursor.execute(watchlist_query, user_id)
    return 0

# End Router Functions----------------------------------------------------------------------------------------------------------------------------------------------------

def search_function(search_word,cursor):
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

def stock_table_job():
    # Create Database Cursor
    cursor = cnx.cursor()

    # Query For Latest Stock Prices
    latest_stock_prices = """
                          SELECT stock_id, price
                          FROM Stock;
                          """

    # Execute Query
    cursor.execute(latest_stock_prices)

    # Initialize Stock Dictionary
    stock_prices = defaultdict(float)

    # Get All Stock Prices
    for stock_id, price in (cursor):
        stock_prices[stock_id] = price

    # Create New Stock History
    for stock_id in sorted(stock_prices):
        # Get Stock Price
        new_price = stock_prices[stock_id]

        # Get Increase Or Decrease Direction
        id = int(random.randint(0, 1))

        # Calculate Price Delta
        delta = float(random.random() * MAXIMUM_PRICE_CHANGE) * (-1 if (id == 0) else 1)

        if (new_price + delta > 10):
            # Calculate New Price
            new_price += delta

        # Create Dynamic SQL Query
        history_update_query = """
                               UPDATE Stock
                               SET price = {:.2f}
                               WHERE stock_id = {}
                               """
        # Insert New Stock Tuple
        cursor.execute(history_update_query.format(new_price, stock_id))

        # Commit Data To Database
        cnx.commit()

    # Close Database Cursor
    cursor.close()

def stock_update_table_job():
    # Create Database Cursor
    cursor = cnx.cursor()

    # Query For Latest Stock Prices
    latest_stock_prices = """
                          SELECT stock_id, price
                          FROM Stock;
                          """

    # Execute Query
    cursor.execute(latest_stock_prices)

    # Initialize Latest Update Idenfitier
    latest_update_id = None

    # Query For Latest Stock Prices
    latest_stock_update = """
                          SELECT COUNT(*)
                          FROM Stock_Update;
                          """

    # Execute Query
    cursor.execute(latest_stock_update)

    # Fetch Result From Cursor
    for result in (latest_stock_update):
        latest_update_id = int(latest_stock_update[0]) + 1

    # Initialize Stock Dictionary
    stock_prices = defaultdict(float)

    # Get All Stock Prices
    for stock_id, price in (cursor):
        stock_prices[stock_id] = price

    # Create New Stock History
    for stock_id in sorted(stock_prices):
        # Get Stock Price
        new_price = stock_prices[stock_id]

        # Get Increase Or Decrease Direction
        id = int(random.randint(0, 1))

        # Calculate Price Delta
        delta = float(random.random() * MAXIMUM_PRICE_CHANGE) * (-1 if (id == 0) else 1)

        if (new_price + delta > 10):
            # Calculate New Price
            new_price += delta

        # Create Dynamic SQL Query
        history_update_query = """
                               INSERT INTO Stock_Update (update_id, stock_id, price_change)
                               VALUES (%s, %s, %s);
                               """
        # Format History Tuple
        history_data = (int(latest_update_id), int(stock_id), float(new_price))

        # Insert New Stock Tuple
        cursor.execute(history_update_query, history_data)

        # Commit Data To Database
        cnx.commit()

    # Close Database Cursor
    cursor.close()

# #changed the stock price every 5 minutes and add the record into stock_update
def update_stock_every_5_minutes():
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

# Start Server
if __name__ == "__main__":
    # Start Flask App
    app.run(debug=True)
