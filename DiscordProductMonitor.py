import csv
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
        print("Payload delivered successfully, code {}.".format(result.status_code))

def checkstock(url, search_string):
    """ Checks stock of page by downloading url and checking to see if 
        search_string exists on the page """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
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

    #Open Product File as Read, and convert it to a Dictionary
    csv_file = open('products.csv', mode='r')
    csv_dict = csv.DictReader(csv_file)
    counter = 0

    #iterate through rows of dictionary
    for row in csv_dict:
        #Captures the column names and continues
        if counter == 0:
            print(f'Opened products.csv, columns are: {", ".join(row)}')
            counter += 1

        # Checks if row is enabled, and calls checkstock to inspect site
        # If checkstock returns True, it sends a discord message    
        if row["Enabled"] == 'Y':
            print(f'CHECKING: {row["URL"]}')
            result = checkstock(row["URL"], row["SearchString"])
            if(result == True):
                discord_notification(row["URL"], row["Product"])


        if row["Enabled"] == 'N':
            print(f'SKIPPING: {row["URL"]}')
        counter += 1
    print(f'Processed {counter-1} websites.')