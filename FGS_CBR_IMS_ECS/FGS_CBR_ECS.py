#!/usr/bin/python
# Author: Hasardine

# Create CBR backup
# You need to create APIG on Flexible Engine with ecs_id as parameter to path
# APIG : https://5487818Example4544.apigateway.eu-west-0.prod-cloud-ocb.orange-business.com/cbr/{ecs_id}

import requests
from requests.packages import urllib3
import json

# Account & password for dev
account = "xx.xxx"
apipass = "xxxxx"
domainID = "OCB000xx"
projectId = "projectid"
backupPolicy = "9c5c4fee-b86a-40a8-a170-db6914b4ffe2"
#ecs_id after getting event for demo only
#ecs_id_demo = "4dc3c6eb-cafd-4bbe-ad89-068c3a08fb9a"

def handler (event, context):
    # Get ECS ID from APIG (as input)
    ecs_id = event['pathParameters']['ecs_id']
    ecs_idText = ">>>>>>ECS ID : " + ecs_id +"<br><br>"

    #For dev  demo only :
    #ecs_id = "4dc3c6eb-cafd-4bbe-ad89-068c3a08fb9a"

    # ====================== Get API token From API password ======================

    urlToken = "https://iam.eu-west-0.prod-cloud-ocb.orange-business.com/v3/auth/tokens"

    payloadToken = "{\r\n    \"auth\": {\r\n        \"identity\": {\r\n            \"methods\": [\r\n                \"password\"\r\n            ],\r\n            \"password\": {\r\n                \"user\": {\r\n                    \"name\": \"" + account +"\"  ,\r\n                    \"password\": \"" +apipass+ "\",\r\n                    \"domain\": {\r\n                        \"name\": \""+domainID+"\"\r\n                    }\r\n                }\r\n            }\r\n        },\r\n        \"scope\": {\r\n            \"project\": {\r\n                //big_data\r\n                \"id\": \""+projectId+"\"\r\n                }\r\n        }\r\n    }\r\n}"
    headersToken = {
      'ContentType': 'application/json;charset=utf8 ',
      'Content-Type': 'text/plain'
    }

    responseToken = requests.request("POST", urlToken, headers=headersToken, data=payloadToken)

    #debug
    #print(payloadToken)
    #print(responseToken.text)


    unscoped_token = responseToken.headers.get("x-subject-token") if "x-subject-token" in responseToken.headers.keys() else None
    if unscoped_token:
        token = ">>>>>>X-Subject-Token: " + unscoped_token

    #For other project #code : B4J1
    # ====================== Get ECS details (ecs id) ======================

    urlEcs = "https://ecs.eu-west-0.prod-cloud-ocb.orange-business.com/v1/"+projectId+"/cloudservers/"+ecs_id

    payloadEcs = ""
    headersEcs = {
        'X-Auth-Token': unscoped_token,
       'Content-Type': 'text/plain'
    }

    responseEcs = requests.request("GET", urlEcs, headers=headersEcs, data=payloadEcs)

    ecsData = json.loads(responseEcs.text)  
    ecsName = ecsData['server']['name']
    ecsImage = ecsData['server']['metadata']['image_name']
    ecsBit = ecsData['server']['metadata']['os_bit']

    tags = ecsData['server']['tags']


    # GET TAGS TODO

    #ecsOs = " <br><br> >>>>>>ECS details: " + ecsName + " " + ecsImage + " " + ecsBit +"bit" 

    # ======================= Get all EVS disk from ECS (ecs id) ======================

    urlEvs = "https://ecs.eu-west-0.prod-cloud-ocb.orange-business.com/v2.1/servers/"+ecs_id+"/block_device"

    payloadEvs = ""
    headersEvs = {
      'X-Auth-Token': unscoped_token
    }
 
    responseEvs = requests.request("GET", urlEvs, headers=headersEvs, data=payloadEvs)
    evsJson = json.loads(responseEvs.text)
    volumeList = evsJson['volumeAttachments']
    evsList = [(elem['id']) for elem in volumeList]
    i=0
    for size in volumeList :
        i = i + int(size['size'])
    
    evsTotalsize = i*2
    evsListDisplay = ', '.join(evsList)
 
    evsDetails = "<br><br> EVS list >>>>>> :" + evsListDisplay + "<br><br> EVS size (x2) >>>>>>  :" + str(evsTotalsize)

   # ====================== Create vault (ecs name) ======================

    urlVault = "https://cbr.eu-west-0.prod-cloud-ocb.orange-business.com/v3/"+projectId+"/vaults"

    vaultName = "vault-"+ecs_id

    #Tags from json list to str for playload
    listTag=[]
    for item in tags:
        tritem = str(item).split("=")
        listTag.append({'key':tritem[0],'value':tritem[1]})

    payloadVault = {"vault": {
        "name": vaultName,
        "resources": [
          {
            "id": ecs_id,
            "type": "OS::Nova::Server"
          }
        ],
        "billing": {
          "size": evsTotalsize,
          "consistent_level": "crash_consistent",
          "protect_type": "backup",
          "object_type": "server",
          "cloud_type": "public"
        },
        "backup_policy_id": backupPolicy,
        "tags" : listTag
      }}
    headersVault = {
      "content-type": "application/json",
      "X-Auth-Token": unscoped_token
    }

    print(payloadVault)

    responseVault = requests.request("POST", urlVault, json=payloadVault, headers=headersVault)
    print(responseVault.text)
    vaultId = json.loads(responseVault.text)['vault']['id']

    vaultDetails = "<br><br> Vault >>>>>>> id: " + vaultId + "<br>" + responseVault.text


    # ====================== Run first backup  ======================

    urlCheckpoint = "https://cbr.eu-west-0.prod-cloud-ocb.orange-business.com/v3/"+projectId+"/checkpoints"

    payloadCheckpoint = {"checkpoint": {
        "vault_id": vaultId
      }}
    headersCheckpoint = {
      "content-type": "application/json",
      "X-Auth-Token": unscoped_token
    }

    responseCheckpoint = requests.request("POST", urlCheckpoint, json=payloadCheckpoint, headers=headersCheckpoint)

    # ====================== Display ======================

    bodythis = ecs_idText + token + str(tags) + evsDetails + vaultDetails + responseCheckpoint.text
    
    return {
        "statusCode":200,
        "body":bodythis,
        "headers": {
            "Content-Type": "text/html",
        },
        "isBase64Encoded": False
    }
