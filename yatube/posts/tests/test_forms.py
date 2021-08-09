import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User

HOMEPAGE_URL = 'posts:index'
NEW_POST_URL = 'posts:new_post'


@override_settings(MEDIA_ROOT=(settings.BASE_DIR + '/media'))
class PostCreateFormTests(TestCase):

    GROUP_TITLE = 'Дубровник'
    GROUP_SLUG = 'dubrovnik'
    USERNAME = 'split'
    POST_TEXT = 'Проверка'
    POST_EDIT_TEXT_BEFORE_EDIT = 'Состояние А'
    POST_EDIT_TEXT_AFTER_EDIT = 'Состояние B'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username=self.USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title=self.GROUP_TITLE,
            slug=self.GROUP_SLUG
        )
        self.post = Post.objects.create(
            author=self.user,
            text=self.POST_EDIT_TEXT_BEFORE_EDIT
        )
        self.edit_post_url = 'posts:edit_post'
        self.post_url = 'posts:post'

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        image = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=image,
            content_type="image/gif"
        )
        form_data = {
            'author': self.user,
            'text': self.POST_TEXT,
            'group': 1,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse(NEW_POST_URL),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(HOMEPAGE_URL))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            Post.objects.first(),
            Post.objects.get(text=self.POST_TEXT, group=1, author=self.user)
        )
        self.assertEqual(
            Post.objects.first(),
            Post.objects.get(image='posts/small.gif')
        )

    def test_cant_create_post_without_text(self):
        """Поле формы text обязательно для заполнения."""
        posts_count = Post.objects.count()
        form_data = {
            'author': self.user,
            'group': 1
        }
        response = self.authorized_client.post(
            reverse(NEW_POST_URL),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(response, 'form', 'text', 'Обязательное поле.')

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse(
                self.edit_post_url,
                kwargs={'username': self.USERNAME, 'post_id': self.post.pk}
            ),
            data={'text': self.POST_EDIT_TEXT_AFTER_EDIT},
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                self.post_url,
                kwargs={'username': self.USERNAME, 'post_id': self.post.pk}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            Post.objects.first(),
            Post.objects.get(
                text=self.POST_EDIT_TEXT_AFTER_EDIT,
                author=self.user
            )
        )
