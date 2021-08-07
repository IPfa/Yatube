from django.test import Client, TestCase


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_author_url_exists_at_desired_location(self):
        """Страница /about/author/ доступна любому пользователю."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech_url_exists_at_desired_location(self):
        """Страница /about/tech/ доступна любому пользователю."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
