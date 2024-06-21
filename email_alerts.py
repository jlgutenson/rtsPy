# built-in imports
import os
import base64
from email.message import EmailMessage
from datetime import datetime, timezone

# third party imports
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def gmail_send_message(subject, body, to_email, from_email, credentials):
    """
    Follow these instructions to get your authentication set up properly:
    https://developers.google.com/gmail/api/quickstart/python
    
    Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    You will need to do a one time authetication with your email
    through a browser window. 
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials, SCOPES
            )
            creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())


    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        message.set_content(body)

        message["To"] = to_email
        message["From"] = from_email
        message["Subject"] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message

def check_results(results_folder):
    """
    checks the current date to see if the results folder has results for today
    """
    current_time = datetime.now(timezone.utc)

    date = current_time.strftime("%Y%m%d")

    todays_results_folder = os.path.join(results_folder, date)

    if os.path.exists(todays_results_folder) is True:
        up_to_date = True
    else:
        up_to_date = False


    return up_to_date


if __name__ == "__main__":
    # email subject
    subject = "Alert: Hydrologic forecasts aren't running!"
    # email message
    body = "The hydrologic forecasts haven't ran today."
    # who you're emailing
    to_email = "jlgutenson@office.ratesresearch.org"
    # Gmail account that is sending the email
    from_email = "jlgutenson@ratesresearch.org"
    # OAuth Credentials
    credentials = "/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/build_hms_inputs/credentials.json"
    # folder where all model results are stored
    results_folder = "/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/build_hms_inputs/hrrr_subhourly/"
    # results_folder = "/home/jlgutenson/rtspy/hrrr_subhourly/"


    # check if the results folder 
    up_to_date = check_results(results_folder)

    if up_to_date is False:
        # now run the thing
        gmail_send_message(subject, body, to_email, from_email, credentials)
    else:
        "Looks like we have results for today at least."