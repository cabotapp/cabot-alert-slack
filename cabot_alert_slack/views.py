from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import SlackAlertUserData

from cabot.cabotapp.models import Service
import json
import re


@csrf_exempt
def slack_message_callback(request):
    payload = json.loads(request.POST['payload'])
    service_id = re.match('acknowledge_(\d+)', payload['callback_id']).groups()[0]

    slack_alias = payload['user']['name']
    # .user.user to go through user_profile -> user...
    user = SlackAlertUserData.objects.get(slack_alias=slack_alias).user.user

    service = Service.objects.get(pk=service_id)
    service.acknowledge_alert(user)

    message = payload['original_message']
    # Strip out button
    for attach in message['attachments']:
        if int(attach['id']) != int(payload['attachment_id']):
            continue
        attach['actions'] = []

    message['attachments'].append({
        'text': 'Acknowledged by @{}'.format(slack_alias),
        'color': 'warning',
    })

    return JsonResponse(message)
