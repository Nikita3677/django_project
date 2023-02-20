from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from http import HTTPStatus
from posts.models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='Egor')
        cls.user_not_author = User.objects.create_user(username='Artyom')
        Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(
            PostURLTests.user_author)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(
            PostURLTests.user_not_author)

    def test_templates_pages_available_to_everyone(self):
        """
        Страницы, доступные любым пользователям,
        используют ожидаемые шаблоны
        """
        cache.clear()
        field_urls = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/Egor/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for field, value in field_urls.items():
            with self.subTest(field=field):
                response = self.guest_client.get(field)
                self.assertTemplateUsed(response, value)

    def test_pages_available_to_everyone(self):
        """Страницы доступны любым пользователям"""
        cache.clear()
        field_urls = {
            '/': HTTPStatus.OK.value,
            '/group/test-slug/': HTTPStatus.OK.value,
            '/profile/Egor/': HTTPStatus.OK.value,
            '/posts/1/': HTTPStatus.OK.value,
            'tralala': HTTPStatus.NOT_FOUND.value
        }
        for field, value in field_urls.items():
            with self.subTest(field=field):
                response = self.guest_client.get(field)
                self.assertEqual(response.status_code, value)

    def test_pages_available_to_authorized(self):
        """
        Страницы, доступные авторизованным пользователям
        """
        field_urls = {
            '/posts/1/edit/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.OK.value,
            '/follow/': HTTPStatus.OK.value,
            '/posts/1/comment/': HTTPStatus.FOUND.value,
            '/profile/Artyom/follow/': HTTPStatus.FOUND.value,
            '/profile/Artyom/unfollow/': HTTPStatus.FOUND.value
        }
        for field, value in field_urls.items():
            with self.subTest(field=field):
                response = self.authorized_client_author.get(field)
                self.assertEqual(response.status_code, value)

    def test_posts_post_id_edit_not_author(self):
        """Редактирование поста недоступно не автору"""
        response = self.authorized_client_not_author.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_templates_pages_available_to_authorized(self):
        """
        Страницы редактирования поста и создания поста
        используют ожидаемые шаблоны
        """
        field_urls = {
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for field, value in field_urls.items():
            with self.subTest(field=field):
                response = self.authorized_client_author.get(field)
                self.assertTemplateUsed(response, value)
