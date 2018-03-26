from datetime import time, datetime, timedelta
from dateutil import tz
import heapq

from pyramid.view import view_config

from calendar import Calendar
from icloud import ICloud
from weather import Weather


@view_config(route_name='home', renderer='templates/hud.jinja2')
def my_view(request):
    """ This function handles incoming requests and comes up with the data that will be passed into our HTML template.
        This file is our entire "controller layer".
    """

    dates = [datetime.now().date() + timedelta(days=x) for x in range(0, 7)]
    events_by_date = {i: [] for i in dates}
    # events should have the properties start: datetime, end: datetime, owners: list of ints, title: string

    i = 0
    for reminder_list in ICloud.iterate_reminders():
        for reminder in find_scheduled_reminders(reminder_list):
            day = reminder['due'].date()
            if day in events_by_date:
                events_by_date[day].append({
                    'start': reminder['due'],
                    'owners': [i],
                    'title': reminder['title'],
                    'type': 'reminder',
                })
        i += 1

    weather_info = Weather.get_forecast()
    forecasts_by_date = {i: [] for i in dates}
    display_hours = [x for x in range(9, 22, 3)]
    for hour_info in weather_info.data:
        time = datetime.fromtimestamp(hour_info['time'], tz=tz.tzlocal())
        date = time.date()
        hour = time.hour
        if not hour in display_hours:
            continue
        forecasts_by_date[date].append({
            'time': time,
            'icon': hour_info['icon'],
            'summary': hour_info['summary'],
            'temperature': int(round(hour_info['temperature'], 0)),
            'feelsLike': int(round(hour_info['apparentTemperature'], 0)),
            'rainChance': int(hour_info['precipProbability'] * 100),
        })

    i = 0
    for event_list in Calendar.iterate_events():
        for event in event_list:
            day = event['start'].date()
            if day in events_by_date:
                # First check for duplicates
                existing_event = find_existing_event_in_list(event, events_by_date[day])
                if existing_event:
                    existing_event['owners'].append(i)
                else:
                    event['owners'] = [i]
                    event['type'] = "calendar"
                    events_by_date[day].append(event)
        i += 1

    viewmodel = {
        'days': [{
            'date': i,
            'events': sorted(events_by_date[i], key=lambda e: e['start']),
            'forecast': forecasts_by_date[i]
        } for i in dates]
    }

    return viewmodel

def find_existing_event_in_list(event, event_list):
    for event2 in event_list:
        if event['title'] == event2['title']\
            and event['start'] == event2['start']\
            and event['end'] == event2['end']:
            return event2

def find_scheduled_reminders(reminders):
    scheduled = []
    one_week_forward = datetime.now() + timedelta(weeks=1)
    for l in reminders.lists.values():
        for item in l:
            if item['due'] is not None and item['due'] < one_week_forward:
                heapq.heappush(scheduled, (item['due'], item))
    sorted_reminders = [heapq.heappop(scheduled)[1] for i in xrange(len(scheduled))]
    return [{
        'title': i['title'],
        'due': i['due'].replace(tzinfo=tz.tzlocal()),
    } for i in sorted_reminders]


def format_calendar_events(events):
    all_days = []
    this_day = []
    current_day = None
    for e in sorted(events, key=lambda x: x['start']):
        start_day = e['start'].strftime('%A')
        if start_day != current_day and current_day is not None:
            all_days.append(this_day)
            this_day = []
        current_day = start_day
        e['day'] = start_day
        if e['all_day']:
            e['start'] = ''
            e['end'] = e['end'].strftime('%A')
        else:
            e['start'] = e['start'].strftime('%I:%M %p')
            e['end'] = e['end'].strftime('%I:%M %p')
        this_day.append(e)
    all_days.append(this_day)
    return all_days
