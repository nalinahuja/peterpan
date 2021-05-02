#!/usr/bin/env python3

import os
import sys

# Prompt Database Confirmation
confirm = input("start: Is the database running? [y/n]: ")

# Verify Confirmation
if (not(confirm == "y")):
    sys.exit("load: Exiting...")

# Set Database Configuration Path
os.environ["DATABASE_CONFIG"] = "./db.yaml"
os.environ["FLASK_ENV"] = "development"
os.environ["FLASK_APP"] = "./app.py"
os.environ["DEBUG"] = "False"

# Display Prompt
print("start: Starting Flask server")

# Start Flask Server
os.system("flask run")
