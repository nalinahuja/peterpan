#!/usr/bin/env bash

export DATABASE_DIR=$(command realpath ./database)
export DATABASE_CONFIG=$(command realpath ./db.yaml)

# Switch To Database Directory
command cd ${DATABASE_DIR}

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

# Load Data Into Database
command python3 ./insert.py

# Delete Data Files
command rm ./stock.csv ./history.csv

# Unset Fields
unset DATABASE_DIR DATABASE_CONFIG
