# Generated by Django 2.2.16 on 2023-02-09 12:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Введите заголовок группы', max_length=200, verbose_name='Заголовок')),
                ('description', models.TextField(help_text='Введите описание группы', verbose_name='Описание')),
                ('slug', models.SlugField(help_text='Введите название группы, к которой будет относиться пост', unique=True, verbose_name='Группа')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Время и дата публикации')),
                ('text', models.TextField(help_text='Введите текст поста', verbose_name='Текст поста')),
                ('image', models.ImageField(blank=True, help_text='Загрузите заглавную картинку поста', upload_to='posts/', verbose_name='Картинка')),
                ('author', models.ForeignKey(help_text='Выберите автора поста', on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('group', models.ForeignKey(blank=True, help_text='Выберите группу, к которой будет относиться пост', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='Группа')),
            ],
            options={
                'verbose_name': 'Пост',
                'verbose_name_plural': 'Посты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст коммента')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время добавления')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор коммента')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='Коммент')),
            ],
        ),
    ]