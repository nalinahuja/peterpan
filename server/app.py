import os
import yaml
import globl
import mysql.connector

from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

# End Imports---------------------------------------------------------------------------------------------------------------------------------------------------------

# Load Database Configuration
dbconf = yaml.load(open(os.environ["DATABASE_CONFIG"]), yaml.Loader)

# Establish Database Connection
cnx = mysql.connector.connect(user = dbconf['mysql_user'], password = dbconf['mysql_password'],
                              host = dbconf['mysql_host'], database = dbconf['mysql_db'])

# End Database Connector----------------------------------------------------------------------------------------------------------------------------------------------

# Query for getting all current stock information
get_stock = "SELECT stock_id, name, price, share FROM Stock;"
user_account_money = "SELECT balance FROM User Where user_id = %s;"
get_stock_by_stock_id = "SELECT name,price,share FROM Stock Where stock_id = %s;"
get_user_balance = "SELECT balance FROM User Where user_id = 0;"
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
update_user_balance = "UPDATE User SET balance = %s WHERE user_id = 0;"
insert_user_transaction = "INSERT INTO User_Transaction (transaction_id,type,user_id,stock_id) VALUES (%s,%s,%s,%s);"
insert_transaction = "INSERT INTO Transaction (transaction_id,amount,date,price) VALUES (%s,%s,%s,%s);"
insert_watchlist = "INSERT INTO Watchlist (user_id,stock_id) VALUES (%s, %s);"

# End SQL Queries-----------------------------------------------------------------------------------------------------------------------------------------------------

# Create Flask Application
app = Flask(__name__)

# Configure Flask Application
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:' +dbconf['mysql_password'] + '@localhost/' + dbconf['mysql_db']

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

# End ORM Initialization----------------------------------------------------------------------------------------------------------------------------------------------------

# Route to landing page
@app.route("/", methods=['GET', 'POST'])
def home():
    if (request.method == 'POST'):
        # Fetch user's input data
        user_data = request.form
        #if a user clicks on buy stock
        if user_data.get("buy"):
            return redirect('/buy')
        #if a user clicks on sell stock
        if user_data.get("sell"):
            return redirect('/sell')

        if (user_data.get("transactions")):
            return (redirect("/transactions"))

    return (render_template('index.html'))


@app.route("/stock/<name>", methods = ["GET", "POST"])
def stock(name):
    # todo, list the stock with the name
    return "hello"

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

    return render_template("transactions.html", data = t_list)

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
        cursor.execute(get_user_balance)
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
        update_info = (remaining,)
        cursor.execute(update_user_balance,update_info)
        cnx.commit()

        #update Watchlist
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
        insert_info = (transaction_id,1,0,stock_id)
        cursor.execute(insert_user_transaction,insert_info)
        cnx.commit()

        #print confirmation table into /templates/confirmation.html
        confirmation_info = [number,stock_id,stock_name,spent,remaining];


        return render_template("confirmation.html", data = confirmation_info)


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
    return render_template("buy_page.html", data = stock_info)

# Page to display when user clicks sell stock
@app.route('/sell')
def sell():
    return (render_template('sell.html'))

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

# Start Server
if __name__ == "__main__":
    app.run(debug = True)
