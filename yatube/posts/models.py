from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
title_size: int = 15


class Post(CreatedModel):
    text = models.TextField(
        "Текст записи",
        help_text="Напишите текст поста"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="group",
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост"
    )
    image = models.ImageField(
        "Изображение",
        upload_to="posts/",
        blank=True,
        help_text="Можно добавить изображение",
    )

    class Meta:
        ordering = ["-pub_date", ]
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:title_size]


class Group(models.Model):
    title = models.CharField(
        "Название группы",
        max_length=200,
        help_text="Введите название группы"
    )
    slug = models.SlugField(
        "Уникальная ссылка",
        unique=True,
        help_text=(
            "Укажите уникальный адрес для страницы группы. Используйте только"
            "латиницу, цифры, дефисы и знаки подчёркивания"
        )
    )
    description = models.TextField(
        "Описание группы",
        help_text="Введите описание группы"
    )

    class Meta:
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария"
    )
    text = models.TextField(
        "Текст комментария",
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписчики"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            )
        ]
