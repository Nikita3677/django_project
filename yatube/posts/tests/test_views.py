import tempfile
import shutil
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from django import forms
from posts.models import Post, Group, Follow
from yatube.settings import POSTS_IN_PAGE


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='somebody')
        cls.user_sub = User.objects.create_user(username='sub')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client_sub = Client()
        self.authorized_client.force_login(PostViewsTests.user)
        self.authorized_client_sub.force_login(PostViewsTests.user_sub)

    def test_pages_uses_correct_templates(self):
        """Страницы используют ожидаемые шаблоны"""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:profile', kwargs={
                'username': 'somebody'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:group_list', kwargs={
                'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:post_edit', kwargs={
                'post_id': '1'}): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_post(self, post):
        self.assertEqual(post.text, PostViewsTests.post.text)
        self.assertEqual(post.author, PostViewsTests.user)
        self.assertEqual(post.group, PostViewsTests.group)
        self.assertEqual(post.image, PostViewsTests.post.image)

    def test_pages_with_paginator_show_correct_context(self):
        """
        Словарь context страниц
        /index/,/group/slug и /profile/username
        содержит ожидаемые значения
        """
        cache.clear()
        field_objects = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'somebody'})
        ]
        for field in field_objects:
            response = self.authorized_client.get(field)
            with self.subTest(field=field):
                first_object = response.context['page_obj'][0]
                self.check_post(first_object)

    def test_post_detail_page_list_is_1(self):
        """
        На страницу /post_detail/ выводится 1 пост,
        отфильтрованный по id
        И словарь context содержит ожидаемые значения
        """
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        post_object = response.context['post']
        self.assertEqual(post_object.id, 1)
        self.check_post(post_object)

    def test_pages_without_paginator_show_correct_context(self):
        """
        Словарь context страниц
        /create и /posts/post_id/edit
        содержит ожидаемые значения
        """
        cache.clear()
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        urls_list = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        ]
        for url in urls_list:
            response = self.authorized_client.get(url)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        """
        Проверяет работу кэша главной страницы
        """
        test_post = Post.objects.create(
            text='Тестовый текст',
            author=PostViewsTests.user
        )
        responce = self.authorized_client.get(
            reverse('posts:index'))
        Post.objects.get(id=test_post.id).delete()
        responce_with_cache = self.authorized_client.get(
            reverse('posts:index'))
        self.assertEqual(responce.content, responce_with_cache.content)
        cache.clear()
        responce_after_del_cache = self.authorized_client.get(
            reverse('posts:index'))
        self.assertNotEqual(responce.content, responce_after_del_cache.content)

    def test_authorized_client_can_follow(self):
        """Подписка"""
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'sub'}))
        self.assertTrue(
            Follow.objects.filter(
                user=PostViewsTests.user,
                author=PostViewsTests.user_sub
            ).exists()
        )

    def test_authorized_client_can_unfollow(self):
        """Отписка"""
        Follow.objects.create(
            user=PostViewsTests.user,
            author=PostViewsTests.user_sub
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'sub'}))
        self.assertFalse(
            Follow.objects.filter(
                user=PostViewsTests.user,
                author=PostViewsTests.user_sub
            ).exists()
        )

    def test_new_post_for_follow_exists(self):
        """
            Новая запись появляется у подписанных
            и не появляется у неподписанных
        """
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'sub'}))
        Post.objects.create(
            text='Тест подписки',
            author=PostViewsTests.user_sub
        )
        field_objects = {
            reverse('posts:follow_index'): [1, self.authorized_client],
            reverse('posts:follow_index'): [0, self.authorized_client_sub]
        }
        for field, value in field_objects.items():
            response = value[1].get(field)
            self.assertEqual(len(response.context['page_obj']), value[0])


class PaginatorPostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='somebody')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        for i in range(1, 14):
            Post.objects.create(
                text='Тестовый текст',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorPostViewsTests.user)

    def test_first_page_contains_10_posts_second_3(self):
        """
        Количество постов на первой странице равно 10 и
        на второй равно 3
        /index/,/group/slug и /profile/username
        """
        cache.clear()
        posts_in_second_page = Post.objects.count() - POSTS_IN_PAGE
        field_objects = {
            reverse('posts:index'): POSTS_IN_PAGE,
            reverse('posts:group_list', kwargs={
                    'slug': 'test-slug'}): POSTS_IN_PAGE,
            reverse('posts:profile', kwargs={
                    'username': 'somebody'}): POSTS_IN_PAGE,
            reverse('posts:index') + '?page=2': posts_in_second_page,
            reverse('posts:group_list', kwargs={
                'slug': 'test-slug'}) + '?page=2': posts_in_second_page,
            reverse('posts:profile', kwargs={
                'username': 'somebody'}) + '?page=2': posts_in_second_page
        }
        for field, value in field_objects.items():
            response = self.authorized_client.get(field)
            with self.subTest(field=field):
                self.assertEqual(len(response.context['page_obj']), value)
