from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import email
import base64
from apiclient import errors

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

"""Get a list of Messages from the user's mailbox.
"""


def ListMessagesMatchingQuery(service, user_id, query=""):
    """List all Messages of the user's mailbox matching the query.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      query: String used to filter messages returned.
      Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
      List of Messages that match the criteria of the query. Note that the
      returned list contains Message IDs, you must use get with the
      appropriate ID to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])

        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = (
                service.users()
                .messages()
                .list(userId=user_id, q=query, pageToken=page_token)
                .execute()
            )
            messages.extend(response["messages"])

        return messages
    except errors.HttpError as error:
        print("An error occurred: {}".format(error))


def GetMessage(service, user_id, msg_id):
    """Get a Message with given ID.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The ID of the Message required.

    Returns:
      A Message.
    """
    try:
        # message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        message = (
            service.users()
            .messages()
            .get(userId=user_id, id=msg_id, format="raw")
            .execute()
        )
        return message

    except:
        print("An error occurred")


def create_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)
    return service


def get_messages_by_sender(sender_mail, sender_name, files_path):
    service = create_service()
    messages = ListMessagesMatchingQuery(service, "me", sender_mail)

    for index, _ in enumerate(messages):
        msg = GetMessage(service, "me", messages[index]["id"])
        msg_str = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))
        mime_msg = email.message_from_string(msg_str.decode())

        with open(files_path + f"\{sender_name}\{sender_name}_{index}.eml", "w+") as f:
            gen = email.generator.Generator(f)
            gen.flatten(mime_msg)


if __name__ == "__main__":
    get_messages_by_sender(
        "Sony@email.sonyentertainmentnetwork.com‏",
        "Sony",
        "C:\\code_projects\\RecieptDownloader",
    )
