import os
import yaml
import pandas as pd
import mysql.connector

# End Imports--------------------------------------------------------------------------------------------------------------------------------------------------------

# Load Database Configuration
db = yaml.load(open(os.environ['DATABASE_CONFIG']), yaml.Loader)

# Establish Database Connection
cnx = mysql.connector.connect(user = db['mysql_user'], password = db['mysql_password'],
                              host = db['mysql_host'], database = db['mysql_db'])

# Create Database Cursor
cursor = cnx.cursor()

# Read Stock Data As Pandas Dataframe
df = pd.read_csv("./stock.csv")

# Dynamic SQL Query
stock_insert_query = """
                     INSERT INTO Stock (stock_id, name, price, share)
                     VALUES (%s, %s, %s, %s)
                     """

# Iterate Over Rows In Dataframe
for label, row in (df.iterrows()):
    # Load Stock Attributes Into Variable
    stock_id = row['stock_id']
    name = row['name']
    price = row['price']
    share = row['share']

    # Format Stock Tuple
    stock_data = (stock_id, name, price, share)

    # Insert New Stock Tuple
    cursor.execute(stock_insert_query, stock_data)

    # Commit Data To Database
    cnx.commit()

# Read History Data As Pandas Dataframe
df = pd.read_csv("./history.csv")

# Dynamic SQL Query
history_insert_query = """
                       INSERT INTO Stock_Update (update_id, stock_id, price_change)
                       VALUES (%s, %s, %s)
                       """

# Iterate Over Rows In Dataframe
for label, row in (df.iterrows()):
    # Load Stock Attributes Into Variable
    update_id = row['update_id']
    stock_id = row['stock_id']
    price_change = row['price_change']

    # Format History Tuple
    history_data = (stock_id, name, price)

    # Insert New Stock Tuple
    cursor.execute(history_insert_query, history_data)

    # Commit Data To Database
    cnx.commit()

# Close Database Cursor
cursor.close()

# Close Database Connection
cnx.close()
