from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group", "image"]
        help_texts = {
            "text": "Введите текст поста",
            "group": "Выберите группу, к которой отнести пост",
            "image": "Выберите изображение для поста",
        }
        labels = {
            "text": "Текст записи",
            "group": "Сообщество",
            "image": "Пикча:)",
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {"text": "Текст комментария"}
