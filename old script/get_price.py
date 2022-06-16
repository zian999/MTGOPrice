# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 16:22:52 2021

Get MTGO card names from `card_list.txt`, then fetch prices of all printings 
from Scryfall.com API and sort from low to high price. Save result into 
`card_prices.txt`.

@author: zianc
"""

import urllib.request, json, datetime


file_path = "./cards_list.txt"
with open(file_path, 'r') as f:
    card_names = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
card_names = [x.strip() for x in card_names] 

with open('cards_tix.txt', 'a') as f:
    t = str(datetime.datetime.now())
    for c in card_names:
        cc = c.replace(' ', '%20')
        cc = cc.replace(';', '%27')
        url = "https://api.scryfall.com/cards/search?order=released&q=%22" + cc + "%22&unique=prints"
        with urllib.request.urlopen(url) as sfapi:
            dl = json.loads(sfapi.read().decode())
        card_sets = []
        card_prices = []
        for prt in dl['data']:        
            if prt['prices']['tix'] is None:
                continue
            card_prices.append(float(prt['prices']['tix']))
            card_sets.append(prt['set'])
        card_info = dict(zip(card_sets, sorted(card_prices)))
        card_info = dict(sorted(card_info.items(), key=lambda item: item[0]))
        card_info = dict(sorted(card_info.items(), key=lambda item: item[1]))
        
        # # write all tix information to a file
        # for key in card_info.keys():
        #     f.write(t + '\t' + c + '\t' + str(card_info[key]) + '\t' + str(key) + '\n')
        
        # only write the lowest tix information to a file
        f.write(t + '\t' + str(list(card_info.keys())[0]) + '\t'+ str(list(card_info.values())[0]) + '\t'  + c + '\n')