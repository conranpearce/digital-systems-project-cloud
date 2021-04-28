import json
import urllib3

# AWS lambda function to turn a TP-Link bulb's colour relating to the current carbon intensity of the National Grid

# Basic get request
def getRequest(url):
    http = urllib3.PoolManager()
    resp = http.request('GET', url)
    return resp.status

# Get the TP-Link token using a UUID
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

# Set the TP-Link bulb colour through a POST request
def setBulbColour(colour):
    uuid = getUUID()
    tokenGenerated = getToken(uuid)
    
    http = urllib3.PoolManager()
    url = "https://wap.tplinkcloud.com"

    data =  "{\n \"method\": \"passthrough\",\n \"params\": {\n \"token\": \"%s\",\n \"deviceId\": \"***\",\n\t\t\"requestData\": \"{\\\"smartlife.iot.smartbulb.lightingservice\\\":{\\\"transition_light_state\\\":{\\\"brightness\\\":100,\\\"ignore_default\\\":0,\\\"mode\\\":\\\"normal\\\",\\\"hue\\\":%s,\\\"saturation\\\":75,\\\"color_temp\\\":0, \\\"on_off\\\":1,\\\"transition_period\\\":2500}}}\"\n }\n}\n\n" % (tokenGenerated, colour)

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
    
    setBulbColour(hue)

# Get the current carbon intensity, provided by the National Grid API
def getCarbonIntensity():
    http = urllib3.PoolManager()
    url = "https://api.carbonintensity.org.uk/intensity/"

    r = http.request('GET', url)
    resp = json.loads(r.data.decode('utf-8'))

    carbonIndex = resp["data"][0]["intensity"]["index"]
    getBulbColour(carbonIndex)
    
# Get a UUID    
def getUUID():
    uuid4 = getRequest("https://www.uuidgenerator.net/api/version4");
    return uuid4

# Main function, invoked by the cloud function
def lambda_handler(event, context):    
    getCarbonIntensity()
