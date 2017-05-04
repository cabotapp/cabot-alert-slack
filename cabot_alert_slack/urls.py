from django.conf.urls import include, url
from .views import slack_message_callback

urlpatterns = [
    url(r'^messages', slack_message_callback, name="slack-message-callback"),
]
