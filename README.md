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

or

```
    $ pip install git+git://github.com/lblasc/cabot-alert-slack.git
    $ foreman stop
```

Edit `conf/*.env`.

```
CABOT_PLUGINS_ENABLED=cabot_alert_slack==0.5
...
SLACK_ALERT_CHANNEL=channel_name_without_hash
SLACK_WEBHOOK_URL=url_of_your_webhook_integration_from_slack
SLACK_ICON_URL=http://lorempixel.com/40/40/
```

Add cabot_alert_slack to the installed apps in settings.py
```
    $ foreman run python manage.py syncdb
    $ foreman start
```
