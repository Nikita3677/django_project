from django.test import TestCase, Client


class StaticPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls(self):
        """Статичные страницы доступны"""
        field_urls = {
            '/about/author/': 200,
            '/about/tech/': 200
        }
        for field, value in field_urls.items():
            with self.subTest(field=field):
                response = self.guest_client.get(field)
                self.assertEqual(response.status_code, value)

    def test_templates_about(self):
        """Статичные страницы используют ожидаемые шаблоны"""
        field_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for field, value in field_urls.items():
            with self.subTest(field=field):
                response = self.guest_client.get(field)
                self.assertTemplateUsed(response, value)
