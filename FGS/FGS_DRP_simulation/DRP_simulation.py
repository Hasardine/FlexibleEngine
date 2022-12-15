# -*- coding:utf-8 -*-
# Author : Benjamin.M / Hasardine
# Function : DRP simultaion : This function list simulate 1 AZ shutdown

# Detail : 
# Choose one AZ (eu-west-0a)
# List project
# list all ECS from each prject that AZ
# shutdown them all

# Choose AZ :

import json
import requests
from openstack import connection #Require public dependency:openstacksdk-python-1.x

def handler(event, context):

    # Some of contexts you can use from the SDK
    ak = context.getAccessKey()
    sk = context.getSecretKey()
    projectid = context.getProjectID()
    logger = context.getLogger()
    project = context.getProjectID()   
    #get token           
    token = context.getToken()

    # ====================== Get API token From API password ======================

#    import requests
#
#    url = "https://iam.eu-west-0.prod-cloud-ocb.orange-business.com/v3/auth/tokens"
#
#    payload={}
#    headers = {
#        'X-Auth-Token': token,
#        'X-Subject-Token': token
#    }
#
#    response = requests.request("GET", url, headers=headers, data=payload)
#
#    print(response.text)


    # ====================== list all project accessible by me (Agency in this case) that contain eu-west-0 in name ======================


    urlProject = "https://iam.eu-west-0.prod-cloud-ocb.orange-business.com/v3/projects"

    payloadProject={}
    headersProject = {
      'X-Auth-Token': token
    }

    responseProject = requests.request("GET", urlProject, headers=headersProject, data=payloadProject)

    # List all project that contains eu-west-0 (Paris datacenter)

    #print(responseProject.text)
    projectdata = json.loads(responseProject.text)
    #print(projectdata)
    projectidinlist = projectdata['projects']
    projectlist = [(elem['id']) for elem in projectidinlist if "eu-west-0" in elem['name']]
    projectdisplay = ', '.join(projectlist)
    print(projectdisplay)

    # ====================== list all ECS from all projects thata are in specific AZ ======================

    ecsCompleteList = []
    for x in  projectlist:
        urlEcs = "https://ecs.eu-west-0.prod-cloud-ocb.orange-business.com/v2.1/cac40e407e8944bdafe047c04a6d6d91/servers/detail?"
        payloadEcs = ""
        headersEcs = {
            'X-Auth-Token': token
        }
        responseEcs = requests.request("GET", urlEcs, headers=headersEcs, data=payloadEcs)
        #print(responseEcs.text)
        ecstdata = json.loads(responseEcs.text)
        #print(projectdata)
        ecstidinlist = ecstdata['servers']
        ecstlist = [(elem['id']) for elem in ecstidinlist if "eu-west-0a" in elem['OS-EXT-AZ:availability_zone']]
        ecsCompleteList = ecsCompleteList + ecstlist
        ecsdisplay = ', '.join(ecstlist)
        print("ECS ZONE A ===>",ecsdisplay)
        print("---list--")
    
    print(ecsCompleteList)
    print(len(ecsCompleteList))

    # ====================== shutdown all ECS ======================

    #
    for x in projectlist :
        for e in ECS :
            urlEcs = "https://ecs.eu-west-0.prod-cloud-ocb.orange-business.com/v2.1/"+x+"/servers/"+e+"/action"

            payloadEcs = "{\r\n    \"os-stop\": {}\r\n}"
            headersEcs = {
            'X-Auth-Token': token,
            'Content-Type': 'text/plain'
            }

            responseEcs = requests.request("POST", urlEcs, headers=headersEcs, data=payloadEcs)

