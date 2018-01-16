from datetime import datetime, timedelta
import heapq

from pyramid.view import view_config

from calendar import Calendar
from icloud import ICloud
from weather import Weather


WEATHER_HOURS_AHEAD = 12


@view_config(route_name='home', renderer='templates/hud.jinja2')
def my_view(request):
    """ This function handles incoming requests and comes up with the data that will be passed into our HTML template.
        This file is our entire "controller layer".
    """

    accounts = []
    for email, cloud_api in ICloud.connected_accounts.iteritems():
        accounts.append({
            'name': cloud_api.data['dsInfo']['firstName'],
            'reminders': find_scheduled_reminders(ICloud.get_reminders(email)),
        })

    weather_info = Weather.get_forecast()
    forecast = []
    for hour_info in weather_info.data:
        hour_time = datetime.fromtimestamp(hour_info['time'])
        if hour_time < datetime.now():
            continue
        forecast.append({
            'time': hour_time.strftime('%a %I:%M %p'),  # Mon 12:00 PM
            'icon': hour_info['icon'],
            'summary': hour_info['summary'],
            'temperature': int(round(hour_info['temperature'], 0)),
            'feelsLike': int(round(hour_info['apparentTemperature'], 0)),
            'rainChance': int(hour_info['precipProbability'] * 100),
        })
        if len(forecast) == WEATHER_HOURS_AHEAD:
            break

    calendar_events = Calendar.get_events('robinthekeller@gmail.com')
    calendar_events.extend(Calendar.get_events('rose.abernathy@gmail.com'))
    calendar_events = Calendar.get_all_events()
    full_calendar = format_calendar_events(calendar_events)

    viewmodel = {
        'accounts': accounts,
        'calendar': full_calendar,
        'forecast': forecast,
    }

    return viewmodel


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
        'due': i['due'].strftime('%A %I:%M %p'),
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
