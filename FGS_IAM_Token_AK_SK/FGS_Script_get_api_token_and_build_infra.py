#!/usr/bin/python
# Author: Hasardine

#Needed :
#APIG that Give SAML Response
#IdP set up for API (no console access)
#Project Id

idpName = 'jump_um_api'
projectId = "cac40e407e8944bdafe047c04a6d6d91"

import json
import sys
import requests
from requests.packages import urllib3
import time
import getpass
#from bs4 import BeautifulSoup (automation to parse HTML page)
from urlparse import urlparse


def handler (event, context):
    print(event['pathParameters']['samlb'])
    SAMLapi = event['pathParameters']['samlb']

    # ====================== Get tokens =========================
    # SSL certificate verification: Set false for dev
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    sslverification = False
    session = requests.Session()

    #Get the response from HTTP Request from SSO to IDP provider:
    SAMLResponse = SAMLapi

    # error handling (not required for FGS as API will handle it)
    if (SAMLResponse == ''):
        print 'If Manual script, please fill SAMLResponse'
        sys.exit(0)

    ##====================== get unscoped token ======================

    # Set headers
    # You need to set uour IDP name on Flexible Engine
    headers = {}
    headers["X-Idp-Id"] = idpName

    # IAM API url: get unscoped token on IDP initiated mode
    sp_unscoped_token_url = "https://iam.eu-west-0.prod-cloud-ocb.orange-business.com/v3.0/OS-FEDERATION/tokens"

    # Set form data
    payload = {}
    payload["SAMLResponse"] = SAMLResponse
    response = session.post(
        sp_unscoped_token_url, data=payload, headers=headers, verify=sslverification)

    # Debug only
    #print("response text" + response.text)
    #print json.dumps(dict(response.headers))
    #print "Status Code: " + str(response.status_code)
    if response.status_code != 201:
        sys.exit(1)

    unscoped_token = response.headers.get("x-subject-token") if "x-subject-token" in response.headers.keys() else None
    if unscoped_token:
        print ">>>>>>X-Subject-Token: " + unscoped_token

    ##====================== get STS token (AK/SK) ======================

    #  Set form data
    # The duration can not exceed 24h
    payload = {
        "auth": {
            "identity": {
                "methods": ["token"],
                "token": {
                    "duration-seconds": "3600"
                }
            }
        }
    }

    # Set headers
    headers = {}
    headers["X-Auth-Token"] = unscoped_token
    sp_STS_token_url = "https://iam.eu-west-0.prod-cloud-ocb.orange-business.com/v3.0/OS-CREDENTIAL/securitytokens"

    response = session.post(
        sp_STS_token_url, json=payload, headers=headers, verify=sslverification)

    # Debug ??

    #print "Status Code: " + str(response.status_code)
    if response.status_code != 201:
        print response.text
        sys.exit(1)

    sts_token = response.text if response.status_code == 201 else None
    if sts_token:
        print ">>>>>>STS Token:" + sts_token

    ##====================== get scoped token ======================
    #name = "eu-west-0"
    payload = {
        "auth": {
            "identity": {
                "methods": ["token"],
                "token": {
                    "id": unscoped_token
                }
            },
            "scope": {
                "project": {
                    "id": projectId
                }
            }
        }
    }

    sp_scoped_token_url = "https://iam.eu-west-0.prod-cloud-ocb.orange-business.com/v3/auth/tokens"

    response = session.post(
        sp_scoped_token_url, json=payload, verify=sslverification)

    # === Debug only ===
    #print "Status Code: " + str(response.status_code)
    #if response.status_code != 201:
    #    print response.text
    #    sys.exit(1)

    scoped_token = response.text if response.status_code == 201 else None
    if scoped_token:
        print ">>>>>>Scoped Token:" + scoped_token

    apiToken = response.headers.get("x-subject-token") if "x-subject-token" in response.headers.keys() else None
    if apiToken:
        print ">>>>>>X-Subject-Token to use: " + apiToken

    # ============ END of tokens =======

    # ================== API call to create infra =========================

    #Build Vpc
    urlVpc = "https://vpc.eu-west-0.prod-cloud-ocb.orange-business.com/v1/cac40e407e8944bdafe047c04a6d6d91/vpcs"

    payloadVpc = "{\r\n    \"vpc\": {\r\n        \"name\": \"vpc-um\",\r\n        \"description\": \"apitest\",\r\n        \"cidr\": \"10.1.0.0/16\"\r\n    }\r\n}"
    headersVpc = {
        'X-Auth-Token': apiToken,
        'Content-Type': 'text/plain'
    }

    responseVpc = requests.request("POST", urlVpc, headers=headersVpc, data=payloadVpc) 

    #Extract Vpc id :
    vpcData = json.loads(responseVpc.text)
    vpcId = vpcData['vpc']['id']

    #Build Subnet 
    urlSub = "https://vpc.eu-west-0.prod-cloud-ocb.orange-business.com/v1/cac40e407e8944bdafe047c04a6d6d91/subnets"

    payloadSub = "{\r\n \"subnet\": {\r\n \"name\": \"umsubnet\",\r\n \"description\": \"\",\r\n \"cidr\": \"10.1.16.0/24\",\r\n \"gateway_ip\": \"10.1.16.1\",\r\n \"ipv6_enable\": true,\r\n \"dhcp_enable\": true,\r\n \"primary_dns\": \"100.125.0.41\",\r\n \"secondary_dns\": \"100.126.0.41\",\r\n \"availability_zone\": \"eu-west-0a\", \r\n \"vpc_id\": \"" + vpcId + "\" \r\n }\r\n}\r\n"
    headersSub = {
      'X-Auth-Token': apiToken,
      'Content-Type': 'text/plain'
    }

    responseSub = requests.request("POST", urlSub, headers=headersSub, data=payloadSub)
    #debug
    #print(payloadSub)
    #print(responseSub.text) 

    #Extract subnet id :
    subData = json.loads(responseSub.text)
    subID = subData['subnet']['id']

    #Build EIP
    urlEIP = "https://vpc.eu-west-0.prod-cloud-ocb.orange-business.com/v1/cac40e407e8944bdafe047c04a6d6d91/publicips"

    payloadEIP = "{\r\n    \"publicip\": {\r\n        \"type\": \"5_bgp\",\r\n        \"ip_version\": 4\r\n    },\r\n    \"bandwidth\": {\r\n        \"name\": \"um-api\",\r\n        \"size\": 10,\r\n        \"share_type\": \"PER\"\r\n    }\r\n}"
    headersEIP = {
        'X-Auth-Token': apiToken,
        'Content-Type': 'text/plain'
        }

    responseEIP = requests.request("POST", urlEIP, headers=headersEIP, data=payloadEIP)
    print(responseEIP.text)
    EipData = json.loads(responseEIP.text)
    eipId = EipData['publicip']['id']

    time.sleep(2)

    #=========ECS=============
    #Build ECS
    urlECS = "https://ecs.eu-west-0.prod-cloud-ocb.orange-business.com/v1/cac40e407e8944bdafe047c04a6d6d91/cloudservers"

    payloadECS = "{\r\n    \"server\": {\r\n        \"availability_zone\": \"eu-west-0b\",\r\n        \"name\": \"um-api-ecs\",\r\n        \"imageRef\": \"a4b175e9-ad85-4b4d-aa36-7dd34a85a10d\",\r\n        \"root_volume\": {\r\n            \"volumetype\": \"SSD\"\r\n        },\r\n        \"data_volumes\": [\r\n            {\r\n                \"volumetype\": \"SSD\",\r\n                \"size\": 100\r\n            },\r\n            {\r\n                \"volumetype\": \"SSD\",\r\n                \"size\": 100,\r\n                \"multiattach\": true,\r\n                \"hw:passthrough\": true\r\n            }\r\n        ],\r\n        \"flavorRef\" : \"s6.large.2\",\r\n        \"vpcid\": \""+vpcId+"\",\r\n        \"nics\": [\r\n            {\r\n                \"subnet_id\": \""+subID+"\"\r\n            }\r\n        ],\r\n        \"publicip\": {\r\n            \"id\": \""+ eipId +"\"\r\n        },\r\n        \"adminPass\": \"Has4rdin3!\",\r\n        \"count\": 1\r\n    }\r\n}"
    headersECS = {
    'X-Auth-Token': apiToken,
    'Content-Type': 'text/plain'
    }

    print (payloadECS)

    responseECS = requests.request("POST", urlECS, headers=headersECS, data=payloadECS)

    #print(responseECS.text)

    #Get job response :
    jobdata = json.loads(responseECS.text)
    jobid = jobdata['job_id']

    #Wait for 3s to ensure ECS job creation
    time.sleep(3)

    #Query Job to obtain ECS ID
    urlECSID = "https://ecs.eu-west-0.prod-cloud-ocb.orange-business.com/v1/cac40e407e8944bdafe047c04a6d6d91/jobs/" + jobid

    payloadECSID = ""
    headersECSID = {
      'X-Auth-Token': apiToken
    }


    responseECSID = requests.request("GET", urlECSID, headers=headersECSID, data=payloadECSID)

    print(responseECSID.text)

    # ================== Display to user ======================

    body = "<html><title>Functiongraph Demo</title><body><p>Hello, UM Demo!</p></body></html>"
    tokenapi = " <br><br> >>>>>>Scoped Token: <br>" + apiToken
    Vpcdetails = "<br><br> Vpc details: <br>" + responseVpc.text 
    vpcids = "<br><br>" + vpcId
    SubDetails = "<br><br> Subnet details: <br>" + responseSub.text
    EIPdetails = "<br><br> EIP detail:  <br> " + responseEIP.text
    ECSInfos = "<br><br> ECS detail:  <br> " + payloadECS

    bodythis = body + tokenapi + Vpcdetails + SubDetails + EIPdetails + vpcids + ECSInfos
    return {
        "statusCode":200,
        "body":bodythis,
        "headers": {
            "Content-Type": "text/html",
        },
        "isBase64Encoded": False
    }





