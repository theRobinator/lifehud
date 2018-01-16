# LifeHUD

LifeHUD is a heads-up display for me to look at every morning when I get up. It includes
integrations for my iCloud reminders, my Google calendar, and the current day's hourly
weather forecast via the [Dark Sky API](https://darksky.net/dev).

## Installation

1. You may want to set up a virtualenv before you start.
2. Copy `config.example.yaml` to `config.yaml` and fill out the fields with your keys.
3.
    ```
    pip install -r requirements.txt
    python setup.py develop
    ```

Now you can `pserve development.ini` and open up http://localhost:6543 to see the app.
