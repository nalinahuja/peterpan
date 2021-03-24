# CS348 Project
cs348 project repository for Elon Musketeers

# Get Started

Install the dependencies using the following command

```bash
command python3 -m pip install -r ./requirements.txt
```

# Load Stock.csv into database

Inside server/db.yaml, enter your database information(mysql_host,mysql_password,mysql_user and mysql_database)

Then run the following command

```bash
python load_stock.py
```
# Load stock page

Inside server directory, run the following command. Remember to enter your database information in db.yaml before

```bash
python app.py
```

