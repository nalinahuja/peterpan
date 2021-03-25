import os


#function that load all information in buy_template_page into buy_page
def load_purchase_page(buy_page,buy_template_page):
    #loop through all lines of code into buy_template.html
    for line in buy_template_page:
        #write each row into buy.html
        buy_page.write(line)



#function that displays stock information in html page
def display_stock(cursor,buy_page):
    table = ""

    #load all stock information into table variable
    for stock_id,name,price,share in cursor:
        table = table + "<tr>\n"
        table = table + "<td>" + str(stock_id) + "</td>"
        table = table + "<td>" + str(name) + "</td>"
        table = table + "<td>" + str(price) + "</td>"
        table = table + "<td>" + str(share) + "</td>"
        table = table + "</tr>\n"

    #load table value into buy_page
    buy_page.write(table)
    buy_page.write("</table>")

def confirmation_table(number,stock_id,stock_name,spent,remaining):
    if os.path.exists("templates/confirmation.html"):
        os.remove("templates/confirmation.html")
    buy_confirmation_page = open("templates/confirmation.html", "x")

    #construct html table for confirmation
    table = "<html> <table border = '1'>"
    table = table + "<tr>\n"
    table = table + "<td>" + "Number of stocks bought" + "</td>"
    table = table + "<td>" + str(number) + "</td>"
    table = table + "</tr>\n"
    table = table + "<tr>\n"
    table = table + "<td>" + "Stock_id" + "</td>"
    table = table + "<td>" + str(stock_id) + "</td>"
    table = table + "</tr>\n"
    table = table + "<tr>\n"
    table = table + "<td>" + "Stock_name" + "</td>"
    table = table + "<td>" + str(stock_name) + "</td>"
    table = table + "</tr>\n"
    table = table + "<tr>\n"
    table = table + "<td>" + "Total_money_spent" + "</td>"
    table = table + "<td>" + str(spent) + "</td>"
    table = table + "</tr>\n"
    table = table + "<tr>\n"
    table = table + "<td>" + "Total_money_remaining" + "</td>"
    table = table + "<td>" + str(remaining) + "</td>"
    table = table + "</tr>\n"
    table = table + "</table></html>"
    buy_confirmation_page.write(table)
