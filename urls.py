import personal

def set_urls():

    global sessionurl, neworderurl, closeorderurl, checkorderurl, positionsurl, pricesurl, headers, payload

    if personal.is_demo:
        ig_host="demo-api.ig.com"
    else:
        ig_host="api.ig.com"

    sessionurl = "https://%s/gateway/deal/session" % ig_host
    neworderurl = 'https://%s/gateway/deal/positions/otc' % ig_host
    closeorderurl = 'https://%s/gateway/deal/positions/otc' % ig_host
    checkorderurl = 'https://%s/gateway/deal/confirms/' % ig_host
    positionsurl = 'https://%s/gateway/deal/positions' % ig_host
    pricesurl = 'https://' + ig_host + '/gateway/deal/prices/%s/%s/2'

    headers = {'content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json; charset=UTF-8', 'X-IG-API-KEY': personal.api_key}
    payload = {'identifier': personal.username, 'password': personal.password}

