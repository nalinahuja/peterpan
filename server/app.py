import os
import yaml
import mysql.connector

from flask import Flask, request, redirect, render_template

# End Imports---------------------------------------------------------------------------------------------------------------------------------------------------------

# Load Database Configuration
db = yaml.load(open(os.environ['DATABASE_CONFIG']), yaml.Loader)

# Establish Database Connection
cnx = mysql.connector.connect(user = db['mysql_user'], password = db['mysql_password'],
                              host = db['mysql_host'], database = db['mysql_db'])

# End Database Connection---------------------------------------------------------------------------------------------------------------------------------------------

# Query for getting all current stock information
get_stock = "SELECT stock_id,name,price,share FROM Stock"

# End SQL Queries-----------------------------------------------------------------------------------------------------------------------------------------------------

# Create Flask Application
app = Flask(__name__)

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

    return (render_template('index.html'))

@app.route("/stock", methods = ["GET", "POST"])
def stock():
    # todo, list top 10 stocks, all stocks
    return "hello"

@app.route("/stock/<name>", methods = ["GET", "POST"])
def stock(name):
    # todo, list the stock with the name
    return "hello"

# Page to display when user clicks buy stock
@app.route('/buy')
def buy():
    #remove buy.html and create it. Make sure buy.html is an empty file
    #every time before writing to it
    if os.path.exists("templates/buy.html"):
        os.remove("templates/buy.html")
    buy_page = open("templates/buy.html", "x")

    #buy_template.html contains code for asking user which stock_id
    #they want to buy and how many they want to buy
    buy_template_page = open("templates/buy_template.html", "r")

    #loop through all lines of code into buy_template.html
    for line in buy_template_page:
        #write each row into buy.html
        buy_page.write(line)

    #execute the query for getting all stock information
    cursor.execute(get_stock)
    table = ""

    #load all stock information into table variable
    for stock_id,name,price,share in cursor:
        table = table + "<tr>\n"
        table = table + "<td>" + str(stock_id) + "</td>"
        table = table + "<td>" + str(name) + "</td>"
        table = table + "<td>" + str(price) + "</td>"
        table = table + "<td>" + str(share) + "</td>"
        table = table + "</tr>\n"

    #load table value into buy_page
    buy_page.write(table)

    #end of html
    buy_page.write("</table>")
    buy_page.write("\n</html>")
    buy_page.close()
    #copy all of the code inside buy_template.html into buy.html
    return (render_template('buy.html'))

# Page to display when user clicks sell stock
@app.route('/sell')
def sell():
    return (render_template('sell.html'))

# Start Server
if __name__ == "__main__":
    app.run(debug = True)
