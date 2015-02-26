import requests
import json
import logging
import time

import urls


logger = logging.getLogger("quotes")
hdlr = logging.FileHandler('Logs/quotes-'+time.strftime("%d-%M-%Y")+'.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

# Tell the user when the Lighstreamer connection state changes
def on_state(state):
    print state

# Process a lighstreamer price update
def processPriceUpdate(item, myUpdateField):
    logger.info(str(myUpdateField))
    window.update_price(*myUpdateField)

# Process an update of the users trading account balance
def processBalanceUpdate(item, myUpdateField):
    balance, pnl = myUpdateField
    r = requests.get(urls.positionsurl, headers=urls.fullheaders)
    s = json.loads(r.content)["positions"]
    nb_pos = sum( 1 if pos["position"]["direction"] == "BUY" else -1 for pos in s)
    window.update_balance(balance, pnl, nb_pos)

# Process an update of the users trading account balance
def processPositionUpdate(item, myUpdateField):
    confirms = next(json.loads(field) for field in myUpdateField if field != None)
    window.add_position(confirms.values())
