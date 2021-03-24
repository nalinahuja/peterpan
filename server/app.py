from flask import Flask,render_template
import mysql.connector
import yaml

app = Flask(__name__)

#load database into Python
db = yaml.load(open('db.yaml'),yaml.Loader)
cnx = mysql.connector.connect(user= db['mysql_user'], password= db['mysql_password'],
                              host= db['mysql_host'],
                              database=db['mysql_db'])


#main program
@app.route("/")
def main():
    return render_template('index.html')

cnx = mysql.connector.connect(user='root', password="youpassword",
                              host="localhost",
                              database="db1")
if __name__ == "__main__":
    app.run(debug=True)
