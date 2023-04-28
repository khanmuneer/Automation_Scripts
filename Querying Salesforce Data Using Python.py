
# Import necessary packages
from simple_salesforce import Salesforce, SalesforceLogin, SFType
import pandas as pd
from pandas import json_normalize

# Define Salesforce login credentials
USERNAME = 'username'
PASSWORD = '*****'
SECURITY_TOKEN = 'YOUR SECURITY TOKEN'
instance_pl = "https://company.lightning.force.com"


# Authenticate and connect to Salesforce instance
SESSION_ID_PL, INSTANCE = SalesforceLogin(username=USERNAME, password=PASSWORD, security_token=SECURITY_TOKEN)
SF_PL = Salesforce(instance = instance_pl, session_id= SESSION_ID_PL)

# Write a SOQL query to retrieve records from any object in Salesforce
assets_object = SF_PL.query("SELECT Id, Name, Email from Contacts WHERE Email != null")

# Create a Pandas dataframe from the records returned by Salesforce using json_normalize
df_assets = json_normalize(assets_object['records'])

# Handling missing data by replacing NaN values with an empty string
df_assets.fillna("", inplace=True)

# Write the resulting dataframe to an Excel file at the specified local path
with open(r'YOUR LOCAL PATH', 'wb') as f:
    df_assets.to_excel(f, index=False)