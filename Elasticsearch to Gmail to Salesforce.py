# This was created when I was working at a SaaS company.
# Technology Inovled: Eleasticsearch, Salesforce, SaaS product, Gmail IMAP, & Python.

# The requirement:
# Whenever there is a new user sign up...the STATUS field (Contact Object) in salesforce needs to be updated. If the user was not already in SF then we had to create a new user
# in the LEAD object and also populate the STATUS field.

# Solution: We used Elasticsearch feature of sending alerts to mailbox. So whenever a user signed up this alert was triggered and the user's email was sent to the mailbox. We 
# then set up a task schedule on windows machine to run the below python script to parse the email from the mailbox and use it to query SF and update the impacted fields. 

import imaplib
import email
import datetime
import re
from simple_salesforce import Salesforce, SalesforceLogin


# INSERT APP PASSWORD HERE
imap_host, imap_user, imap_pass = (
    "gmail.com",
    "email@email.com",
    "xxx",
)


#EMAIL_PATTERN = r"Cognito Sign Up: Success <code>([\s\S]*?)</code>"
EMAIL_PATTERN = r"([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)"
# catches all emails

#Adding dates to variables
today = datetime.datetime.today().strftime("%Y-%m-%d")
todayimap = datetime.datetime.today().strftime("%d-%b-%Y")
yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
yesterdayimap = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%d-%b-%Y")


my_mail = imaplib.IMAP4_SSL(imap_host)
my_mail.login(imap_user, imap_pass)
my_mail.select("shared mailbox")
KEY = "FROM"
VALUE = "noreply@alerts.elastic.co"
_, data = my_mail.search(None, KEY, VALUE, f"(SENTSINCE {yesterdayimap})")
mail_id_list = data[0].split()


msgs = []
for num in mail_id_list:
    typ, data = my_mail.fetch(num, "(RFC822)")
    msgs.append(data)

# Parses Email body for the last 1 day and creates
# a list with the email id's that a found.
master_list = []
for msg in msgs[::-1]:
    for response_part in msg:
        if type(response_part) is tuple:
            my_msg = email.message_from_bytes((response_part[1]))
            for part in my_msg.walk():
                if part.get_content_type() == "text/html":
                    html_body = part.get_payload(decode=True)
                    html_body_decode = html_body.decode()
                    html_body_decode = html_body_decode.replace("\\", "")
                    find_emails = re.findall(EMAIL_PATTERN, html_body_decode)
                    for each in find_emails:
                        lower_each = each.lower()
                        master_list.append(lower_each.replace("\\", ""))


# flows security token, search 'security token' in SF setup/settings
SECURITY_TOKEN = "your security token"
USERNAME = "salesforce_username"
PASSWORD = "salesforce_password"
# domain = 'login'
SESSION_ID, INSTANCE = SalesforceLogin(
    username=USERNAME, password=PASSWORD, security_token=SECURITY_TOKEN, domain="test"
)
sf = Salesforce(instance=INSTANCE, session_id=SESSION_ID)


def sf_lookup_email(each_email):
    """Looks up an email ID in SF and checks if it's found in CONTACTS or LEAD objects.
    Appends string contact/lead/nothing based of where it's found"""

    contact_sql = "SELECT Id, Name, First_Login_Live__c FROM Contact where Email = '" + each_email + "'"
    contact_result = sf.query(contact_sql)
    row = []
    if len(contact_result["records"]) > 0:
        row.append("Contact")
        row.append(contact_result["records"][0]["Id"])
        row.append(contact_result["records"][0]["Name"])
        row.append(contact_result["records"][0]["Email"])
        row.append(contact_result["records"][0]["First_Login_Live__c"])
        return row
    else:
        lead_sql = "SELECT id, Name, Email,First_Login_Live__c FROM Lead where Email = '" + each_email + "'"
        lead_result = sf.query(lead_sql)
        if len(lead_result["records"]) > 0:
            row.append("Lead")
            row.append(lead_result["records"][0]["Id"])
            row.append(lead_result["records"][0]["Name"])
            row.append(lead_result["records"][0]["Email"])
            row.append(lead_result["records"][0]["First_Login_Live__c"])
            return row
        else:
            row.append("Nothing")
            row.append(each_email)
            return row


def upsert_contact_lead(lookup_result_list):
    """Updates SF fields if user already in SF or
    creates a new LEAD if not present"""

    if lookup_result_list[0] == "Contact":
        sf.Contact.update(lookup_result_list[1], {"Status_Live__c": "Reader"})
    elif lookup_result_list[0] == "Lead":
        sf.Lead.update(lookup_result_list[1], {"Status_Live__c": "Reader"})
    else:
        print(lookup_result_list[1])
        sf.Lead.create(
            {
                "Company": "Unknown",
                "Email": lookup_result_list[1],
                "Status_Live__c": "Reader",
                "LastName": lookup_result_list[1],
            }
        )


print(master_list)
for i in master_list:
    lookup_result = sf_lookup_email(i)
    upsert_contact_lead(lookup_result)
