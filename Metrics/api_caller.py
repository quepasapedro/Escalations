from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'escalations-metrics'

flags = None


def get_credentials():
    """
    Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json') # could rename this

    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)

    return credentials


def read_main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1_xbER251owgKHWjFurQ6CSC0rJevP9TSu9-JoOMcbJo'
    rangeName = 'Tickets!A:Q'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', {})

    if not values:
        print('No data found.')
    else:
        return values


def write_main(write_values, write_range):  # going to need to pass an argument here
    """Shows basic usage of the Sheets API."""

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1yphtzhkhamAe62O4dgsfecBbVJ3DTnYeBT_LPHj7ZVs'  # Metrics sheet
    rangeName = write_range  # Will fail; no sheet by that name
    valueInputOption = 'RAW'
    majorDimension = 'ROWS'

    values = write_values

    body = {"range": rangeName, "majorDimension": majorDimension, "values": values}

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheetId, range=rangeName, valueInputOption=valueInputOption, body=body).execute()
    values = result.get("updatedCells", [])

    if not values:
        print('No data found.')
    else:
        return values
        # pass


def read():
    values_list = read_main()
    return values_list

def write(to_write, write_range):
    write_main(to_write, write_range)
    pass
