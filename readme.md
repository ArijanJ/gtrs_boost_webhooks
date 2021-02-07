Small python program to notify a discord channel when a server boost is detected on gametracker.rs

## Configuration

All configuration is done in config.json:

{

    "servers": {

        "Server_Name": {

            "ip": "server_ip:20000",

            "webhook": "webhookURL",

            "lastBoost": "0"

        },

        "Second_Server_Name": {

            "ip": "server_ip:20000",

            "webhook": "webhookURL",

            "lastBoost": "0"

        }

    }

}
