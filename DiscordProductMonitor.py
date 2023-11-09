import sqlite3
import requests
import config

def discord_notification(url, product):
    message = {
    "content" : f"{product} found at {url}",
    "username" : "Product Monitor"
    }
    result = requests.post(config.discord_webhook_url, json = message)

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
        print("SUCCESS: Product Found at " + url)
        return True
    else:
        print("ERROR: Reached Else case of checkstock")

if __name__ == "__main__":

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
            print('Product Found')
            discord_notification(url, product)