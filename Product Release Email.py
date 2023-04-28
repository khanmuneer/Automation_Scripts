# Just before the annual product update our team wanted to reach out to select users and gather their feedback. 
# I created this script to send out personalized email to multiple users with their activation codes and other details. 
# We use Outlook at our org so this is specific to Outlook. 

import win32com.client as win32
import win32com.client as client
import pandas as pd


# specify the full file path to the Excel file
file_path = 'YOUR LOCAL PATH'

# use HTML template that needs to be sent out
html_file_path = 'HTML TEMPLATE.html'

# add you SF email if you want to log the emails sent to the users
SF_EMAIL = "YOUR SF EMAIL"

# read recipient email addresses, first names, IDs, and seats from Excel
df = pd.read_excel(file_path)
recipients = df[['Email', 'First Name', 'Activation ID', '# of Licenses']].to_dict('records')

outlook = win32.Dispatch('outlook.application')

# read the contents of the HTML file
with open(html_file_path, 'r') as file:
    html = file.read()

# send the email to each recipient on the excel file
for recipient in recipients:
    try:
        mail = outlook.CreateItem(0)
        to = recipient['Email']
        first_name = recipient['First Name']
        id = recipient['ID']
        seats = recipient['Seats']
        # create the HTML message with the recipient's first name and ID and Licenses
        html_personalized = html.format(first_name=first_name, id=id, seats=seats)
        mail.BCC = SF_EMAIL
        mail.to = to
        mail.Subject = 'YOU SUBJECT®'
        mail.HTMLBody = html_personalized
        mail.SentOnBehalfOfName = 'common@company.com'
        mail.Send()
    except Exception as e:
        print(e)
        print(f'Error sending email to {to}: {e}')
        outlook = None
        outlook = win32.Dispatch('outlook.application')
