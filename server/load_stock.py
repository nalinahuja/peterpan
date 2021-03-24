#function to load stock into database
import pandas as pd
import mysql.connector
import yaml

#load database
db = yaml.load(open('db.yaml'),yaml.Loader)
cnx = mysql.connector.connect(user= db['mysql_user'], password= db['mysql_password'],
                              host= db['mysql_host'],
                              database=db['mysql_db'])
cursor = cnx.cursor()

#read stock information stock->(stock_id(PK),name,price,share)
df = pd.read_csv("database/data/stock.csv")

add_stock = "INSERT INTO Stock "\
               "(stock_id, name, price, share)"\
               "VALUES (%s, %s, %s, %s)"


#iterate all rows in stock csv and insert the data into database
for label,row in df.iterrows():
    #load stock attributes into variable
    stock_id = row['stock_id']
    name = row['name']
    price = row['price']
    share = row['share']
    stock_data = (stock_id, name, price, share)
    #insert new stock
    cursor.execute(add_stock, stock_data)
    # Make sure data is committed to the database
    cnx.commit()
cursor.close()
cnx.close()
