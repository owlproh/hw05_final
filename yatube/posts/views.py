from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

cnt_posts: int = 10
size_text: int = 30
cache_time: int = 20


def paginator(request, post_list, cnt_posts):
    paginator = Paginator(post_list, cnt_posts)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(cache_time, key_prefix="index_page")
def index(request):
    template = "posts/index.html"
    post_list = Post.objects.select_related("author", "group")
    page_obj = paginator(request, post_list, cnt_posts)
    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group.select_related("group")
    page_obj = paginator(request, post_list, cnt_posts)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = "posts/profile.html"
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related("author")
    count_posts = author.posts.count()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author
    )
    page_obj = paginator(request, post_list, cnt_posts)
    context = {
        "author": author,
        "count_posts": count_posts,
        "page_obj": page_obj,
        "following": following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    post = get_object_or_404(Post, pk=post_id)
    post_title = post.text[:size_text]
    author = post.author
    author_cnt_posts = author.posts.select_related("author").count()
    form = CommentForm(request.POST or None)
    comments = post.comments.select_related("author")
    context = {
        "post": post,
        "post_title": post_title,
        "author": author,
        "author_cnt_posts": author_cnt_posts,
        "comments": comments,
        "form": form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = "posts/create_post.html"
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(f"/profile/{post.author}/", {"form": form})
    form.errors
    return render(request, template, {"form": form})


@login_required
def post_edit(request, post_id):
    template_create = "posts/create_post.html"
    template_post = "posts:post_detail"
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    groups = Group.objects.all()
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user == author:
        if request.method == "POST" and form.is_valid:
            post = form.save()
            return redirect(template_post, post_id)
        context = {
            "form": form,
            "groups": groups,
            "post": post,
            "is_edit": is_edit,
        }
        return render(request, template_create, context)
    return redirect(template_post, post_id)


@login_required
def add_comment(request, post_id):
    template = "posts:post_detail"
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(template, post_id=post_id)


@login_required
def follow_index(request):
    template = "posts/follow.html"
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, post_list, cnt_posts)
    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    template = "posts:profile"
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(template, username=username)


@login_required
def profile_unfollow(request, username):
    template = "posts:profile"
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(template, username=username)
