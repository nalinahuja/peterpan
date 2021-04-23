#!/usr/bin/env bash

# Export Database Environment Variables
export DATABASE_DIR=$(command realpath ./database)

# Prompt Database Confirmation
command read -p "load: Is the database running? [y/n]: " confirm

# Verify Confirmation
[[ ${confirm} != "y" ]] && command exit 1

# Prompt Load Confirmation
command read -p "load: Is the database populated? [y/n]: " confirm

# Verify Confirmation
if [[ ${confirm} == "n" ]]
then
  # Switch To Database Directory
  command cd ${DATABASE_DIR}/data

  # Display Prompt
  command echo -e "load: Creating dataset"

  # Create SQL Data
  command python3 ./create.py

  # Verify Data Files
  if [[ ! -f ./stock.csv || ! -f ./history.csv ]]
  then
    # Display Data Corruption Error
    command echo -e "load: Could not create dataset"

    # Exit Program
    command exit 1
  fi

  # Display Prompt
  command echo -e "load: Inserting dataset into table"

  # Load Data Into Database
  command python3 ./insert.py

  # Delete Data Files
  command rm ./stock.csv ./history.csv

  # Switch To Parent Directory
  command cd ../..
fi

# Display Prompt
command echo -e "load: Starting Flask server"

# Export Server Environment Variables
export FLASK_APP=app.py

# Start Flask Server
command python3 ./app.py

# Unset Fields
unset DATABASE_DIR DATABASE_CONFIG
