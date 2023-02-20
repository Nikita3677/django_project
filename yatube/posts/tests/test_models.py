from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='Тестовый слаг'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def test_model_post_have_correct_object_names(self):
        """Проверяем метод __str__ модели Post."""
        post = PostModelTest.post
        post_str = str(post)
        post_text = post.text[:15]
        self.assertEqual(post_str, post_text,
                         'Метод __str__ модели Post работает неправильно')

    def test_model_post_have_correct_verbose_name(self):
        """Проверяем verbose_name модели Post"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, value)

    def test_model_post_have_correct_help_text(self):
        """Проверяем help_text модели Post"""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'author': 'Выберите автора поста',
            'group': 'Выберите группу, к которой будет относиться пост'
        }
        for field, value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='Тестовый слаг'
        )

    def test_model_group_have_correct_object_names(self):
        """Проверяем метод __str__ модели Group."""
        group = GroupModelTest.group
        group_str = str(group)
        group_title = group.title[:30]
        self.assertEqual(group_str, group_title,
                         'Метод __str__ модели Group работает неправильно')

    def test_model_group_have_correct_verbose_name(self):
        """Проверяем verbose_name модели Group"""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'description': 'Описание',
            'slug': 'Группа'
        }
        for field, value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, value)

    def test_model_group_have_correct_help_text(self):
        """Проверяем help_text модели Group"""
        group = GroupModelTest.group
        field_help_text = {
            'title': 'Введите заголовок группы',
            'description': 'Введите описание группы',
            'slug': 'Введите название группы, к которой будет относиться пост'
        }
        for field, value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, value)
