import json
import urllib3

def getRequest(url):
    http = urllib3.PoolManager()
    resp = http.request('GET', url)
    return resp.status

def getToken(uuid):
    http = urllib3.PoolManager()
    url = "https://wap.tplinkcloud.com"

    data = "{\n \"method\": \"login\",\n \"params\": {\n \"appType\": \"Kasa_Android\",\n \"cloudUserName\": \"***\",\n \"cloudPassword\": \"***\",\n \"terminalUUID\": \"% (uuid)\"\n }\n}";

    r = http.request(
        'POST', 
        url,
        body=data,
        headers={
            'Content-Type': 'application/json'
        })

    resp = json.loads(r.data.decode('utf-8'))
    return resp['result']['token']

def setBulbColour(colour):    
    uuid = getUUID()
    tokenGenerated = getToken(uuid)
    
    http = urllib3.PoolManager()
    url = "https://wap.tplinkcloud.com"

    data =  "{\n \"method\": \"passthrough\",\n \"params\": {\n \"token\": \"%s\",\n \"deviceId\": \"801210885499B637BA066FDA9E00E82E1D1D1B9F\",\n\t\t\"requestData\": \"{\\\"smartlife.iot.smartbulb.lightingservice\\\":{\\\"transition_light_state\\\":{\\\"brightness\\\":100,\\\"ignore_default\\\":0,\\\"mode\\\":\\\"normal\\\",\\\"hue\\\":%s,\\\"saturation\\\":75,\\\"color_temp\\\":0, \\\"on_off\\\":1,\\\"transition_period\\\":2500}}}\"\n }\n}\n\n" % (tokenGenerated, colour)

    r = http.request(
        'POST', 
        url,
        body=data,
        headers={
            'Content-Type': 'application/json'
        })

    resp = json.loads(r.data.decode('utf-8'))    
    return resp

def getBulbColour(currentCarbonIntensity):
    hue = 0 
    if currentCarbonIntensity == 'very low':
        hue = 120
    elif currentCarbonIntensity == 'low':
        hue = 150
    elif currentCarbonIntensity == 'moderate':
        hue = 45
    elif currentCarbonIntensity == 'high':
        hue = 30
    elif currentCarbonIntensity == 'very high':
        hue = 1
    
    setBulbColour(hue)

def getCarbonIntensity():
    http = urllib3.PoolManager()
    url = "https://api.carbonintensity.org.uk/intensity/"

    r = http.request('GET', url)
    resp = json.loads(r.data.decode('utf-8'))

    carbonIndex = resp["data"][0]["intensity"]["index"]
    getBulbColour(carbonIndex)
    
def getUUID():
    uuid4 = getRequest("https://www.uuidtools.com/api/generate/v1/");
    return uuid4

def main(request):
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        getCarbonIntensity()
    