from django.contrib.auth import models
from django.test import TestCase
from django.urls import reverse


class Test(TestCase):
    def test_admin_action(self):
        guest_user = models.User.objects.filter(username='guest').first()
        self.client.login(username='admin', password='admin')
        user_cl = reverse('admin:auth_user_changelist')
        r = self.client.get(user_cl)
        self.assertRegex(r.content, rb'Welcome,\s+<strong>admin</strong>')
        r = self.client.post(
            user_cl,
            {
                'action': 'impersonate_action',
                '_selected_action': [guest_user.pk],
            },
        )
        # 404 as it is not available during testing
        self.assertRedirects(r, '/', status_code=302, target_status_code=404)
        r = self.client.get(reverse('admin:index'))
        self.assertRegex(r.content, rb'Welcome,\s+<strong>guest</strong>')
