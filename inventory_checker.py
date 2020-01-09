#!/usr/bin/python3

import bs4
import time
import os
import requests
import smtplib
import sys

# Settings
DELAY = 300 # 5 minutes
EMAIL_SERVER_PORT = 465
EMAIL_SERVER_SSL = 'smtp.gmail.com'

# Objects
class Store():
    AVAIL = {
        "In Stock",
        "Limited Stock",
        "Out of Stock"
    }
    def __init__(self, row):
        self.store = {
            "Name": row.select_one(".address-location-name").text.strip(),
            "Street": row.select_one("address").contents[0].strip(),
            "City": " ".join(row.select_one("address").contents[2].strip().split(" ")[:-2]),
            "State": row.select_one("address").contents[2].strip().split(" ")[-2],
            "Zip": row.select_one("address").contents[2].strip().split(" ")[-1],
            "Distance": row.select_one(".address__below").text.strip(),
        }
        self.address = f"{self.store['Street']}\n\
                        {self.store['City']}, {self.store['State']} {self.store['Zip']}"
        self.availability = row.select_one(".availability-status-indicator__text").text.strip()
        self.price = float(row.select_one(".price-formatted").text.strip().replace("$",""))
    def __repr__(self):
        return f"\n{self.store['Name']}\n \
                {self.address}\n \
                {self.availability}\n \
                {self.price}"


class Inventory():
    def __init__(self, SKU, ZIP):
        URL = f"https://brickseek.com/walmart-inventory-checker/?sku={SKU}&zip={ZIP}"
        data = {
            'store_type': '3',
            'sku': SKU,
            'zip': ZIP,
            'sort': 'quan'
        }
        res = requests.post(URL, data=data)
        page = bs4.BeautifulSoup(res.text, features="html.parser")
        rows = page.select(".inventory-checker-table--store-availability-price .table__body .table__row")
        self.name = page.select_one(".section-title").text.strip()
        self.msrp = float(page.select_one(".item-overview__meta-item .price-formatted").text.replace("$",""))
        self.stores = []
        for row in rows:
            self.stores.append(Store(row))
    def __repr__(self):
        return self.stores
    def lowest_price(self):
        min_price = min([x.price for x in self.stores if x.availability != "Out of Stock"])
        return [x for x in self.stores if x.price == min_price]
    def beat_price(self, price):
        return [x for x in self.stores if x.price <= price and x.availability != "Out of Stock"]
    def beat_discount(self, discount):
        return [x for x in self.stores if x.price <= self.msrp*(1-discount/100) and x.availability != "Out of Stock"]


# Functions
def mail(subject, body):
    sender = "BRICKSEEK_CHECKER@home.lab"
    recipient = os.environ['EMAIL_DEST']
    subject = f"{subject}"
    body = f"{body}"
    email_content = f"\
    From: {sender}\n\
    To: {recipient}\n\
    Subject: {subject}\n\n\
    {body}"

    try:
        with smtplib.SMTP_SSL(EMAIL_SERVER_SSL, EMAIL_SERVER_PORT) as server:
            server.ehlo()
            server.login(os.environ['EMAIL_USER'], os.environ['EMAIL_PASS'])
            server.sendmail(sender, recipient, email_content)
        print('Email sent!')
    except SMTPAuthenticationError as e:
        print(f"Bad password! -- {e}")
    except:
        print('Something went wrong...')

def main():
    SKU = sys.argv[1]
    ZIP = sys.argv[2]
    if len(sys.argv) > 3:
        OPTION = sys.argv[3]
    else:
        OPTION = ""

    while True:
        inventory = Inventory(SKU, ZIP)
        if not OPTION:
            print(inventory)
            exit(0)
        if "price" in OPTION:
            price = int(OPTION.split(":")[1])
            stores = inventory.beat_price(price)
            if len(stores) > 0:
                print(f"The following stores beat the price of ${stores[0].price}.")
                print(inventory.stores)
                subject = f"Sale on {inventory.name}, ${stores[0].price}"
                body = f"The following stores beat the price of ${price} on {inventory.name}:\n\n{stores}"
                mail(subject, body)
                exit(0)
            else:
                print(f"No stores in area beat the price of ${price}, will check again.")
        if "discount" in OPTION:
            discount = int(OPTION.split(":")[1])
            stores = inventory.beat_discount(discount)
            if len(stores) > 0:
                print(f"The following stores beat the discount of {stores[0].price}%.")
                print(inventory.stores)
                subject = f"Sale on {inventory.name}, ${stores[0].price}"
                body = f"The following stores beat the discount of {discount}% on {inventory.name}:\n\n{stores}"
                mail(subject, body)
                exit(0)
            else:
                print(f"No stores in area beat the discount of {discount}%, will check again.")
        time.sleep(DELAY)

if __name__ == "__main__":
    main()