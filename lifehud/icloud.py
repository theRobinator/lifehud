from getpass import getpass

from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudAPIResponseError


class ICloud(object):
    """ The ICloud class wraps the iCloud API, and can return just about anything related to an iCloud account. """
    account_names = []
    connected_accounts = {}
    account_passwords = {}

    @staticmethod
    def initialize(config):
        for i in config['users']:
            password = getpass('Enter the iCloud password for %s: ' % i)
            ICloud.add_account(i, password)


    @staticmethod
    def add_account(username, password):
        ICloud.account_names.append(username)
        ICloud.account_passwords[username] = password
        api = PyiCloudService(username, password)
        ICloud.connected_accounts[username] = api
        if api.requires_2fa:
            import click
            print "Two-step authentication required for %s. Your trusted devices are:" % username
            devices = api.trusted_devices
            for i, device in enumerate(devices):
                print "  %s: %s" % (i, device.get('deviceName',
                                                  "SMS to %s" % device.get('phoneNumber')))

            device = click.prompt('Which device would you like to use?', default=0)
            device = devices[device]
            if not api.send_verification_code(device):
                print "Failed to send verification code"
                exit(1)

            code = click.prompt('Please enter validation code')
            if not api.validate_verification_code(device, code):
                print "Failed to verify verification code"
                exit(1)
        return api

    @staticmethod
    def get_reminders(username):
        try:
            return ICloud.connected_accounts[username].reminders
        except PyiCloudAPIResponseError, e:
            ICloud.add_account(username, ICloud.account_passwords[username])
            return ICloud.connected_accounts[username].reminders

    @staticmethod
    def iterate_reminders():
        for username in ICloud.account_names:
            yield ICloud.get_reminders(username)

