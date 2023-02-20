import tempfile
import shutil
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from posts.models import Post, Group, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nikita')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateTest.user)

    def test_post_create(self):
        """
        Валидная форма создает пост
        авторизованного пользователя
        """
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Пост формы',
            'group': PostCreateTest.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'Nikita'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateTest.user.id,
                text='Пост формы',
                group=PostCreateTest.group.id,
                image='posts/small.gif'
            ).exists()
        )

    def test_post_edit(self):
        """
        Валидная форма редактирует пост
        и не создает новый
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': PostCreateTest.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}), data=form_data, follow=True)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateTest.user.id,
                text='Измененный текст',
                group=PostCreateTest.group.id
            ).exists()
        )


class CommentCreateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Nikita')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user
        )

    def test_comment_create(self):
        """Валидная форма создает коммент"""
        form_data = {
            'text': 'Тестовый коммент',
        }
        responce = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': '1'}), data=form_data, follow=True)
        self.assertRedirects(
            responce,
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый коммент',
                post=self.post.id,
                author=self.user.id
            ).exists()
        )
