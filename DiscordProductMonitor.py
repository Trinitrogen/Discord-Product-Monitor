import sqlite3
import requests
import sys
import os
from urllib.parse import urlparse


#TODO - Add column for last checked and last found
#TODO - Add Logging
#TODO - Disable Product When Found


def test_search():
    """Takes interactive input and tests if product is in stock
    but does not send notification"""
    url = input("URL Of Product: ")
    search_string = input("Sting To Search For: ")
    result = checkstock(url, search_string)

def disable_product(id):
    """ calls list_products, then prompts user to provide ID of product, 
    then sets the Enabled row to 0"""
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()    
    sql =   '''UPDATE products SET enabled = 0 WHERE product_id = ?;''' 
    cursor.execute(sql,id)
    connection.commit()
    cursor.close()
    connection.close()

def enable_product(id):
    """ calls list_products, then prompts user to provide ID of product, 
    then sets the Enabled row to 1"""
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()    
    sql =   '''UPDATE products SET enabled = 1 WHERE product_id = ?;''' 
    cursor.execute(sql,id)
    connection.commit()
    cursor.close()
    connection.close()

def list_disabled_products():
    """ List All Products"""
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    print("ID\tEnabled?\tProduct\tURL\tSearch String")
    cursor.execute('''SELECT * FROM products WHERE enabled = 0''')
    for row in cursor:
        id = row[0]
        product = row[2]
        url = urlparse(row[3]).netloc
        search_string = row[4]

        if(row[1] == 1):
            enabled = "Yes"
        else:
            enabled = "No"
        print(f"{id}\t{enabled}\t{product}\t{url}\t{search_string}")
    cursor.close()
    connection.close()

def list_enabled_products():
    """ List All Products"""
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    print("ID\tEnabled?\tProduct\tURL\tSearch String")
    cursor.execute('''SELECT * FROM products WHERE enabled = 1''')
    for row in cursor:
        id = row[0]
        product = row[2]
        url = urlparse(row[3]).netloc
        search_string = row[4]

        if(row[1] == 1):
            enabled = "Yes"
        else:
            enabled = "No"
        print(f"{id}\t{enabled}\t{product}\t{url}\t{search_string}")
    cursor.close()
    connection.close()

def list_products():
    """ List All Products"""
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    print("ID\tEnabled?\tProduct\tURL\tSearch String")
    print("--\t--------\t-------\t---\t-------------")
    sql =  '''SELECT * FROM products'''
    cursor.execute(sql)
    for row in cursor:
        id = row[0]
        product = row[2]
        url = urlparse(row[3]).netloc
        search_string = row[4]

        if(row[1] == 1):
            enabled = "Yes"
        else:
            enabled = "No"
        print(f"{id}\t{enabled}\t{product}\t{url}\t{search_string}")
    cursor.close()
    connection.close()

def insert_product(product, url, search_string):
    """ Insert Product Into Database """
    sql =   '''INSERT INTO products (enabled,product_name, url, 
            search_string) VALUES (?,?,?,?);'''
    data_tuple = (1,product, url, search_string)
    insert_connection = sqlite3.connect('products.db')
    insert_cursor = insert_connection.cursor()
    insert_cursor.execute(sql, data_tuple)
    insert_connection.commit()
    insert_cursor.close()
    insert_connection.close()

def add_product():
    product = input('Name of the product: ')
    url = input(f'URL for {product}: ')
    search_string = input('What string to search for: ')
    insert_product(product, url, search_string)

def discord_notification(url, product):
    """ Send Discord Notification with Product Name and URL"""
    discord_webhook = os.getenv('DISCORD_WEBHOOK')
    message = {
    "content" : f"{product} found at {url}",
    "username" : "Product Monitor"
    }
    result = requests.post(discord_webhook, json = message)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Discord Webhook Successful, Code {}.".format(result.status_code))

def checkstock(url, search_string):
    """ Checks stock of page by downloading url and checking to see if 
        search_string exists on the page """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
    headers = {'User-Agent': user_agent}
    print(f'DOWNLOADING {url}')
    website = requests.get(url,headers)

    if website.status_code != 200:
        print("ERROR: Website returns code " + str(website.status_code))
        return False
    if search_string in website.text:
        print("IN STOCK: Product Found at " + url)
        return True
    if search_string not in website.text:
        print("OUT OF STOCK: Product not found at " + url)
        return False
    else:
        print("ERROR: Else case of checkstock")

if __name__ == "__main__":

    #Confirm DISCORD_WEBHOOK environment variable exists
    if(('DISCORD_WEBHOOK' in os.environ) == False):
        print("Missing DISCORD_WEBHOOK Variable")
        quit(1)

    #Make sure current working directory is same as script
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    #Check for arguments
    if (args_count := len(sys.argv)) > 1:
        if sys.argv[1] == '-a':
            add_product()
            quit(0)
        if sys.argv[1] == '-l':
            list_products()
            quit(0)
        if sys.argv[1] == '-d':
            list_enabled_products()
            id = input('Which Product To Disable: ')
            disable_product(id)
            quit(0)
        if sys.argv[1] == '-e':
            list_disabled_products()
            id = input('Which Product To Enable: ')  
            enable_product(id)
            quit(0)
        if sys.argv[1] == '-t':
            test_search()
            quit(0)
        else:
            print(f'Unknown Parameter {sys.argv[1]}')

    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM products WHERE enabled = 1''')

    for row in cursor:
        id = row[0]
        product = row[2]
        url = row[3]
        search_string = row[4]

        print(f'CHECKING: {url}')
        result = checkstock(url, search_string)
        if(result == True):
            print('Product Found Calling Discord_Notification')
            discord_notification(url, product)
    cursor.close()
    connection.close()