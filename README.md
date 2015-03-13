Cabot Slack Plugin
=====

Based on: https://github.com/bonniejools/cabot-alert-hipchat

This is an alert plugin for the cabot service monitoring tool. It allows you to alert users by their user handle in a slack channel.

## Installation
Enter the cabot virtual environment.
```
    $ pip install cabot-alert-slack
    $ foreman stop
```
Edit conf/*.env.

```
SlACK_ALERT_CHANNEL=test
SlACK_WEBHOOK_URL=https://hooks.slack.com/services/10242TGDW/103VaVDPL/hp2jQB3m9Nqta98WE5gnNB0o
SLACK_ICON_URL=http://lorempixel.com/40/40/
```

Add cabot_alert_slack to the installed apps in settings.py
```
    $ foreman run python manage.py syncdb
    $ foreman start
```
