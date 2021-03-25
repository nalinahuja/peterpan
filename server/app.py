import os
import yaml
import mysql.connector

from flask import Flask, request, redirect, render_template

# End Imports--------------------------------------------------------------------------------------------------------------------------------------------------------

# Load Database Configuration
db = yaml.load(open(os.environ['DATABASE_CONFIG']), yaml.Loader)

# Establish Database Connection
cnx = mysql.connector.connect(user = db['mysql_user'], password = db['mysql_password'],
                              host = db['mysql_host'], database = db['mysql_db'])

# End Database Connection--------------------------------------------------------------------------------------------------------------------------------------------

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

# Page to display when user clicks buy stock
@app.route('/buy')
def buy():
    return (render_template('buy.html'))

# Page to display when user clicks sell stock
@app.route('/sell')
def sell():
    return (render_template('sell.html'))

# Start Server
if __name__ == "__main__":
    app.run(debug = True)
