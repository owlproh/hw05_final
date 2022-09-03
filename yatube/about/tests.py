from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class AboutUrlTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="guest")

    def test_about_pages(self):
        """Страницы для всех"""
        about_pages = [
            "/about/author/",
            "/about/tech/"
        ]
        for page in about_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)
