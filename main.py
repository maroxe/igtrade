# IG API Trader
import wx
import igls,requests,json, time
import gui
import events
from personal import *

if liveOrDemo == "Demo":
    ig_host="demo-api.ig.com"
elif liveOrDemo == "Live":
    ig_host="api.ig.com"

sessionurl = "https://%s/gateway/deal/session" % ig_host
neworderurl = 'https://%s/gateway/deal/positions/otc' % ig_host
closeorderurl = 'https://%s/gateway/deal/positions/otc' % ig_host
checkorderurl = 'https://%s/gateway/deal/confirms/' % ig_host
positionsurl = 'https://%s/gateway/deal/positions' % ig_host
pricesurl = 'https://' + ig_host + '/gateway/deal/prices/%s/%s/2'

headers = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'X-IG-API-KEY': APIkey}
payload = {'identifier': username, 'password': password}

def buy(event):
    expiry = '-'
    body = {"currencyCode": "EUR", "epic": epic, "expiry": expiry, "direction": "BUY", "size": 1, "forceOpen": False, "guaranteedStop": False, "orderType": "MARKET"}
    requests.post(neworderurl, data=json.dumps(body), headers=fullheaders)
    
def sell(event):
    expiry = '-'
    body = {"currencyCode": "EUR", "epic": epic, "expiry": expiry, "direction": "SELL", "size": 1, "forceOpen": False, "guaranteedStop": False, "orderType": "MARKET"}
    requests.post(neworderurl, data=json.dumps(body), headers=fullheaders)
    


def calculatePivots():
    r = requests.get(pricesurl % (epic, 'DAY'), headers=fullheaders)
    s = json.loads(r.content)['prices'][0]

    H = (s['highPrice']['ask']  + s['highPrice']['bid']) / 2
    B =  (s['lowPrice']['ask']  + s['lowPrice']['bid']) / 2
    C =  (s['closePrice']['ask']  + s['closePrice']['bid']) / 2

    Pivot = (H + B + C) / 3
    S1 = (2 * Pivot) - H
    S2 = Pivot - (H - B)
    S3 = B - 2* (H - Pivot)
    R1 = (2 * Pivot) - B
    R2 = Pivot + (H - B)
    R3 = H + 2* (Pivot - B)
    
    return S3, S2, S1, Pivot, R1, R2, R3

    
if __name__ == '__main__':
    print 'launching...'
    r = requests.post(sessionurl, data=json.dumps(payload), headers=headers)
    print 'request completed'

    cst = r.headers['cst']
    xsecuritytoken = r.headers['x-security-token']
    fullheaders = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'X-IG-API-KEY': APIkey, 'CST': cst, 'X-SECURITY-TOKEN': xsecuritytoken }

    body = r.json()
    
    lightstreamerEndpoint = body[u'lightstreamerEndpoint']
    clientId = body[u'clientId']
    accounts = body[u'accounts']

    # Depending on how many accounts you have with IG the '0' may need to change to select the correct one (spread bet, CFD account etc)
    accountId = accounts[0][u'accountId']

    print 'connecting...'

    client = igls.LsClient(lightstreamerEndpoint+"/lightstreamer/")
    client.on_state.listen(events.on_state)
    client.create_session(username=accountId, password='CST-'+cst+'|XST-'+xsecuritytoken, adapter_set='')

    priceTable = igls.Table(client,
        mode=igls.MODE_MERGE,
        item_ids='L1:IX.D.DAX.IMF.IP',
        schema="OFFER BID",
    )

    priceTable.on_update.listen(events.processPriceUpdate)

    balanceTable = igls.Table(client,
        mode=igls.MODE_MERGE,
        item_ids='ACCOUNT:'+accountId,
        schema='AVAILABLE_CASH PNL',
    )


    balanceTable.on_update.listen(events.processBalanceUpdate)

    
    positionTable = igls.Table(client,
        mode=igls.MODE_DISTINCT,
        item_ids='TRADE:'+accountId,
        schema='CONFIRMS WOU OPU',
    )

    positionTable.on_update.listen(events.processPositionUpdate)


    app = wx.App()
    pivots = calculatePivots()
    window = gui.Window(None, pivots=pivots, title='Trading Dax')
    window.buy_button.Bind(wx.EVT_BUTTON, buy)
    window.sell_button.Bind(wx.EVT_BUTTON, sell)
    app.MainLoop()






