# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 2022

Get the info of my purchased MTGO cards from `TradeRecord.csv`, fetch their
scryfall ids, and store them in the `cards` table, and the trading history
in the `trading_history` table in a sqlite3 database. Then, fetch their prices
from Scryfall.com API and save the prices, ratio to highest purchase price and
time into another table named `prices`.

@author: zianc
"""

import urllib.request, urllib.parse, json, datetime, csv, sqlite3


path_records = "./TradeRecords.csv"

# connect to the sqlite db
conn = sqlite3.connect("./price_db.db")
cur = conn.cursor()
# # Below is a generic way of creating a table if it doesn't exist
# # Another way is simply use CREATE TABLE IF NOT EXIST in sqlite
#
# try:
#     cur.execute('''CREATE TABLE purchased_cards
#                 (Name TEXT, SetName TEXT, CardNo INTEGER,
#                  ID TEXT, Quantity INTEGER, PurchasePrice REAL,
#                  Expansion REAL, PurchaseDate TEXT)''')
# except sqlite3.OperationalError:
#     # table `purchased_cards` exists
#     pass

cur.execute('''CREATE TABLE IF NOT EXISTS cards (
                    Name TEXT NOT NULL,
                    SetName TEXT NOT NULL,
                    CardNo INTEGER NOT NULL,
                    ID TEXT PRIMARY KEY,
                    StockQuantity INTEGER NOT NULL,
                    FOREIGN KEY (ID) REFERENCES prices (ID)
                    FOREIGN KEY (ID) REFERENCES trade_history (ID)
                )''')
cur.execute('''CREATE TABLE IF NOT EXISTS prices (
                    ID TEXT NOT NULL,
                    Price REAL NOT NULL,
                    Ratio REAL NOT NULL,
                    Datetime TEXT NOT NULL,
                    PRIMARY KEY (ID, Price, Datetime)
                )''')
cur.execute('''CREATE TABLE IF NOT EXISTS trade_history (
                    ID TEXT NOT NULL,
                    TradePrice REAL NOT NULL,
                    Quantity INTEGER NOT NULL,
                    Expansion REAL NOT NULL,
                    TradeDate TEXT NOT NULL,
                    PRIMARY KEY (ID, TradePrice, Quantity, TradeDate)
                )''')

with open(path_records, newline='') as f_records:
    
    records_reader = csv.reader(f_records)
    next(records_reader)    # skip header
    
    cstock_quantity = {}
    highest_purchase = {}
    
    for row in records_reader:
        card_name, set_name, card_no, isFoil, \
            quantity, trade_price, expansion_price, trade_date = row
        card_no = int(card_no)
        quantity = int(quantity)
        trade_price = float(trade_price)
        expansion_price = float(expansion_price)
        
        # get and prepare the info from TradeRecords.csv and Scryfall
        url = "https://api.scryfall.com/cards/named?exact=" \
              + urllib.parse.quote(card_name) + "&set=" + set_name
        with urllib.request.urlopen(url) as sfapi:
            sfjson = json.loads(sfapi.read())
        card_id = sfjson['id']
        new_date = datetime.datetime.now()
        if (sfjson['prices']['tix'] is None):
            new_price = 0
        else:
            new_price = float(sfjson['prices']['tix'])
        
        # update the `cards` table
        # check if there is a same record, insert if not
        if (len(cur.execute(
                    '''SELECT * FROM cards WHERE ID = :id''', {"id": card_id}
                    ).fetchall()
                ) == 0):
            cur.execute('''INSERT INTO cards VALUES (?, ?, ?, ?, -999)''',
                        (card_name, set_name, card_no, card_id))
        
        # update the `trade_history` table
        # check if ther is a same trade record, insert if not
        if (len(cur.execute(
                    '''SELECT * FROM trade_history
                    WHERE ID = :id
                    AND TradePrice = :tp
                    AND Quantity = :qt
                    AND TradeDate = :td''',
                    {"id": card_id,
                     "tp": trade_price,
                     "qt": quantity,
                     "td": trade_date}
                    ).fetchall()
                ) == 0):
            cur.execute('''INSERT INTO trade_history VALUES (?, ?, ?, ?, ?)''',
                        (card_id, trade_price, quantity, expansion_price, trade_date))
        
        # store the highest purchase price of each card for later use
        if (quantity > 0):
            if (card_id in highest_purchase):
                highest_purchase[card_id] = \
                    max(highest_purchase[card_id], trade_price)
            else:
                highest_purchase[card_id] = trade_price
        # calculate the ratio to highest purchase price
        ratio = new_price / highest_purchase[card_id]
        
        # update the `prices` table
        cur.execute('''INSERT INTO prices VALUES (?, ?, ?, ?)''',
                    (card_id, trade_price, ratio, new_date))
        
        # stock_quantity for later use
        if (card_id in cstock_quantity):
            cstock_quantity[card_id] = cstock_quantity[card_id] + quantity
        else:
            cstock_quantity[card_id] = quantity
            
    # update the stock_quantity for all cards in `cards` table
    for c in cstock_quantity:
        cur.execute('''UPDATE cards
                    SET StockQuantity = :sq
                    WHERE ID = :id''',
                    {"sq": cstock_quantity[c],
                     "id": c}
                    )


# Save (commit) the changes
conn.commit()

# We can close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()