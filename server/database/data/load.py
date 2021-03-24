import os
import random
import string
import numpy as np
import pandas as pd

# Seed Random Module
random.seed(os.urandom(1024))

# Data File Name
DATA_FILE = "stock.csv"

# Number Of Unique Stocks
NUM_STOCKS = 1000

# Maximum Stock Name Length
MAXIMUM_NAME_LENGTH = 5

# Maximum Stock Price
MAXIMUM_STOCK_PRICE = 5000

# Maximum Stock Shares
MAXIMUM_STOCK_SHARES = 20000

def generate_name():
    return ''.join([random.choice(string.ascii_uppercase) for i in range(MAXIMUM_NAME_LENGTH)])

if __name__ == "__main__":
    # Name Set
    name_set = set()

    # Stock Tuples
    stocks = []

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

    # Create CSV Data File
    file = open(DATA_FILE, "w")

    # Append Column Headers To File
    file.write("id, name, price, share\n")

    # Iterate Over Stock Data
    for i, stock in enumerate(stocks, 1):
        # Unpack Stock Data
        name, price, share = stock

        # Append Stock Data To File
        file.write("{}, {}, {:.2f}, {}\n".format(i, name, price, share))

    # Close Data File
    file.close()
