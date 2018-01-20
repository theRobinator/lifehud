from getpass import getpass

from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudAPIResponseError


class ICloud(object):
    """ The ICloud class wraps the iCloud API, and can return just about anything related to an iCloud account. """
    connected_accounts = {}
    account_passwords = {}

    @staticmethod
    def initialize(config):
        for i in config['users']:
            password = getpass('Enter the iCloud password for %s: ' % i)
            ICloud.add_account(i, password)


    @staticmethod
    def add_account(username, password):
        ICloud.account_passwords[username] = password
        api = PyiCloudService(username, password)
        ICloud.connected_accounts[username] = api
        return api

    @staticmethod
    def get_reminders(username):
        try:
            return ICloud.connected_accounts[username].reminders
        except PyiCloudAPIResponseError, e:
            ICloud.add_account(username, ICloud.account_passwords[username])
            return ICloud.connected_accounts[username].reminders
