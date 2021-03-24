from flask import Flask,render_template,request,redirect
import mysql.connector
import yaml

app = Flask(__name__)

#load database into Python
db = yaml.load(open('db.yaml'),yaml.Loader)
cnx = mysql.connector.connect(user= db['mysql_user'], password= db['mysql_password'],
                              host= db['mysql_host'],
                              database=db['mysql_db'])


#main program
@app.route("/",methods=['GET', 'POST'])
def main():
    #print("get requested method")
    if request.method == 'POST':
        # Fetch user's input data
        print("get requested method")
        user_data = request.form
        #if a user clicks on buy stock
        if user_data.get("buy"):
            return redirect('/buy')
        #if a user clicks on sell stock
        if user_data.get("sell"):
            return redirect('/sell')

    return render_template('index.html')

#page to display when user clicks buy stock
@app.route('/buy')
def buy():
    return render_template('buy.html')

#page to display when user clicks sell stock
@app.route('/sell')
def sell():
    return render_template('sell.html')

if __name__ == "__main__":
    app.run(debug=True)
