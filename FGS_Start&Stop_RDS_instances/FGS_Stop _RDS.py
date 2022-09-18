#!/usr/bin/python
# Author: Hasardine
# Python 3.6

# Stop instance
# APIG : https://rds.eu-west-0.prod-cloud-ocb.orange-business.com/v3/{project-id}/instances/{instance-id}/action/shutdown 

import requests
from requests.packages import urllib3


# Account & password for dev
account = "xxxx.xx"
apipass = "xxxxxxxxx"
domainID = "OCBxxxxxx"
projectId = "xxxxxxxxxxxx"
instanceId = "xxxxxxxxx"

def handler (event, context):
  
  # ====================== Get API token From API password ======================
  urlToken = "https://iam.eu-west-0.prod-cloud-ocb.orange-business.com/v3/auth/tokens"

  payloadToken = "{\r\n    \"auth\": {\r\n        \"identity\": {\r\n            \"methods\": [\r\n                \"password\"\r\n            ],\r\n            \"password\": {\r\n                \"user\": {\r\n                    \"name\": \"" + account+"\" ,\r\n                    \"password\": \"" +apipass+ "\",\r\n                    \"domain\": {\r\n                        \"name\": \""+domainID+"\"\r\n                    }\r\n                }\r\n            }\r\n        },\r\n        \"scope\": {\r\n            \"project\": {\r\n                //big_data\r\n                \"id\": \""+projectId+"\"\r\n                }\r\n        }\r\n    }\r\n}"
  headersToken = {
    'ContentType': 'application/json;charset=utf8 ',
    'Content-Type': 'text/plain'
  }

  responseToken = requests.request("POST", urlToken, headers=headersToken, data=payloadToken)

  unscoped_token = responseToken.headers.get("x-subject-token") if "x-subject-token" in responseToken.headers.keys() else None

  # ====================== Stop RDS Instance ======================


  urlRds = "https://rds.eu-west-0.prod-cloud-ocb.orange-business.com/v3/"+projectId+"/instances/"+instanceId+"/action/shutdown"

  headersRds = {
    "content-type": "application/json",
    "X-Auth-Token": unscoped_token,
    "X-Language": "en-us"
  }

  responseRds = requests.request("POST", urlRds, headers=headersRds)

  print(responseRds.text)


