from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Convention, Panel, ConventionDay, Room
from datetime import date, time

class ConventionModelTest(TestCase):
    def test_single_convention_enforced(self):
        Convention.objects.create(name='Test Con', start_date=date(2026, 4, 3), end_date=date(2026, 4, 4))
        second = Convention(name='Second Con', start_date=date(2026, 5, 1), end_date=date(2026, 5, 2))
        with self.assertRaises(Exception):
            second.full_clean()

class PanelToggleCancelledTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='staff', password='pass', is_staff=True)
        self.client = Client()
        self.client.login(username='staff', password='pass')
        self.convention = Convention.objects.create(name='Test Con', start_date=date(2026, 4, 3), end_date=date(2026, 4, 4))
        self.day = ConventionDay.objects.create(convention=self.convention, date=date(2026, 4, 3))
        self.room = Room.objects.create(name='Room 1', convention=self.convention)
        self.panel = Panel.objects.create(title='Panel 1', description='Desc', convention_day=self.day, start_time=time(9,0), end_time=time(10,0), room=self.room)

    def test_toggle_cancelled(self):
        url = reverse('events:toggle_cancelled', args=[self.panel.pk])
        response = self.client.post(url, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(Panel.objects.get(pk=self.panel.pk).cancelled)
