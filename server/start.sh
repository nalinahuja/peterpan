#!/usr/bin/env bash

# Prompt Database Confirmation
command read -p "load: Is the database running? [y/n]: " confirm

# Verify Confirmation
[[ ${confirm} != "y" ]] && command exit 1

# Prompt Load Confirmation
command read -p "load: Is the database populated? [y/n]: " confirm

# Verify Confirmation
if [[ ${confirm} == "n" ]]
then
  # Display Prompt
  command echo -e "load: Creating dataset"

  # Create SQL Data
  command python3 ./database/dataset/create.py

  # Verify Data Files
  if [[ ! -f ./database/dataset/stock.csv || ! -f ./database/dataset/history.csv ]]
  then
    # Display Data Corruption Error
    command echo -e "load: Could not create dataset"

    # Exit Program
    command exit 1
  fi

  # Display Prompt
  command echo -e "load: Inserting dataset into table"

  # Load Data Into Database
  command python3 ./database/dataset/insert.py

  # Delete Data Files
  command rm ./database/dataset/stock.csv ./database/dataset/history.csv
fi

# Display Prompt
command echo -e "load: Starting Flask server"

# Export Server Environment Variables
export FLASK_APP=app.py

# Start Flask Server
command flask run

# Unset Fields
unset DATABASE_DIR DATABASE_CONFIG
