from configparser import ConfigParser
import requests
import time
import json

lastBoostTime = 0
updateInterval = 10 # Seconds to update

dumpedJson = {}

webhook = {}
webhook["embeds"] = [] 

config = {}

def loadConfig():
    global lastBoostTime
    cfg = ConfigParser()
    cfg.read('config.ini')

    config["token"] = cfg.get('configuration', 'token')
    config["ip_address"] = cfg.get('configuration', 'ip_address')
    with open('last.ini', 'r') as file:
        lines = file.readlines()
        if len(lines) != 0:
            lastBoostTime = int(lines[0])
        file.close()


    config["title"] = cfg.get('text', 'title')
    config["content"] = cfg.get('text', 'content')

def formatTime(lastTime):
    return time.strftime('%H:%M:%S', time.localtime(lastTime))

def sendWebhook(name, lastTime, stat):
    print("Sending webhook with name " + name + " at time " + formatTime(lastTime) + " with status " + stat)

    embed = {}
    embed["title"] = config["title"]
    embed["description"] = config["content"].format(name = name, localtime = formatTime(lastTime), status = stat) 

    if stat == "ok":
        embed["color"] = 3066993
    else:
        embed["color"] = 15158332

    webhook["embeds"].append(embed)

    result = requests.post(config["token"], data = json.dumps(webhook), headers = {"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Webhook sent successfully")

loadConfig()
print("Running for " + config["ip_address"])

while True:

    # Get JSON
    jsonApi = requests.get("http://api.gametracker.rs/demo/json/server_boosts/" + config["ip_address"])
    dumpedJson = jsonApi.json() 

    lastBoost = dumpedJson['boosts'][0]['boost']

    actualLastBoostTime = int(lastBoost['time'])

    # Compare and send webhook
    if lastBoostTime < actualLastBoostTime:
        lastBoostTime = actualLastBoostTime
        print("Got new boost at " + '[' + formatTime(lastBoostTime) + ']')
        sendWebhook(lastBoost['name'], lastBoostTime, lastBoost['status'])

        with open('last.ini', 'w+') as file:
            lines = file.readlines()

            file.truncate(0)
            file.write(str(lastBoostTime))

            file.close()

    time.sleep(updateInterval)