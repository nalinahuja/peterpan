#!/usr/bin/env python3

import os
import sys

# Declare Database Configuration Path
os.environ["DATABASE_CONFIG"] = os.path.realpath("../../db.yaml")

# Display Prompt
print("\rload: Creating dataset ", end = "")

# Create SQL Data
os.system("python3 ./create.py")

# Verify Data Files
if (not(os.path.isfile("../stock.csv")) or not(os.path.isfile("../history.csv"))):
  # Display Data Corruption Error
  print("\rload: Could not create dataset")

  # Exit Program
  sys.exit(1)

# Display Prompt
print("\rload: Inserting dataset into table ", end = "")

# Load Data Into Database
os.system("python3 ./insert.py")

# Display Prompt
print("\rload: Operation successful          ")
