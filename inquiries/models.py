from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.contrib.postgres.fields import ArrayField


# Create your models here.
from django.utils.datetime_safe import datetime


class Inquiry(models.Model):
    """Модель заявки"""
    inquiry_id = models.AutoField(primary_key=True, help_text='Идентификатор заявки', blank=False)
    inquiry_title = models.CharField(max_length=256, help_text='Заголовок заявки', blank=False)
    inquiry_text = models.TextField(max_length=4096, help_text='Текст заявки', blank=False)
    inquiry_creator = models.ForeignKey(User, help_text='Создатель заявки', on_delete=models.SET_NULL, null=True)
    inquiry_created_at = models.DateTimeField(auto_now_add=True, help_text='Дата создания заявки')
    inquiry_updated_at = models.DateTimeField(help_text='Дата обновления заявки', null=True)
    # inquiry_is_done = models.BooleanField(blank=True, default=False, help_text='Признак завершения заявки')


class InquiryForm(ModelForm):
    class Meta:
        model = Inquiry
        fields = ['inquiry_title', 'inquiry_text']


class ToDoCategory(models.Model):
    category_id = models.AutoField(primary_key=True, help_text='Идентификатор категории', blank=False)
    category_name = models.CharField(max_length=256, help_text='Имя категории', blank=False)


class ToDo(Inquiry):
    """Модель заявки на исполнение"""
    TASK_STATUS = (
        ('n', 'Новая'),
        ('w', 'В работе'),
        ('r', 'На проверке'),
        ('c', 'Завершена'),
    )
    TASK_PRIORITY = (
        ('3', 'Низкий'),
        ('2', 'Средний'),
        ('1', 'Высокий'),
        ('0', 'Наивысший'),
    )
    TASK_CATEGORY = (
        ('1', 'Сантехника'),
        ('2', 'Электрика'),
        ('3', 'Ремонтные работы'),
        ('4', 'Лифт'),
        ('5', 'Общедомовая территория'),
    )
    todo_priority = models.CharField(
        max_length=1,
        choices=TASK_PRIORITY,
        blank=True,
        default='2',
        help_text='Приоритет заявки',
        null=False,
    )
    todo_assigned_to = models.ForeignKey(User,
                                         on_delete=models.SET_NULL,
                                         blank=True, null=True,
                                         help_text='Исполнитель заявки')
    todo_status = models.CharField(
        max_length=1,
        choices=TASK_STATUS,
        blank=True,
        default='n',
        help_text='Статус заявки',
    )
    todo_category = models.CharField(
        max_length=1,
        choices=TASK_CATEGORY,
        blank=True,
        default='1',
        help_text='Категория заявки'
    )

    def __str__(self):
        return f'Заявка на исполнение: {self.inquiry_created_at} - {self.inquiry_title}'

    def change_assignee(self, person):
        if self.todo_status == 'w':
            self.todo_assigned_to = person

    def send_to_review(self):
        if self.todo_status == 'w':
            self.todo_status = 'r'

    def accept(self):
        if self.todo_status == 'r':
            self.todo_status = 'c'
            self.todo_assigned_to = models.SET_NULL

    def reject(self):
        if self.todo_status == 'r':
            self.todo_status = 'w'

    def assign(self, assignee):
        self.todo_assigned_to = assignee


class Image(models.Model):
    """Изображение в заявке"""
    inquiry = models.ForeignKey('Inquiry', on_delete=models.CASCADE, null=False, help_text='Заявка')
    image = models.BinaryField(help_text='Изображение')


class Poll(Inquiry):
    """Модель голосования"""
    poll_open = models.BooleanField(blank=True, default=False, help_text='Открытое голосование')
    poll_preliminary_results = models.BooleanField(blank=True, default=False, help_text='Предварительные результаты')
    poll_deadline = models.DateTimeField(null=False, help_text='Дата завершения голосования')
    # poll_variants = models.JSONField(help_text='Варианты голосования')
    # poll_variants = ArrayField(models.CharField(max_length=255), blank=True)

    def __str__(self):
        return f'Опрос: {self.inquiry_created_at} - {self.inquiry_title}'


class Announcement(Inquiry):
    """Модель объявления"""
    announcement_is_visible = models.BooleanField(default=True, blank=False, help_text='Признак публикации')
    announcement_auto_invisible_date = models.DateField(blank=True, null=True, help_text='Дата актуальности')
    ANNOUNCEMENT_CATEGORY = (
        ('0', 'Купля/продажа'),
        ('1', 'Аренда'),
        ('2', 'Ремонтные работы'),
        ('3', 'Отключение услуг'),
        ('4', 'Placeholder'),
        ('5', 'Placeholder'),
    )
    announcement_category = models.CharField(
        null=False,
        max_length=1,
        choices=ANNOUNCEMENT_CATEGORY,
        default='0',
        help_text='Категория объявления',
        blank=False,
    )

    def __str__(self):
        return f'Объявление: {self.inquiry_created_at} - {self.inquiry_title}'


