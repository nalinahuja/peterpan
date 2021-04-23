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
  # Change To Database Directory
  command cd ./database/util

  # Display Prompt
  command echo -e "load: Creating dataset"

  # Create SQL Data
  command python3 ./create.py

  # Verify Data Files
  if [[ ! -f ../stock.csv || ! -f ../history.csv ]]
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

  # Change To Root Directory
  command cd ../..
fi

# Display Prompt
command echo -e "load: Starting Flask server"

# Export Server Environment Variables
export FLASK_APP=app.py

# Start Flask Server
command flask run
