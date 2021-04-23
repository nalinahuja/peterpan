#!/usr/bin/env bash

# Declare Database Configuration Path
declare DATABASE_CONFIG=$(command realpath "../../db.yaml")

# Display Prompt
command echo -en "\rload: Creating dataset"

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
command echo -en "\rload: Inserting dataset into table"

# Load Data Into Database
command python3 ./insert.py

# Display Prompt
command echo -e "\rload: Operation successful"
