import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User

HOME_PAGE_URL = 'posts:index'
NEW_POST_PAGE_URL = 'posts:new_post'
GROUP_PAGE_URL = 'posts:group'
PROFILE_PAGE_URL = 'posts:profile'
FOLLOW_PAGE_URL = 'posts:follow_index'
PROFILE_FOLLOW_PAGE_URL = 'posts:profile_follow'
PROFILE_UNFOLLOW_PAGE = 'posts:profile_unfollow'


@override_settings(MEDIA_ROOT=(settings.BASE_DIR + '/media'))
class PostsPagesTests(TestCase):

    USERNAME = 'split'
    USERNAME2 = 'hannover'
    USERNAME3 = 'berlin'
    GROUP_TITLE = 'Дубровник'
    GROUP_SLUG = 'dubrovnik'
    GROUP_HR_TITLE = 'Хорватия'
    GROUP_HR_SLUG = 'croatia'
    POST_TEXT = 'Assignment Test'
    POSTS_TEXT = 'Hello World!'
    CACHE_TEST_POST = 'Тест Кеша'
    SUBSCRIPTION_POST_TEXT = 'Подписан!'
    IMAGE = (
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.uploaded_image = SimpleUploadedFile(
            name='image',
            content=self.IMAGE,
            content_type='image/gif'
        )
        self.client = Client()
        self.user = User.objects.create_user(username=self.USERNAME)
        self.user2 = User.objects.create_user(username=self.USERNAME2)
        self.user3 = User.objects.create_user(username=self.USERNAME3)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(self.user3)
        self.group = Group.objects.create(
            title=self.GROUP_TITLE,
            slug=self.GROUP_SLUG
        )
        self.group_hr = Group.objects.create(
            title=self.GROUP_HR_TITLE,
            slug=self.GROUP_HR_SLUG
        )
        self.templates_pages_names = {
            'posts/index.html': reverse(HOME_PAGE_URL),
            'posts/new_post.html': reverse(NEW_POST_PAGE_URL),
            'posts/group.html': reverse(
                GROUP_PAGE_URL,
                kwargs={'slug': self.GROUP_SLUG}
            )
        }
        self.post_at = Post.objects.create(
            author=self.user,
            text=self.POST_TEXT,
            group=self.group,
            image=self.uploaded_image
        )  # assignment test
        self.objs = []
        for self.post in range(0, 11):
            self.post = self.objs.append(
                Post(
                    author=self.user,
                    text=self.POSTS_TEXT,
                    group=self.group,
                    image=self.uploaded_image
                )
            )
        self.follow = Follow.objects.create(user=self.user, author=self.user2)
        self.bulk = Post.objects.bulk_create(self.objs)
        self.post_edit_page_url = 'posts:edit_post'
        self.post_page_url = 'posts:post'

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator(self):
        """Проверка паджинатора на разных страницах"""
        pages = (
            (HOME_PAGE_URL, None),
            (GROUP_PAGE_URL, [self.GROUP_SLUG]),
            (PROFILE_PAGE_URL, [self.USERNAME])
        )
        for url, parameters in pages:
            with self.subTest(adress=url):
                response_first_page = self.client.get(
                    reverse(url, args=parameters)
                )
                response_second_page = self.client.get(
                    reverse(url, args=parameters)
                    + '?page=2'
                )
                self.assertEqual(
                    len(response_first_page.context['page'].object_list),
                    10
                )
                self.assertEqual(
                    len(response_second_page.context['page'].object_list),
                    2
                )

    def test_home_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(HOME_PAGE_URL))
        self.assertEqual(
            response.context['page'].object_list[0].text,
            'Hello World!'
        )
        self.assertEqual(
            response.context['page'].object_list[0].author,
            self.user
        )
        self.assertTrue(
            response.context['page'].object_list[0].image
        )

    def test_group_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(GROUP_PAGE_URL, kwargs={'slug': self.GROUP_SLUG})
        )
        self.assertEqual(
            response.context['page'].object_list[0].text,
            'Hello World!'
        )
        self.assertEqual(
            response.context['page'].object_list[0].author,
            self.user
        )
        self.assertEqual(response.context['group'].title, self.GROUP_TITLE)
        self.assertEqual(response.context['group'].description, '')
        self.assertTrue(
            response.context['page'].object_list[0].image
        )

    def test_new_post_page_shows_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(NEW_POST_PAGE_URL))
        self.assertIsInstance(
            response.context['form'].fields['group'],
            forms.fields.ChoiceField
        )
        self.assertIsInstance(
            response.context['form'].fields['text'],
            forms.fields.CharField
        )
        self.assertEqual(response.context['title_header'], 'Добавить запись')
        self.assertEqual(response.context['button'], 'Добавить')

    def test_edit_post_page_shows_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                self.post_edit_page_url,
                kwargs={'username': self.USERNAME, 'post_id': self.post_at.pk}
            )
        )
        self.assertIsInstance(
            response.context['form'].fields['group'],
            forms.fields.ChoiceField
        )
        self.assertIsInstance(
            response.context['form'].fields['text'],
            forms.fields.CharField
        )
        self.assertEqual(
            response.context['title_header'],
            'Редактировать запись'
        )
        self.assertEqual(response.context['button'], 'Сохранить')

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(PROFILE_PAGE_URL, kwargs={'username': self.USERNAME})
        )
        self.assertEqual(len(response.context['posts']), 12)
        self.assertEqual(response.context['profile_user'], self.user)
        self.assertEqual(
            response.context['page'].object_list[0].text,
            'Hello World!'
        )
        self.assertEqual(
            response.context['page'].object_list[0].author,
            self.user
        )
        self.assertTrue(
            response.context['page'].object_list[0].image
        )

    def test_post_page_shows_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                self.post_page_url,
                kwargs={'username': self.USERNAME, 'post_id': self.post_at.pk}
            )
        )
        self.assertEqual(len(response.context['posts']), 12)
        self.assertEqual(response.context['profile_user'], self.user)
        self.assertEqual(
            response.context['post'].text,
            self.POST_TEXT
        )
        self.assertEqual(
            response.context['post'].author,
            self.user
        )
        self.assertTrue(
            response.context['post'].image
        )

    def test_post_assignment(self):
        """Пост появляется на главной странице."""
        """И на странице указанного при публикации сообщества."""
        response_home_page = self.authorized_client.get(
            reverse(HOME_PAGE_URL) + '?page=2'
        )
        response_group_page_dubrovnik = self.authorized_client.get(
            reverse(GROUP_PAGE_URL, kwargs={'slug': self.GROUP_SLUG})
            + '?page=2'
        )
        response_group_page_croatia = self.authorized_client.get(
            reverse(GROUP_PAGE_URL, kwargs={'slug': self.GROUP_HR_SLUG})
        )
        self.assertEqual(
            response_home_page.context['page'].object_list[1],
            self.post_at
        )
        self.assertEqual(
            response_group_page_dubrovnik.context['page'].object_list[1],
            self.post_at
        )
        self.assertEqual(
            list(response_group_page_croatia.context['page'].object_list),
            []
        )

    def test_cache(self):
        """Тестирование кеша"""
        cache.clear()  # почистили кеш
        Post.objects.create(
            author=self.user,
            text=self.CACHE_TEST_POST
        )  # создали пост
        response_home_page_2_one = self.authorized_client.get(
            reverse(HOME_PAGE_URL) + '?page=2'
        )  # проверили что пост появился (12 + 1 = 13)
        Post.objects.create(
            author=self.user,
            text=self.CACHE_TEST_POST
        )  # создали еще один пост
        response_home_page_2_two = self.authorized_client.get(
            reverse(HOME_PAGE_URL) + '?page=2'
        )  # проверили что пост не появился (12 + 1 = 13)
        self.assertEqual(
            len(response_home_page_2_one.context['page'].object_list),
            3
        )
        self.assertEqual(
            len(response_home_page_2_two.context['page'].object_list),
            3
        )

    def test_auth_user_could_subscribe(self):
        """Авторизованный пользователь может подписываться"""
        counter_before_subscription = Follow.objects.count()
        self.authorized_client2.get(
            reverse(PROFILE_FOLLOW_PAGE_URL, args=[self.user3.username])
        )  # user 2 subscribes on user 3
        counter_after_subscribtion = Follow.objects.count()
        self.assertEqual(counter_before_subscription, 1)
        self.assertEqual(counter_after_subscribtion, 2)

    def test_auth_user_could_unsubcribe(self):
        """Авторизованный пользователь может отписываться"""
        counter_before_unsubscription = Follow.objects.count()
        self.authorized_client.get(
            reverse(PROFILE_UNFOLLOW_PAGE, args=[self.user2.username])
        )  # user 1 unsubscribes form user 2
        counter_after_unsubscription = Follow.objects.count()
        self.assertEqual(counter_before_unsubscription, 1)
        self.assertEqual(counter_after_unsubscription, 0)

    def test_new_post_occurs_by_subscribers(self):
        """Новая запись пользователя появляется."""
        """В ленте тех, кто на него подписан."""
        """И не появляется в ленте тех, кто не подписан на него."""
        form_data = {
            'author': self.user3,
            'text': self.SUBSCRIPTION_POST_TEXT,
        }
        self.authorized_client3.post(
            reverse(NEW_POST_PAGE_URL),
            data=form_data,
            follow=True
        )  # user 3 created post
        self.authorized_client2.get(
            reverse(PROFILE_FOLLOW_PAGE_URL, args=[self.user3.username])
        )  # user 2 subscribed on user 3
        response_u2 = self.authorized_client2.get(
            reverse(FOLLOW_PAGE_URL)
        )  # user 2 follow page
        response_u1 = self.authorized_client.get(
            reverse(FOLLOW_PAGE_URL)
        )  # user 1 follow page (is not subscribed on user 3)
        self.assertIn(
            Post.objects.get(
                author=self.user3,
                text=self.SUBSCRIPTION_POST_TEXT
            ),
            response_u2.context['page'].object_list
        )
        self.assertNotIn(
            Post.objects.get(
                author=self.user3,
                text=self.SUBSCRIPTION_POST_TEXT
            ),
            response_u1.context['page'].object_list
        )
