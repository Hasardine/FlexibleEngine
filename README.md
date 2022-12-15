# FlexibleEngine

## Best practice for Pyhton scripts
Using pyhton script, you can use **IAM agencies** & **openstacksdk-python-1x**.
Here are the steps :
- in IAM service, create 1 agency for **FunctionGraph Service** with the right permissions that you will need.
- *(optional: You can create custom policies to be include in your agency)*
- When creating the FGS function:
    - In **configuration**, select your custom agency.
    - In **code**, select the **openstacksdk-python-1x**

Then use the `FGS_Python_Token_Best_Practice.py` example

## Tools for FE

### FGS - FunctionGraph Service
- FGS_Python_Token_Best_Practice : The best practice to use AK/SK
- FGS_IAM_Token_AK_SK : Get AK/SK from an IDP link by providing the SAML API response (on web browser)
- FGS_CBR_IMS_ECS : (passing tags from initial ECS to vault to image to ECS)
    - File 1 : Create a Vault and perform a backup for a specific ECS (providing ECS ID)
    - File 2 : Create an image from latest backup from vault and create an ECS from this .

### ModelArts
- Custom_environment : Custom environment for ModelArts Notebooks
