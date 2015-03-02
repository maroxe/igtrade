# IG API Trader
import wx
import igls,requests,json, time
import gui
import urls
import events
import personal


def buy(event): order(event, "BUY")
def sell(event): order(event, "SELL")

def order(event, direction):
    expiry = '-'
    body = {"currencyCode": "EUR", "epic": personal.epic, "expiry": expiry, "direction": direction, "size": 1, "forceOpen": False, "guaranteedStop": False, "orderType": "MARKET"}
    requests.post(urls.neworderurl, data=json.dumps(body), headers=urls.fullheaders, proxies=personal.proxies)

def calculatePivots():
    r = requests.get(urls.pricesurl % (personal.epic, 'DAY'), headers=urls.fullheaders, proxies=personal.proxies)
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

def getDailyPrices():
    url = 'https://' + urls.ig_host + '/gateway/deal/prices/%s/%s/%d' %  (personal.epic, 'MINUTE', 100000)
    r = requests.get(url, headers=urls.fullheaders, proxies=personal.proxies)
    s = json.loads(r.content)
    import pickle
    with open('Logs/quotesobjectv2.pickle', 'w') as f: pickle.dump(s,  f)
    
    


def main(event):

    loging_window.on_close()
    
    # Connecting to IG
    print 'Connecting as', personal.username
    urls.set_urls()
    r = requests.post(urls.sessionurl, data=json.dumps(urls.payload), headers=urls.headers, proxies=personal.proxies)

    cst = r.headers['cst']
    xsecuritytoken = r.headers['x-security-token']
    urls.fullheaders = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'X-IG-API-KEY': personal.api_key, 'CST': cst, 'X-SECURITY-TOKEN': xsecuritytoken }

    body = r.json()
    
    lightstreamerEndpoint = body[u'lightstreamerEndpoint']
    clientId = body[u'clientId']
    accounts = body[u'accounts']

    # Depending on how many accounts you have with IG the '0' may need to change to select the correct one (spread bet, CFD account etc)
    accountId = accounts[0][u'accountId']

    client = igls.LsClient(lightstreamerEndpoint+"/lightstreamer/")
    client.on_state.listen(events.on_state)
    client.create_session(username=accountId, password='CST-'+cst+'|XST-'+xsecuritytoken, adapter_set='')

    priceTable = igls.Table(client,
        mode=igls.MODE_MERGE,
        item_ids='L1:%s' % personal.epic,
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

    pivots = calculatePivots()
    window = gui.Window(None, pivots=pivots, title='Trading IG')
    window.buy_button.Bind(wx.EVT_BUTTON, buy)
    window.sell_button.Bind(wx.EVT_BUTTON, sell)
    events.window = window

if __name__ == '__main__':

    # Login Window
    app = wx.App()
    loging_window = gui.LogWindow(None)
    loging_window.connect_button.Bind(wx.EVT_BUTTON, main)
    app.MainLoop()



