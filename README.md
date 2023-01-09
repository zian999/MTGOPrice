# MTGOPrice

Get the info of my purchased MTGO cards from `TradeRecord.csv`, fetch their
scryfall ids, and store them in the `cards` table, and the trading history
in the `trading_history` table in a sqlite3 database. Then, fetch their prices
from Scryfall.com API and save the prices, ratio to highest purchase price and
time into another table named `prices`.
