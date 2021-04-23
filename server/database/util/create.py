import os
import random
import string
import numpy as np

from collections import defaultdict

# Seed Random Module
random.seed(os.urandom(1024))

# End Imports--------------------------------------------------------------------------------------------------------------------------------------------------------

# Stock File Name
STOCK_FILE = os.path.realpath("../stock.csv")

# History File Name
HISTORY_FILE = os.path.realpath("../history.csv")

# Number Of Unique Stocks
NUM_STOCKS = 50

# Maximum Name Length
MAXIMUM_NAME_LENGTH = 5

# Maximum Price Change
MAXIMUM_PRICE_CHANGE = 20

# Maximum Stock Price
MAXIMUM_STOCK_PRICE = 5000

# Maximum Stock Shares
MAXIMUM_STOCK_SHARES = 20000

# Maximum History Length
MAXIMUM_HISTORY_LENGTH = 50

# End Constants-------------------------------------------------------------------------------------------------------------------------------------------------------

def generate_name():
    return ''.join([random.choice(string.ascii_uppercase) for i in range(MAXIMUM_NAME_LENGTH)])

if __name__ == "__main__":
    # Name Set
    name_set = set()

    # Stock Tuples
    stocks = []

    # History Tuples
    history = defaultdict(list)

    # Generate Stock Entries
    for i in range(NUM_STOCKS):
        # Stock Name
        name = generate_name()

        # Create Unique Stock Name
        while (name in name_set):
            name = generate_name()

        # Stock Price
        pers = np.arange(1, MAXIMUM_STOCK_PRICE, 1)

        # Make each of the first 500 elements 5 times more likely
        prob = [5.0] * (500) + [1.0] * (len(pers) - 500)

        # Normalize Data To [0, 1]
        prob /= np.sum(prob)

        # Get Stock Price
        price = (np.random.choice(pers, 1, p = prob)[0]) + random.random()

        # Get Stock Share
        shares = int(random.random() * MAXIMUM_STOCK_SHARES)

        # Append Stock Data
        stocks.append((name, price, shares))

        # Initialize Previous Prive
        prev_price = price

        # Create Stock History
        for j in range(MAXIMUM_HISTORY_LENGTH):
            # Get Increase Or Decrease Direction
            id = int(random.randint(0, 1))

            # Calculate Price Delta
            delta = float(random.random() * MAXIMUM_PRICE_CHANGE) * (-1 if (id == 0) else 1)

            # Calculate Current Price
            curr_price = prev_price + delta

            # Verify Current Price
            if (curr_price < 10):
                continue

            # Append Stock Update To History Dictionary
            history[i].append((j, i, curr_price))

            # Update Previous Price
            prev_price = curr_price

    # Create CSV Stock File
    stock_file = open(STOCK_FILE, "w")

    # Append Column Headers To File
    stock_file.write("stock_id,name,price,share\n")

    # Iterate Over Stock Data
    for i, stock in enumerate(stocks):
        # Unpack Stock Data
        name, price, share = stock

        # Append Stock Data To File
        stock_file.write("{},{},{:.2f},{}\n".format(i, name, price, share))

    # Close Stock File
    stock_file.close()

    # Create CSV History File
    hist_file = open(HISTORY_FILE, "w")

    # Append Column Headers To File
    hist_file.write("update_id,stock_id,price_change\n")

    # Iterate Over Stocks By Id
    for i in sorted(history.keys()):
        # Get Stock Updates List
        updates = history[i]

        # Iterate Over Stock Updates
        for j in range(len(updates)):
            # Unpack Stock Data
            update_id, stock_id, price_change = updates[j]

            # Append History Data To File
            hist_file.write("{},{},{}\n".format(update_id, stock_id, price_change))

    # Close History File
    hist_file.close()

# End File------------------------------------------------------------------------------------------------------------------------------------------------------
