import httplib2
import os
from datetime import datetime, timedelta
import webbrowser

import argparse
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from pyramid.view import view_config
from pyramid.response import Response


CREDENTIALS_FILE = os.path.join(os.path.expanduser('~'), '.credentials', 'lifehud-calendar')
APPLICATION_NAME = 'LifeHUD'


class Calendar(object):
    """ The Calendar class wraps the Google Calendar API and can return upcoming events. """
    credentials = None
    flow = None

    client_id = None
    client_secret = None
    accounts = []

    @staticmethod
    def initialize(config):
        Calendar.client_id = config['client_id']
        Calendar.client_secret = config['client_secret']
        Calendar.accounts = config['accounts']
        Calendar.start_auth()

    @staticmethod
    def start_auth():
        if Calendar.credentials is not None:
            return

        storage = Storage(CREDENTIALS_FILE)
        try:
            Calendar.credentials = storage.get()
            assert Calendar.credentials is not None and not Calendar.credentials.invalid
            return
        except Exception, e:
            pass

        Calendar.flow = client.OAuth2WebServerFlow(client_id=Calendar.client_id,
                                   client_secret=Calendar.client_secret,
                                   scope='https://www.googleapis.com/auth/calendar.readonly',
                                   redirect_uri='http://localhost:6543/oauthCallback')
        auth_uri = Calendar.flow.step1_get_authorize_url()
        webbrowser.open(auth_uri, 1)


    @staticmethod
    def get_all_events():
        result = []
        for account in Calendar.accounts:
            result.extend(Calendar.get_events(account))
        return result

    @staticmethod
    def get_events(calendar_id):
        http = Calendar.credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        one_week_ahead = (datetime.utcnow() + timedelta(weeks=1)).isoformat() + 'Z'
        eventsResult = service.events().list(
            calendarId=calendar_id, timeMin=now, timeMax=one_week_ahead, maxResults=10, singleEvents=True, orderBy='startTime'
        ).execute()
        events = eventsResult.get('items', [])

        if not events:
            return []
        result = []
        for e in events:
            if 'date' in e['start']:
                all_day = True
                start_date = datetime.strptime(e['start']['date'], '%Y-%m-%d')
                end_date = datetime.strptime(e['end']['date'], '%Y-%m-%d')
            else:
                all_day = False
                start_date = datetime.strptime(e['start']['dateTime'], '%Y-%m-%dT%H:%M:%S-08:00')
                end_date = datetime.strptime(e['end']['dateTime'], '%Y-%m-%dT%H:%M:%S-08:00')

            result.append({
                'calendar': calendar_id,
                'start': start_date,
                'end': end_date,
                'all_day': all_day,
                'title': e['summary'],
            })

        return result


@view_config(route_name='oauthCallback')
def oauth_callback(request):
    code = request.params['code']
    credentials = Calendar.flow.step2_exchange(code)
    storage = Storage(CREDENTIALS_FILE)
    storage.put(credentials)
    Calendar.credentials = credentials
    return Response(status=200, body='huzzah')
