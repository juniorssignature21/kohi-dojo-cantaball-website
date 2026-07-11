from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import LeagueWeek, Payment, Registration, Season, Team


User = get_user_model()


class HomeViewTests(TestCase):
    def test_home_view_exposes_weekly_registration_context(self):
        season = Season.objects.create(
            name="Season 2025",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            is_active=True,
        )
        week = LeagueWeek.objects.create(
            season=season,
            week_number=5,
            registration_open=timezone.now() - timedelta(days=1),
            registration_close=timezone.now() + timedelta(days=3),
            max_teams=20,
            status="OPEN",
        )
        user = User.objects.create_user(username="captain", email="captain@example.com", password="password123")
        team = Team.objects.create(user=user, team_name="Thunder")
        registration = Registration.objects.create(week=week, team=team, status="CONFIRMED")
        Payment.objects.create(
            team=team,
            registration=registration,
            amount=Decimal("5000"),
            reference="ref-001",
            gateway="Flutterwave",
            status="SUCCESS",
        )

        response = self.client.get(reverse("app:home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_week"], week)
        self.assertEqual(response.context["registered_count"], 1)
        self.assertEqual(response.context["remaining_slots"], 19)
        self.assertEqual(response.context["registration_progress"], 5)