class Notification(Inquiry):
    """Модель уведомления"""
    notification_is_read = models.BooleanField(default=False, null=False, help_text='Признак прочтения')
    notification_recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, help_text='Получатель')
    NOTIFICATION_CATEGORY = (
        ('0', 'Общее'),
        ('1', 'Оплата счетов'),
        ('2', 'Показания счётчиков'),
        ('3', 'Placeholder'),
        ('4', 'Placeholder'),
        ('5', 'Placeholder'),
    )
    notification_category = models.CharField(
        null=False,
        max_length=1,
        choices=NOTIFICATION_CATEGORY,
        default='0',
        help_text='Категория уведомления',
        blank=False,
    )

    def __str__(self):
        return f'Уведомление: {self.inquiry_created_at} - {self.inquiry_title}'


class Property(models.Model):
    """Модель помещения"""
    property_id = models.AutoField(primary_key=True, help_text='Идентификатор помещения', blank=False)
    property_street_name = models.CharField(max_length=100, help_text='Улица', blank=False)
    property_building_number = models.IntegerField(help_text='Номер дома', blank=False)
    property_entrance_number = models.IntegerField(help_text='Номер подъезда', blank=False)
    property_flat_number = models.IntegerField(help_text='Номер этажа', blank=False)
    property_room_number = models.IntegerField(help_text='Номер помещения', blank=False)
    property_area = models.IntegerField(help_text='Площадь помещения', blank=False)
    PROPERTY_TYPES = (
        ('0', 'Жилое'),
        ('1', 'Коммерческое'),
    )
    property_type = models.CharField(
        max_length=1,
        choices=PROPERTY_TYPES,
        default='0',
        help_text='Тип помещения',
        blank=False
    )

    def __str__(self):
        return f'ул. {self.property_street_name}, д. {self.property_building_number}, кв. {self.property_room_number}'


class Ownership(models.Model):
    """Модель отношения помещение-собственник"""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, help_text='Владелец помещения')
    property = models.ForeignKey('Property', on_delete=models.CASCADE, blank=False, help_text='Помещение')

    def __str__(self):
        return f'{self.owner} - {self.property}'


class Comment(models.Model):
    """Модель комментария в заявке на исполнение"""
    comment_id = models.AutoField(primary_key=True, blank=False, help_text='ID комментария')
    inquiry = models.ForeignKey('Inquiry', on_delete=models.CASCADE, blank=False, null=False, help_text='Заявка')
    comment_text = models.TextField(max_length=4096, help_text='Текст комментария', blank=False, null=False)
    comment_creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, help_text='Автор комментария')
    # comment_created_at = models.DateTimeField(auto_now_add=True, help_text='Дата и время комментария')    
    comment_created_at = models.DateTimeField(help_text='Дата и время комментария')


class VoteOption(models.Model):
    """Модель варианта голосования"""
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE, blank=False, help_text='Голосование')
    vote_option_text = models.TextField(max_length=512, help_text='Текст варианта голосования', blank=False)

    def __str__(self):
        return f'{self.vote_option_text}'


class Vote(models.Model):
    """Модель голоса"""
    voter = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, help_text='Пользователь')
    selected_option = models.ForeignKey('VoteOption', on_delete=models.CASCADE, blank=False, help_text='Выбранный '
                                                                                                       'вариант')

    def __str__(self):
        return f'{self.voter}'


class Profile(models.Model):
    """Профиль пользователя системы"""
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, blank=False, help_text='Пользователь')
    # first_name = models.CharField(max_length=100, help_text='Имя пользователя')
    # last_name = models.CharField(max_length=100, help_text='Фамилия пользователя')
    # email = models.EmailField(max_length=150, help_text='Адрес электронной почты')
    phone_number = models.CharField(max_length=100, help_text='Номер телефона')
    photo = models.BinaryField(null=True, help_text='Фотография пользователя')
    is_manager = models.BooleanField(default=False, blank=False, help_text='Признак управляющего')
    # is_blocked = models.BooleanField(default=False, blank=False, help_text='Признак блокировки')

    class Meta:
        ordering = ['is_manager', 'user']

    # def __str__(self):
    #     return {self.user.username}


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
