from django.test import TestCase
from http import HTTPStatus


class CoreViewTests(TestCase):
    def test_custom_404_page(self):
        """Если нет страницы, то используется кастомный шаблон 404"""
        response = self.client.get("/owls/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
