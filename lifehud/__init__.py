from pyramid.config import Configurator
import yaml

from calendar import Calendar
from icloud import ICloud
from weather import Weather


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with open('config.yaml', 'r') as fp:
        local_config = yaml.safe_load(fp)['config']
    Calendar.initialize(local_config['calendar'])
    ICloud.initialize(local_config['icloud'])
    Weather.initialize(local_config['weather'])

    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('oauthCallback', '/oauthCallback')
    config.scan()
    return config.make_wsgi_app()
