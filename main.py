import requests
import time
import json

updateInterval = 120 # Seconds to update

jsonFile = {}
dumpedJson = {}

def loadJson():
    global jsonFile
    with open('config.json', 'r') as file:
        jsonFile = json.load(file)
        file.close()

def formatTime(lastTime):
    return time.strftime('%H:%M:%S', time.localtime(lastTime))

def sendWebhook(server, name, lastTime, stat):

    webhook = {}
    webhook["embeds"] = []
    embed = {}
    
    if stat == "ok":
        emoteStat = ":white_check_mark:"
        embed["color"] = 3066993
    else:
        emoteStat = ":x:"
        embed["color"] = 15158332

    embed["title"] = jsonFile['translation']['title'] + ' ' + emoteStat
    embed["description"] = jsonFile['translation']['content'].format(name = name, localtime = formatTime(lastTime), status = stat) 

    webhook["embeds"].append(embed)

    print("Sending webhook with name " + name + " at time " + formatTime(lastTime) + " with status " + stat + " in " + str(len(jsonFile['servers'][server]['webhooks'])) + " servers.")

    for url in jsonFile['servers'][server]['webhooks']:

        result = requests.post(url, data = json.dumps(webhook), headers = {"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Webhook sent successfully")

loadJson()
print("Running for:")
for server in jsonFile['servers']:
    print(server)

while True:

    # Get JSON
    for server in jsonFile['servers']:

        try:
            jsonApi = requests.get("http://api.gametracker.rs/demo/json/server_boosts/" + jsonFile['servers'][server]['ip'])
        except (TimeoutError, ConnectionError) as err:
            print("Request error:" + err)
            continue;

        dumpedJson = jsonApi.json() 

        if dumpedJson['apiError']:
            print("apiError occured.")
            continue;

        try:
            lastBoost = dumpedJson['boosts'][0]['boost']
        except:
            continue

        actualLastBoostTime = int(lastBoost['time'])

        server_lastBoost = jsonFile['servers'][server]['lastBoost']

        # Compare and send webhook
        if int(server_lastBoost) < actualLastBoostTime and lastBoost['status'] != "pending":
            server_lastBoost = actualLastBoostTime
            print("Got new boost at " + '[' + formatTime(server_lastBoost) + '] on server ' + server)

            sendWebhook(server, lastBoost['name'], server_lastBoost, lastBoost['status'])

            with open('config.json', 'w+') as file:
                print("Writing " + lastBoost['time'])
                jsonFile['servers'][server]['lastBoost'] = lastBoost['time']
                json.dump(jsonFile, file, indent=4)

                file.close()

        time.sleep(updateInterval / len(jsonFile['servers']))
