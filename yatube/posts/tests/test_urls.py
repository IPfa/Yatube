from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

HOME_PAGE_URL = '/'
GROUP_PAGE_URL = '/group/'
NEW_POST_PAGE_URL = '/new/'
PAGE_NOT_EXIST = '/group/hello/'
HOME_PAGE_NAME = 'posts:index'
GROUP_PAGE_NAME = 'posts:group'
NEW_POST_NAME = 'posts:new_post'
LOGIN_PAGE_NAME = 'login'
PROFILE_PAGE_NAME = 'posts:profile'
POST_PAGE_NAME = 'posts:post'
POST_EDIT_PAGE_NAME = 'posts:edit_post'


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        cache.clear()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):

    USERNAME = 'split'
    USERNAME2 = 'zadar'
    GROUP_TITLE = 'Дубровник'
    GROUP_SLUG = 'dubrovnik'
    POST_TEXT = 'For post id'

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username=self.USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user2 = User.objects.create_user(username=self.USERNAME2)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        self.group = Group.objects.create(
            title=self.GROUP_TITLE,
            slug=self.GROUP_SLUG
        )
        self.templates_url_names = {
            'posts/index.html': '/',
            'posts/group.html': f'/group/{self.group.slug}/',
            'posts/new_post.html': '/new/',
        }
        self.post = Post.objects.create(
            author=self.user,
            text=self.POST_TEXT,
            group=self.group
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_not_available_for_not_post_author(self):
        """Страница /<username>/<post_id>/edit/ не доступна не автору поста."""
        response = self.authorized_client2.get(
            f'/{self.post.author}/{self.post.pk}/edit/'
        )
        self.assertNotEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse(
                POST_PAGE_NAME,
                kwargs={'username': self.post.author, 'post_id': self.post.pk}
            )
        )

    def test_username_post_id_edit_url_uses_correct_template(self):
        """Страница /<username>/<post_id>/edit/ использует."""
        """Соответствующий шаблон."""
        response = self.authorized_client.get(
            f'/{self.post.author}/{self.post.pk}/edit/'
        )
        self.assertTemplateUsed(response, 'posts/new_post.html')

    def test_permissions(self):
        """Тест проверки "разрешенных" url."""
        """Для авторизованных/неавторизованных юзеров."""
        test_urls = (
            (HOME_PAGE_URL, self.guest_client),
            (NEW_POST_PAGE_URL, self.authorized_client),
            (f'{GROUP_PAGE_URL}{self.group.slug}/', self.guest_client),
            (f'/{self.post.author}/', self.guest_client),
            (f'/{self.post.author}/{self.post.pk}/', self.guest_client),
            (
                f'/{self.post.author}/{self.post.pk}/edit/',
                self.authorized_client
            ),
        )
        for adress, client in test_urls:
            with self.subTest(adress=adress):
                response = client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects(self):
        """Проверка всех возможных редиректов для GET-запросов."""
        """Авторизованных пользователей"""
        test_redirects = (
            (
                f'/{self.post.author}/{self.post.pk}/edit/',
                self.authorized_client2,
                POST_PAGE_NAME,
                [self.post.author, self.post.pk],
            ),
        )
        for adress, client, url, parameters in test_redirects:
            with self.subTest(adress=adress):
                response = client.get(adress)
                self.assertRedirects(response, reverse(url, args=parameters))

    def test_view_functions_names(self):
        """Проверка соответствия прямых ссылок."""
        """И полученных через reverse(name)"""
        test_names = (
            (HOME_PAGE_URL, HOME_PAGE_NAME, None),
            (NEW_POST_PAGE_URL, NEW_POST_NAME, None),
            (
                f'/{self.post.author}/',
                PROFILE_PAGE_NAME,
                [self.post.author]
            ),
            (
                f'{GROUP_PAGE_URL}{self.group.slug}/',
                GROUP_PAGE_NAME,
                [self.group.slug]
            ),
            (
                f'/{self.post.author}/{self.post.pk}/',
                POST_PAGE_NAME,
                [self.post.author, self.post.pk]
            ),
            (
                f'/{self.post.author}/{self.post.pk}/edit/',
                POST_EDIT_PAGE_NAME,
                [self.post.author, self.post.pk]
            )
        )
        for adress, name, parameters in test_names:
            with self.subTest(adress=adress):
                self.assertEqual(adress, reverse(name, args=parameters))

    def test_server_returns_404(self):
        """Сервер возвращает 404, если страница не найдена."""
        response = self.guest_client.get(PAGE_NOT_EXIST)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_only_auth_user_could_add_comment(self):
        """Только авторизованный пользователь может комментировать записи."""
        response = self.guest_client.get(
            f'/{self.post.author}/{self.post.pk}/comment/'
        )
        self.assertRedirects(
            response,
            reverse(LOGIN_PAGE_NAME)
            + f'?next=/{self.post.author}/{self.post.pk}/comment/'
        )
