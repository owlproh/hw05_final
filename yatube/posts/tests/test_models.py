from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()
size_str: int = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост для проверки",
        )

    def test_PostModel_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        object_name = post.text[:size_str]
        self.assertEqual(object_name, self.post.text[:size_str])

    def test_PostModel_verbose_name(self):
        """"Проверяем наличие verbose_name"""
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст записи",
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_PostModel_help_text(self):
        """"Проверяем help_text"""
        post = PostModelTest.post
        field_help_texts = {
            "text": "Напишите текст поста",
            "group": "Группа, к которой будет относиться пост",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_GroupModel_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = GroupModelTest.group
        object_name = group.title
        self.assertEqual(object_name, str(group))


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_creator = User.objects.create(username="user_cr")
        cls.post = Post.objects.create(
            text="Текст тестового поста",
            author=cls.user_creator,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_creator,
            text="Текст тестового комментария к посту",
        )

    def test_CommentModel_object_name(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        object_name = self.comment.text
        self.assertEqual(object_name, str(self.comment.text))

    def test_CommentModel_verbose_name(self):
        """Проверяем наличие verbose_name"""
        comment = CommentModelTest.comment
        verboses = {
            "text": "Текст комментария",
            "author": "Автор комментария",
            "post": "Пост",
        }
        for field, expected_value in verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name, expected_value
                )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.following = User.objects.create(
            username="following_man")
        cls.follower = User.objects.create(
            username="follower_man")
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.following
        )

    def test_FollowModel(self):
        """Проверяем модель подписок."""
        follow = FollowModelTest.follow
        author = follow.author
        follower = follow.user
        self.assertEqual(author, self.following)
        self.assertEqual(follower, self.follower)
