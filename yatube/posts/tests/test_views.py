import shutil
import tempfile
from datetime import date

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, Follow

User = get_user_model()
count_test_post: int = 15
cnt_posts: int = 10

test_img = (
    b"\x47\x49\x46\x38\x39\x61\x02\x00"
    b"\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
    b"\x00\x00\x00\x2C\x00\x00\x00\x00"
    b"\x02\x00\x01\x00\x00\x02\x02\x0C"
    b"\x0A\x00\x3B"
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTests(TestCase):
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
        tst_img = SimpleUploadedFile(
            name="test_img.gif",
            content=test_img,
            content_type="image/gif"
        )
        cls.post = Post.objects.create(
            text="Текст тестового поста",
            author=cls.user_creator,
            group=cls.group,
            pub_date=date.today(),
            image=tst_img
        )
        cls.form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField
        }
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_creator,
            text="Текст тестового комментария к посту",
        )
        cls.posts = cls.post.author.posts.select_related("author")
        cls.cnt_posts = cls.post.author.posts.count()
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="guest")
        self.post_creator = Client()
        self.post_creator.force_login(self.user_creator)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_uncreator)
        cache.clear()

    def checking_correct_post(self, post):
        self.assertEqual(self.post.author, post.author)
        self.assertEqual(self.post.text, post.text)
        self.assertEqual(self.post.group, post.group)
        self.assertEqual(self.post.pub_date, post.pub_date)
        self.assertEqual(self.post.image, post.image)
        cache.clear()

    def checking_correct_group(self, group):
        self.assertEqual(self.group.title, group.title)
        self.assertEqual(self.group.slug, group.slug)
        self.assertEqual(self.group.description, group.description)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            reverse(
                "posts:index"
            ): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": self.post.author}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.pk}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_create"
            ): "posts/create_post.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.pk}
            ): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.post_creator.get(reverse_name)
                self.assertTemplateUsed(response, template)
                if reverse_name == reverse(
                    "posts:post_edit", kwargs={"post_id": self.post.pk}
                ):
                    self.assertRedirects(
                        self.guest_client.get(reverse_name),
                        "/auth/login/?next=%2Fposts%2F1%2Fedit%2F"
                    )
                elif reverse_name == reverse(
                    "posts:post_create",
                ):
                    self.assertRedirects(
                        self.guest_client.get(reverse_name),
                        "/auth/login/?next=%2Fcreate%2F"
                    )
                else:
                    cache.clear()
                    self.assertTemplateUsed(
                        self.guest_client.get(reverse_name),
                        template
                    )

    def test_index_show_correct_context(self):
        """Cписок всех постов"""
        cache.clear()
        response = self.authorized_client.get(reverse("posts:index"))
        self.checking_correct_post(response.context["page_obj"][0])
        cache.clear()

    def test_grouplist_show_correct_context(self):
        """Список постов отфильтрованный по группе"""
        response = self.authorized_client.get(reverse(
            "posts:group_list", kwargs={"slug": self.group.slug}
        ))
        self.checking_correct_group(response.context.get("group"))
        self.checking_correct_post(response.context["page_obj"][0])
        cache.clear()

    def test_profile_show_correct_context(self):
        """Список постов отфильтрованный по пользователю"""
        response = self.authorized_client.get(reverse(
            "posts:profile", kwargs={"username": self.post.author}
        ))
        self.checking_correct_post(
            response.context["page_obj"][0]
        )
        self.assertEqual(
            response.context.get("count_posts"),
            self.cnt_posts
        )
        self.assertEqual(
            response.context.get("author"),
            self.post.author
        )
        cache.clear()

    def test_postdetail_show_correct_context(self):
        """Один пост, отфильтрованный по id"""
        size_text: int = 30
        response = self.authorized_client.get(reverse(
            "posts:post_detail", kwargs={"post_id": self.post.pk}
        ))
        self.checking_correct_post(response.context.get("post"))
        self.assertEqual(
            response.context.get("post_title"),
            self.post.text[:size_text]
        )
        self.assertEqual(
            response.context.get("author"),
            self.post.author
        )
        self.assertEqual(
            response.context.get("author_cnt_posts"),
            self.cnt_posts
        )
        cache.clear()

    def test_editpost_show_correct_context(self):
        """Форма редактирования поста, отфильтрованного по id"""
        response = self.post_creator.get(reverse(
            "posts:post_edit", kwargs={"post_id": self.post.pk}
        ))
        is_edit = response.context["is_edit"]
        self.assertTrue(is_edit)
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)
        cache.clear()

    def test_addpost_show_correct_context(self):
        """Форма создания поста"""
        response = self.authorized_client.get(reverse(
            "posts:post_create"
        ))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)
        cache.clear()

    def test_correctly_added_post(self):
        """Пост корректно добавился на главную, в группу, в профиль"""
        cache.clear()
        response_index = self.authorized_client.get(reverse(
            "posts:index"
        ))
        response_group = self.authorized_client.get(reverse(
            "posts:group_list", kwargs={"slug": f'{self.group.slug}'}
        ))
        response_profile = self.authorized_client.get(reverse(
            "posts:profile", kwargs={"username": f'{self.post.author}'}
        ))
        index = response_index.context["page_obj"]
        group = response_group.context["page_obj"]
        profile = response_profile.context["page_obj"]
        self.assertIn(self.post, index, "На главную пост не добавился")
        self.assertIn(self.post, group, "В группу пост не добавился")
        self.assertIn(self.post, profile, "В профиль пост не добавился")
        cache.clear()

    def test_cache_index(self):
        """Проверка кэширования главной страницы"""
        post_cnt = Post.objects.count()
        response = self.authorized_client.get("/")
        content_before = response.content
        Post.objects.get().delete()
        self.assertEqual(Post.objects.count(), post_cnt - 1)
        content_after = response.content
        self.assertEqual(content_before, content_after)
        cache.clear()
        after_clear = self.authorized_client.get("/")
        self.assertNotEqual(content_before, after_clear)
        cache.clear()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Текст описания тестовой группы"
        )
        cls.some_posts = [
            Post(
                author=cls.user_auth,
                text=f"Тестовый пост{i}",
                group=cls.group
            )
            for i in range(count_test_post)
        ]
        Post.objects.bulk_create(cls.some_posts)
        cls.pages: tuple = (
            reverse("posts:index"),
            reverse("posts:profile",
                    kwargs={"username": f"{cls.user_auth.username}"}),
            reverse("posts:group_list",
                    kwargs={"slug": f"{cls.group.slug}"}))

    def setUp(self):
        self.not_authorized = Client()
        self.authorized = Client()
        self.authorized.force_login(self.user_auth)
        cache.clear()

    def test_correct_page_context_guest_client(self):
        """Проверка количества постов на страницах для гостя."""
        cache.clear()
        for page in self.pages:
            response_1page = self.not_authorized.get(page)
            response_2page = self.not_authorized.get(page + "?page=2")
            self.assertEqual(
                len(response_1page.context.get("page_obj")),
                cnt_posts
            )
            self.assertEqual(
                len(response_2page.context.get("page_obj")),
                count_test_post - cnt_posts
            )
        cache.clear()

    def test_correct_page_context_auth_client(self):
        """Проверка количества постов на страницах для авторизованного."""
        cache.clear()
        for page in self.pages:
            response_1page = self.authorized.get(page)
            response_2page = self.authorized.get(page + "?page=2")
            self.assertEqual(
                len(response_1page.context.get("page_obj")),
                cnt_posts
            )
            self.assertEqual(
                len(response_2page.context.get("page_obj")),
                count_test_post - cnt_posts
            )
        cache.clear()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create(
            username="follower_man")
        cls.following = User.objects.create(
            username="following_man")
        cls.follower_post = Post.objects.create(
            text="Текст тестового поста follower",
            author=cls.follower,
        )
        cls.following_post = Post.objects.create(
            text="Текст тестового поста following",
            author=cls.following,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)
        self.authorized_following = Client()
        self.authorized_following.force_login(self.following)

    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь может подписываться."""
        follow_count = Follow.objects.count()
        response_follow = self.authorized_follower.get(reverse(
            "posts:profile_follow",
            kwargs={"username": self.following}
        ))
        self.assertRedirects(
            response_follow,
            reverse("posts:profile",
                    kwargs={"username": self.following}
                    )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower,
                author=self.following
            ).exists()
        )

    def test_authorized_user_can_unfollow(self):
        """Авторизованный пользователь может отписываться."""
        Follow.objects.create(user=self.follower, author=self.following)
        follow_count = Follow.objects.count()
        response_unfollow = self.authorized_follower.get(reverse(
            "posts:profile_unfollow",
            kwargs={"username": self.following}
        ))
        self.assertRedirects(
            response_unfollow,
            reverse("posts:profile",
                    kwargs={"username": self.following}
                    )
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower,
                author=self.following
            ).exists()
        )

    def test_follower_get_follow_index(self):
        """Новая запись пользователя появляется в ленте у подписчика."""
        Follow.objects.create(user=self.follower, author=self.following)
        response_follower = self.authorized_follower.get(
            reverse("posts:follow_index"))
        first_post = response_follower.context["page_obj"][0]
        self.assertEqual(first_post.text, self.following_post.text)
        self.assertEqual(first_post.author, self.following)

    def test_unfollower_dont_get_follow_index(self):
        """Новая запись пользователя не появляется в ленте у не подписчиков"""
        response_following = self.authorized_following.get(reverse(
            "posts:follow_index"))
        self.assertEqual(
            response_following.context['page_obj'].paginator.count, 0)
