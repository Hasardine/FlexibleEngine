# -*- coding:utf-8 -*-
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

    import requests

    url = "https://iam.eu-west-0.prod-cloud-ocb.orange-business.com/v3/auth/tokens"

    payload={}
    headers = {
        'X-Auth-Token': token,
        'X-Subject-Token': token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)



    
