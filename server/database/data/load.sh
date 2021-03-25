#!/usr/bin/env bash

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
command python3 ./load.py
