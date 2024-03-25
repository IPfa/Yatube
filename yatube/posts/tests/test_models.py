from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):

    POST_TEXT = 'Все отлично, купаюсь в море))'
    USER_USERNAME = 'split'

    def setUp(self):
        self.user = User.objects.create_user(username=self.USER_USERNAME)
        self.post = Post.objects.create(
            text=self.POST_TEXT,
            author=self.user
        )

    def test_object_name_is_text_field(self):
        """__str__  post - это строчка с содержимым
           post.text обрезанная до 15 символов."""
        post = self.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):

    GROUP_TITLE = 'Дубровник'
    GROUP_SLUG = 'Dubrovnik'

    def setUp(self):
        self.group = Group.objects.create(
            title=self.GROUP_TITLE,
            slug=self.GROUP_SLUG
        )

    def test_object_name_is_title_field(self):
        """__str__  group - это строчка с содержимым group.title."""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
