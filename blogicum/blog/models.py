from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

# Я еще раз почитал информацию
# в Интернете (и на официальном сайте Django):
# related_name для полей одной модели могут совпадать, если они
# указывают на связь с разными моделями.
# Другими словами, related_name обязаны быть разными
# для связей с одной моделью
# (особый случай, если related_name для поля указывается
# в абстрактном классе, ведь
# тогда в дочерних это имя будет тем же
# и возникнет коллизия: в таких случаях
# рекомендуется использовать синтаксис '%(app_label)s_%(class)s')


class AbstractModel(models.Model):
    """
    Модель-шаблон.
    """
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title


class Category(AbstractModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(AbstractModel):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name


class Post(AbstractModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Формат: ГГГГ-ММ-ДД ЧЧ:ММ:СС. '
            'Если установить дату и время в будущем '
            '— можно делать отложенные публикации.'
        ),
    )
    image = models.ImageField('Фото', upload_to='post_images', blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    text = models.TextField('Текст')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )

    class Meta:
        ordering = ('created_at',)
