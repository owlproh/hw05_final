from http import HTTPStatus
from django.urls import reverse

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_creator = User.objects.create(username="user_cr")
        cls.user_uncreator = User.objects.create(username="user_un")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Текст описания тестовой группы"
        )
        cls.post = Post.objects.create(
            text="Текст тестового поста",
            author=cls.user_creator,
            group=cls.group
        )
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="guest")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_uncreator)
        self.post_creator = Client()
        self.post_creator.force_login(self.user_creator)
        cache.clear()

    def test_pages_for_all(self):
        """Страницы для всех"""
        cache.clear()
        pages_for_all = [
            "",
            f"/group/{self.group.slug}/",
            f"/profile/{self.post.author}/",
            f"/posts/{self.post.id}/",
        ]
        for page in pages_for_all:
            with self.subTest(page=page):
                self.assertEqual(
                    self.guest_client.get(page).status_code,
                    HTTPStatus.OK
                )
                self.assertEqual(
                    self.authorized_client.get(page).status_code,
                    HTTPStatus.OK
                )
                self.assertEqual(
                    self.post_creator.get(page).status_code,
                    HTTPStatus.OK
                )
        cache.clear()

    def test_pages_for_author(self):
        """Страницы для автора"""
        response = self.post_creator.get(f"/posts/{self.post.id}/edit/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        cache.clear()

    def test_pages_for_uncreator(self):
        """Страницы для авторизованного, но не автора"""
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        cache.clear()

    def test_page_not_exist(self):
        """Страницы, которых не предусмотрено"""
        response = self.guest_client.get("/owls/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        cache.clear()

    def test_templates_for_urls(self):
        """Корректность шаблонов"""
        templates_urls = {
            reverse("posts:index"): "posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.post.author}/": "posts/profile.html",
            f"/posts/{self.post.id}/": "posts/post_detail.html",
            f"/posts/{self.post.id}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }
        for url, template in templates_urls.items():
            with self.subTest(url=url):
                response = self.post_creator.get(url)
                self.assertTemplateUsed(response, template)
        cache.clear()

    def test_follow_index_page(self):
        """Страница подписок доступна автору."""
        response = self.post_creator.get(reverse("posts:follow_index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
