from django.db import models
from cabot.cabotapp.alert import AlertPlugin, AlertPluginUserData

from os import environ as env

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Context, Template

import requests
import json

slack_template = """
Service {{ service.name }} {% if service.overall_status == service.PASSING_STATUS %}*is back to normal*{% else %}reporting *{{ service.overall_status }}* status{% endif %}: {{ scheme }}://{{ host }}{% url 'service' pk=service.id %} \
{% if alert %}{% for alias in users %} @{{ alias }}{% endfor %}{% endif %}\

{% if service.overall_status != service.PASSING_STATUS %}Checks failing:\
{% for check in service.all_failing_checks %}\
    {% if check.check_category == 'Jenkins check' %}\
        {% if check.last_result.error %}\
            - {{ check.name }} ({{ check.last_result.error|safe }}) {{check.jenkins_config.jenkins_api}}job/{{ check.name }}/{{ check.last_result.job_number }}/console
        {% else %}\
            - {{ check.name }} {{check.jenkins_config.jenkins_api}}/job/{{ check.name }}/{{check.last_result.job_number}}/console
        {% endif %}\
    {% else %}
        - {{ check.name }} {% if check.last_result.error %} ({{ check.last_result.error|safe }}){% endif %}
    {% endif %}\
{% endfor %}\
{% endif %}\
"""

# This provides the slack alias for each user. Each object corresponds to a User
class SlackAlert(AlertPlugin):
    name = "Slack"
    author = "Luka Blaskovic"

    def send_alert(self, service, users, duty_officers):
        alert = True
        slack_aliases = []
        users = list(users) + list(duty_officers)

        slack_aliases = [u.slack_alias for u in SlackAlertUserData.objects.filter(user__user__in=users)]

        if service.overall_status == service.WARNING_STATUS:
            alert = False  # Don't alert at all for WARNING
        if service.overall_status == service.ERROR_STATUS:
            if service.old_overall_status in (service.ERROR_STATUS, service.ERROR_STATUS):
                alert = False  # Don't alert repeatedly for ERROR
        if service.overall_status == service.PASSING_STATUS:
            color = 'good'
            if service.old_overall_status == service.WARNING_STATUS:
                alert = False  # Don't alert for recovery from WARNING status
        else:
            color = 'danger'

        c = Context({
            'service': service,
            'users': slack_aliases,
            'host': settings.WWW_HTTP_HOST,
            'scheme': settings.WWW_SCHEME,
            'alert': alert,
        })
        message = Template(slack_template).render(c)
        self._send_slack_alert(message, service, color=color, sender='Cabot')

    def _send_slack_alert(self, message, service, color='good', sender='Cabot'):

        channel = '#' + env.get('SLACK_ALERT_CHANNEL')
        url = env.get('SLACK_WEBHOOK_URL')
        icon_url = env.get('SLACK_ICON_URL')

        actions = []
        if env.get('SLACK_INTERACTIVE_MESSAGES', False) and service.overall_status != service.PASSING_STATUS:
            actions.append({
                "name": "acknowledge",
                "text": "Acknowledge",
                "type": "button",
                "value": "acknowledge",
            })

        # TODO: handle color
        resp = requests.post(url, data=json.dumps({
            'channel': channel,
            'username': sender[:15],
            'icon_url': icon_url,
            'link_names': 1,
            'attachments': [{
                'title': service.name,
                'text': message,
                'color': color,
                'mrkdwn_in': ["text"],
                'fields': [{
                    'title': 'status',
                    'value': service.overall_status,
                    'short': True
                    }, {
                    'title': 'old status',
                    'value': service.old_overall_status,
                    'short': True
                    }
                ],
                'callback_id': "acknowledge_{}".format(service.id),
                'actions': actions
            }]
        }))

class SlackAlertUserData(AlertPluginUserData):
    name = "Slack Plugin"
    slack_alias = models.CharField(max_length=50, blank=True)

