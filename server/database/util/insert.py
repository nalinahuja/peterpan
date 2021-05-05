import os
import yaml
import pandas as pd
import mysql.connector

# End Imports--------------------------------------------------------------------------------------------------------------------------------------------------------


# Load Database Configuration
dbconf = yaml.load(open(os.environ["DATABASE_CONFIG"]), yaml.Loader)

# Establish Database Connection
cnx = mysql.connector.connect(user = dbconf['mysql_user'], password = dbconf['mysql_password'],
                              host = dbconf['mysql_host'], database = dbconf['mysql_db'])

# Create Database Cursor
cursor = cnx.cursor()

# End Database Connection--------------------------------------------------------------------------------------------------------------------------------------------

# Delete From All Tables
cursor.execute("DELETE FROM `Group_Transaction`;")
cursor.execute("DELETE FROM `User_Transaction`;")
cursor.execute("DELETE FROM `Transaction`;")

cursor.execute("DELETE FROM `Group_Stock`;")
cursor.execute("DELETE FROM `Group_Users`;")
cursor.execute("DELETE FROM `Group_Info`;")

cursor.execute("DELETE FROM `User_Stock`;")
cursor.execute("DELETE FROM `Watchlist`;")
cursor.execute("DELETE FROM `User`;")

cursor.execute("DELETE FROM `Stock_Update`;")
cursor.execute("DELETE FROM `Stock`;")

# Commit Data To Database
cnx.commit()

# Insert a user for testing purpose
insert_user = """
              INSERT INTO User (user_id, balance, password)
              VALUES (%s, %s, %s);
              """

# Insert User Into Database
random_user = (int(0), float(2500000), str("123"))
cursor.execute(insert_user, random_user)
cnx.commit()

# Read Stock Data As Pandas Dataframe
df = pd.read_csv(os.path.realpath("../stock.csv"))

# Dynamic SQL Query
stock_insert_query = """
                     INSERT INTO Stock (stock_id, name, price, share)
                     VALUES (%s, %s, %s, %s);
                     """

# Iterate Over Rows In Dataframe
for label, row in (df.iterrows()):
    # Load Stock Attributes Into Variable
    stock_id = row['stock_id']
    name = row['name']
    price = row['price']
    share = row['share']

    # Format Stock Tuple
    stock_data = (int(stock_id), str(name), float(price), int(share))

    # Insert New Stock Tuple
    cursor.execute(stock_insert_query, stock_data)

    # Commit Data To Database
    cnx.commit()

# End Stock Data Insertion--------------------------------------------------------------------------------------------------------------------------------------------

# Read History Data As Pandas Dataframe
df = pd.read_csv(os.path.realpath("../history.csv"))

# Dynamic SQL Query
history_insert_query = """
                       INSERT INTO Stock_Update (update_id, stock_id, price_change)
                       VALUES (%s, %s, %s);
                       """

# Iterate Over Rows In Dataframe
for label, row in (df.iterrows()):
    # Load Stock Attributes Into Variable
    update_id = row['update_id']
    stock_id = row['stock_id']
    price_change = row['price_change']

    # Format History Tuple
    history_data = (int(update_id), int(stock_id), float(price_change))

    # Insert New Stock Tuple
    cursor.execute(history_insert_query, history_data)

    # Commit Data To Database
    cnx.commit()

# Close Database Cursor
cursor.close()

# Close Database Connection
cnx.close()

# End History Data Insertion------------------------------------------------------------------------------------------------------------------------------------------
