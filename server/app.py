import os
import ui
import yaml
import globl
import mysql.connector

from collections import defaultdict
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, redirect, render_template

# End Imports---------------------------------------------------------------------------------------------------------------------------------------------------------

# Load Database Configuration
dbconf = yaml.load(open(os.environ["DATABASE_CONFIG"]), yaml.Loader)

# Establish Database Connection
cnx = mysql.connector.connect(user = dbconf['mysql_user'], password = dbconf['mysql_password'],
                              host = dbconf['mysql_host'], database = dbconf['mysql_db'])

# End Database Connector----------------------------------------------------------------------------------------------------------------------------------------------

# Database Constants
BUY, SELL = 1, 0

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
update_stock_share = "UPDATE Stock SET share = %s WHERE stock_id = %s;"
update_user_balance = "UPDATE User SET balance = %s WHERE user_id = %s;"
insert_user_transaction = "INSERT INTO User_Transaction (transaction_id,type,user_id,stock_id) VALUES (%s,%s,%s,%s);"
insert_transaction = "INSERT INTO Transaction (transaction_id,amount,date,price) VALUES (%s,%s,%s,%s);"
insert_watchlist = "INSERT INTO Watchlist (user_id,stock_id) VALUES (%s, %s);"

# End SQL Queries-----------------------------------------------------------------------------------------------------------------------------------------------------

# Create Flask Application
app = Flask(__name__)

# Configure Flask Application
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:' + dbconf['mysql_password'] + '@localhost/' + dbconf['mysql_db']

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
from orm import User
# End ORM Initialization----------------------------------------------------------------------------------------------------------------------------------------------------

# Route to landing page
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
    return (render_template('index.html', navbar = ui.navbar(), num_stocks = num_stocks, num_shares = num_shares, transaction_cnt = transaction_cnt, avg_buy_price = avg_buy_price, avg_sell_price = avg_sell_price, stock_name_1 = namelist[0], stock_name_2 = namelist[1], price_arr_1 = str(datalists[0]), price_arr_2 = str(datalists[1])))

@app.route("/login", methods=['GET', 'POST'])
def login():
    return (render_template('login.html', navbar = ui.navbar()))

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
        return (render_template('register_success.html', navbar = ui.navbar()))
    cursor.close()
    return (render_template('register.html', navbar = ui.navbar()))


#route for search page
@app.route("/search/<search_info>", methods=['GET', 'POST'])
def search(search_info):
    cursor = cnx.cursor()
    data = search_function(search_info,cursor)
    if(data == -1):
        return "Stock not found"
    cursor.close()
    return render_template("search.html",data = data, navbar = ui.navbar())



@app.route("/stock/<name>", methods = ["GET", "POST"])
def stock(name):
    # todo, list the stock with the name
    return name

@app.route("/stock", methods = ["GET", "POST"])
def stockf():
    # todo, list top 10 stocks, all stocks
    return "hello"

# Page to display the transaciton history
@app.route("/transactions", methods = ["GET", "POST"])
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

    return render_template("transactions.html", data = t_list, navbar = ui.navbar())

# Page to display when user clicks buy stock
@app.route('/buy', methods = ["GET", "POST"])
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


        return render_template("confirmation.html", data = confirmation_info, navbar = ui.navbar())


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
    return render_template("buy_page.html", data = stock_info, navbar = ui.navbar())

# Page to display when user clicks sell stock
@app.route('/sell')
def sell():
    return (render_template('sell.html', navbar = ui.navbar()))

@app.route('/transaction_history/<user_id>')
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
def user_info(user_id):
    cursor = cnx.cursor()
    user_query = "SELECT * FROM User u WHERE u.user_id = %s;"
    cursor.execute(user_query, user_id)
    return 0

@app.route('/watchlist/<user_id>')
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
# End Router Function----------------------------------------------------------------------------------------------------------------------------------------------------


# Functions
#search_function: get user's search keyword(either stock_Id or stock name)
#and find if it is in Database
#if it is in database, then return stock information
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

# Start Server
if __name__ == "__main__":
    app.run(debug = True)
