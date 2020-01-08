# Inventory Checker

This tool can scan for drops in prices on an item of your choice and will send an email to a desired account once that deal is beat.

## Setup

Make sure your email account allows insecure app logins:

- [Google](https://myaccount.google.com/lesssecureapps)

Make the following environmental variables, take note of the space at the beginning which will hide the command from history.

```bash
# This is the recipient of your email
 export EMAIL_DEST=""
# This is the account information you are sending from
 export EMAIL_USER="" 
 export EMAIL_PASS=""
```

## Usage

To just pull information:

```bash
python3 inventory_checker.py $SKU $ZIPCODE
```

To continuously scan for a price to be beaten, and send an email once is found:

```bash
# PRICE is an integer or float
python3 inventory_checker.py $SKU $ZIPCODE price:$PRICE
```

To continuously scan for a discount to be beaten, and send an email once is found:

```bash
# DISCOUNT is between 0 and 1
python3 inventory_checker.py $SKU $ZIPCODE price:$DISCOUNT
```

## Plans

Add support for more of the stores that BrickSeek supports.
