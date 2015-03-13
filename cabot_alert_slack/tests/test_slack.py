from cabot.cabotapp.tests.tests_basic import LocalTestCase
from mock import Mock, patch

from cabot.cabotapp.models import UserProfile, Service
from cabot_alert_slack import models
from cabot.cabotapp.alert import update_alert_plugins

class TestSlackAlerts(LocalTestCase):
    def setUp(self):
        super(TestSlackAlerts, self).setUp()

        self.user_profile = UserProfile(user=self.user)
        self.user_profile.save()
        self.slack_user_data = models.SlackAlertUserData.objects.create(
            slack_alias = "test_user_slack_alias",
            user = self.user_profile,
            title=models.SlackAlertUserData.name,
            )
        self.slack_user_data.save()

        self.service.users_to_notify.add(self.user)

        update_alert_plugins()
        self.slack_plugin = models.SlackAlert.objects.get(title=models.SlackAlert.name)
        self.service.alerts.add(self.slack_plugin)
        self.service.save()
        self.service.update_status()

    def test_users_to_notify(self):
        self.assertEqual(self.service.users_to_notify.all().count(), 1)
        self.assertEqual(self.service.users_to_notify.get(pk=1).username, self.user.username)

    @patch('cabot_alert_slack.models.SlackAlert._send_slack_alert')
    def test_normal_alert(self, fake_slack_alert):
        self.service.overall_status = Service.PASSING_STATUS
        self.service.old_overall_status = Service.ERROR_STATUS
        self.service.save()
        self.service.alert()
        fake_slack_alert.assert_called_with(u'Service Service is back to normal: http://localhost/service/1/. @test_user_slack_alias', color='green', sender='Cabot/Service')

    @patch('cabot_alert_slack.models.SlackAlert._send_slack_alert')
    def test_failure_alert(self, fake_slack_alert):
        # Most recent failed
        self.service.overall_status = Service.CALCULATED_FAILING_STATUS
        self.service.old_overall_status = Service.PASSING_STATUS
        self.service.save()
        self.service.alert()
        fake_slack_alert.assert_called_with(u'Service Service reporting failing status: http://localhost/service/1/. Checks failing: @test_user_slack_alias', color='red', sender='Cabot/Service')
