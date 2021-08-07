from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/group.html',
                  {'group': group, 'page': page})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(author=user)
    following = Follow.objects.filter(user=user)
    posts = Post.objects.filter(author=user)
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        follow_bool = False
        if Follow.objects.filter(user=request.user, author=user):
            follow_bool = True
    else:
        follow_bool = False
    context = {
        'profile_user': user,
        'posts': posts,
        'page': page,
        'followers': followers,
        'following': following,
        'follow_bool': follow_bool,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    post = Post.objects.get(author=user, pk=post_id)
    comments = Comment.objects.filter(post=post_id)
    form = CommentForm()
    context = {
        'profile_user': user,
        'posts': posts,
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:index')
    title_header = 'Добавить запись'
    button = 'Добавить'
    context = {
        'form': form,
        'title_header': title_header,
        'button': button
    }
    return render(request, 'posts/new_post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = Post.objects.get(pk=post_id)
    title_header = 'Редактировать запись'
    button = 'Сохранить'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post.text = form.cleaned_data['text']
        post.group = form.cleaned_data['group']
        post.image = form.cleaned_data['image']
        post.save()
        return redirect('posts:post', username=username, post_id=post_id)
    if request.user == post.author:
        form = PostForm(instance=post)
        context = {
            'form': form,
            'title_header': title_header,
            'button': button,
            'post': post
        }
        return render(request, 'posts/new_post.html', context)
    else:
        return redirect('posts:post', username=username, post_id=post_id)


@login_required
def add_comment(request, post_id, username):
    post_add_comment = get_object_or_404(Post, pk=post_id)
    user_who_adds_comment = User.objects.get(username=username)
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Comment.objects.create(
            post=post_add_comment,
            author=user_who_adds_comment,
            text=form.cleaned_data['text']
        )
        return redirect(
            'posts:post',
            username=post_add_comment.author,
            post_id=post_id
        )
    context = {
        'form': form,
        'post': post_add_comment,
    }
    return render(request, 'posts/comments.html', context)


@login_required
def follow_index(request):
    user_follows = Follow.objects.filter(user=request.user)
    post_list = []
    for model_object in user_follows:
        following_posts = list(Post.objects.filter(author=model_object.author))
        for post in following_posts:
            post_list.append(post)
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    profile = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=profile):
        return redirect('posts:profile', username=profile)
    elif request.user == profile:
        return redirect('posts:profile', username=profile)
    else:
        Follow.objects.create(user=request.user, author=profile)
        return redirect('posts:profile', username=profile)


@login_required
def profile_unfollow(request, username):
    profile = get_object_or_404(User, username=username)
    follow_object = Follow.objects.get(user=request.user, author=profile)
    follow_object.delete()
    return redirect('posts:profile', username=profile)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
