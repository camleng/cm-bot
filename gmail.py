import httplib2
from apiclient import discovery, errors
from oauth2client import client, tools
from oauth2client.file import Storage
import os
import base64
from bs4 import BeautifulSoup


class Gmail:
    def __init__(self):
        current_dir = os.path.dirname(__file__)
        self.credential_dir = os.path.join(current_dir, '.credentials')

    def build_messages(self, service):
        """Uses the Gmail API to list messages matching the given query
        """
        user_id = 'me'
        query = 'subject:spiritual cyber-vitamin'
        response = service.users().messages().list(userId=user_id, q=query).execute()
        return response.get('messages', [])

    def get_last_message_id(self, service, query=''):
        messages = self.build_messages(service)
        return messages[0]['id']
    
    def get_credentials(self):
        """Gets stored oauth2 credentials
        """
        scopes = 'https://www.googleapis.com/auth/gmail.readonly'
        client_secret_file = 'client_secret.json'
        credential_file = 'groupme-bot.json'
        application_name = 'GroupMe Bot'

        if not os.path.exists(self.credential_dir):
            os.makedirs(self.credential_dir)

        credential_path = os.path.join(self.credential_dir, credential_file)
        client_secret_path = os.path.join(self.credential_dir, client_secret_file)

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(client_secret_path, scopes)
            flow.user_agent = application_name
            credentials = tools.run_flow(flow, store)
            print(f'Storing credentials to {credential_path}')
        return credentials

    def authorize(self):
        # authorize with oauth2
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        return discovery.build('gmail', 'v1', http=http)

    def get_message_info(self, service, msg_id):
        """Uses the Gmail API to extract the encoded text from the message
        and decodes it to make it readable and searchable
        """
        try:
            message = self.get_message(service, msg_id)
            headers = self.get_headers(service, msg_id)
            return message, headers
        except errors.HttpError as error:
            print(f'An error occurred: {error}')

    def decode_text(self, encoded_message):
        message = str(base64.urlsafe_b64decode(encoded_message['raw']), 'utf-8')
        return message.replace('=\r\n', '').replace('=22', '"').replace('=46', 'F').lower()

    def get_text(self, encoded_message: str):
        text = self.decode_text(encoded_message)
        return BeautifulSoup(text, 'html.parser').text

    def get_message(self, service, msg_id):
        user_id = 'me'
        encoded_message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        return self.get_text(encoded_message)

    def get_headers(self, service, msg_id):
        user_id = 'me'
        response = service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
        return response['payload']['headers']