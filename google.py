import json 
import urllib3

# Google cloud function to turn a TP-Link bulb's colour relating to the current carbon intensity of the National Grid

# Get request template
def getRequest(url):
    http = urllib3.PoolManager()
    resp = http.request('GET', url)
    return resp.status

# Get the TP-Link token using a UUID
def getToken(username, password, uuid):
    http = urllib3.PoolManager()
    url = "https://wap.tplinkcloud.com"

    data = "{\n \"method\": \"login\",\n \"params\": {\n \"appType\": \"Kasa_Android\",\n \"cloudUserName\": \"%s\",\n \"cloudPassword\": \"%s\",\n \"terminalUUID\": \"%s\"\n }\n}" % (username, password, uuid)

    r = http.request(
        'POST', 
        url,
        body=data,
        headers={
            'Content-Type': 'application/json'
        })

    resp = json.loads(r.data.decode('utf-8'))
    return resp['result']['token']

# Set the TP-Link bulb colour through a POST request
def setBulbColour(colour, tokenGenerated, deviceId):    
    http = urllib3.PoolManager()
    url = "https://wap.tplinkcloud.com"

    data =  "{\n \"method\": \"passthrough\",\n \"params\": {\n \"token\": \"%s\",\n \"deviceId\": \"%s\",\n\t\t\"requestData\": \"{\\\"smartlife.iot.smartbulb.lightingservice\\\":{\\\"transition_light_state\\\":{\\\"brightness\\\":100,\\\"ignore_default\\\":0,\\\"mode\\\":\\\"normal\\\",\\\"hue\\\":%s,\\\"saturation\\\":75,\\\"color_temp\\\":0, \\\"on_off\\\":1,\\\"transition_period\\\":2500}}}\"\n }\n}\n\n" % (tokenGenerated, deviceId, colour)

    r = http.request(
        'POST', 
        url,
        body=data,
        headers={
            'Content-Type': 'application/json'
        })

    resp = json.loads(r.data.decode('utf-8'))    
    return resp

# Set the bulb hue depending on the current carbon intensity index
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

    return hue
    
# Get the current carbon intensity, provided by the National Grid API
def getCarbonIntensity():
    http = urllib3.PoolManager()
    url = "https://api.carbonintensity.org.uk/intensity/"

    r = http.request('GET', url)
    resp = json.loads(r.data.decode('utf-8'))

    carbonIndex = resp["data"][0]["intensity"]["index"]

    return carbonIndex

# Get UUID to pass into token    
def getUUID():
    uuid4 = getRequest("https://www.uuidtools.com/api/generate/v1/");
    return uuid4

# Main function, invoked by the cloud function
def main(request):
    request_json = request.get_json()
    if request_json:
        deviceId = request_json['deviceId']
        username = request_json['username']
        password = request_json['password']

        carbonIndex = getCarbonIntensity()
        bulbColour = getBulbColour(carbonIndex)
        uuid = getUUID()
        token = getToken(username, password, uuid)
        setBulbColour(bulbColour, token, deviceId)

    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else
        return "error"
    