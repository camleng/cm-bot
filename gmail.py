import base64
import os
from argparse import Namespace
from logging import NOTSET

from apiclient import discovery, errors
from oauth2client import client, tools
from oauth2client.file import Storage
import httplib2

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

    def get_last_email_id(self, service, query=''):
        messages = self.build_messages(service)
        return messages[0]['id']
    
    def get_new_credentials(self):
        scopes = 'https://www.googleapis.com/auth/gmail.readonly'        
        self.make_credential_dir()
        credential_path = os.path.join(self.credential_dir, 'cm-bot.json')        
        client_secret_path = os.path.join(self.credential_dir, 'client_secret.json')   
        flow = client.flow_from_clientsecrets(client_secret_path, scopes)
        flow.user_agent = 'CM Bot'
        store = Storage(credential_path)
        credentials = tools.run_flow(flow, store, self.get_flags())
        print(f'Storing credentials to {credential_path}')
        return credentials

    def make_credential_dir(self):
        if not os.path.exists(self.credential_dir):
            os.makedirs(self.credential_dir)

    def get_credentials(self):
        """Gets stored oauth2 credentials
        """
        self.make_credential_dir()
        credential_path = os.path.join(self.credential_dir, 'cm-bot.json')

        credentials = Storage(credential_path).get()
        if not credentials or credentials.invalid:
            credentials = self.get_new_credentials()
        return credentials

    def authorize(self):
        # authorize with oauth2
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        return discovery.build('gmail', 'v1', http=http)

    def get_email_info(self, service, msg_id):
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

    def get_flags(self):
        kwargs = {
            'auth_host_name': 'localhost',
            'noauth_local_webserver': False,
            'auth_host_port': [8080, 8090],
            'logging_level': 'ERROR'
        }
        return Namespace(**kwargs)
