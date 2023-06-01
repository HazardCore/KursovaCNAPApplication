import json
import datetime
from tempfile import template

from django.db import models
from django.contrib.postgres import fields

from django.utils.translation import gettext_lazy as _
from django.forms.models import model_to_dict
from django.utils.html import format_html, mark_safe

from django.conf import settings

import uuid

from simple_history.models import HistoricalRecords
from django.core.validators import FileExtensionValidator

class CertificateApplicationStatusType(models.TextChoices):
    CREATED = 'CREATED', _('Створена') 
    PROCESSING = 'PROCESSING', _('В обробці') 
    FAILED = 'FAILED', _('Помилка обробки') 
    ON_REVIEW = 'ON_REVIEW', _('Подана на розгляд') 
    EXECUTED = 'EXECUTED', _('Виконана')  
    REJECTED = 'REJECTED', _('Запит відхилено')  

class TemplateType(models.TextChoices):
    TYPE_1 = 0, _('Довідка про медичне страхування')


# class SoftDeleteManager(models.Manager):
#     MODE_CHOISE = ['clear', 'deleted', 'all']

#     def __init__(self, *args, **kwargs):
#         mode = kwargs.pop('mode', 'clear')
#         ##raise Exception(mode)
#         if not mode:
#             raise Exception('"mode" is required in "SoftDeleteManager"')

#         if mode not in SoftDeleteManager.MODE_CHOISE:
#             raise Exception(
#                 '"mode" must bee in  "SoftDeleteManager.MODE_CHOISE"')
#         super(SoftDeleteManager, self).__init__(*args, **kwargs)
#         self.mode = mode

#     def get_queryset(self):
#         base_qeeryset = super(SoftDeleteManager, self).get_queryset()
#         ##base_qeeryset = SafeDeleteQueryset(self.model, using=self._db)

#         if self.mode == 'clear':
#             qs = base_qeeryset.filter(is_deleted=False)
#         elif self.mode == 'deleted':
#             qs = base_qeeryset.filter(is_deleted=True)
#         elif self.mode == 'all':
#             qs = base_qeeryset.all()
#         else:
#             raise Exception('"mode" is not set')

#         return qs
    
#     def create(self, *args, **kwargs):
#         print("************************************************!!!!!!!!!!!!!!")
        
#         self.auditlog_event_type = kwargs.get("event_type", None)
#         self.auditlog_actor = kwargs.get("actor", None)
#         self.auditlog_object_repr = kwargs.get("object_repr", None)
#         try:
#             kwargs.pop('event_type', None)
#             kwargs.pop('actor', None)
#             kwargs.pop('object_repr', None)
#             ret = super(SoftDeleteManager, self).create(*args, **kwargs)
#         finally:
#             del self.auditlog_event_type
#             del self.auditlog_actor
#             del self.auditlog_object_repr
#         return ret


class CertificateApplication(models.Model):
    id = models.AutoField(primary_key=True)

    application_status = models.CharField(max_length=20, choices=CertificateApplicationStatusType.choices, 
                                                    default=CertificateApplicationStatusType.CREATED,
                                                    verbose_name='Статус заявки')

    applicant_unique_code = models.CharField(max_length=10, null=True, blank=True,
                                       verbose_name='Код РНОКПП заявника', help_text='Подається разом з заявою')

    failure_reason = models.CharField(max_length=255, null=True, blank=True,
             verbose_name='Причина помилки', help_text='Помилка отримання даних від міністерства')

    сertificate_no = models.CharField(max_length=255, null=True, blank=True,
             verbose_name='Унікальний номер довідки', help_text='Генерується автоматично при підтвердженні заявки')

    applicant_fullname = models.CharField(max_length=255, null=True, blank=True,
             verbose_name='Повне ім\'я заявника', help_text='Заповнюється за запитом до міністерства автоматично')
    applicant_home_address = models.CharField(max_length=512, null=True, blank=True,
             verbose_name='Домашня адреса', help_text='Заповнюється за запитом до міністерства автоматично')
    applicant_medical_ensurance = models.CharField(max_length=512, null=True, blank=True,
             verbose_name='Номер та дата медичного страхування', help_text='Заповнюється за запитом до міністерства автоматично')

    application_file = models.FileField(null=True, blank=True, verbose_name='Заявка в форматі PDF', help_text="У вигляді файлу", max_length=512,)
    
    

    created_at = models.DateTimeField(verbose_name='Дата створення заявки', auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name='Дата оновлення інформації про заявку', auto_now=True,)

    # objects = SoftDeleteManager(mode='all')

    class Meta:
        ordering = ["id"]
        verbose_name = 'Довідка'
        verbose_name_plural = 'Довідки'


class Template(models.Model):
    main_file = models.FileField(verbose_name="Файл",
                                 null=True,
                                 max_length=500)
    title = models.CharField(verbose_name="Назва", max_length=100,
                             default='', db_index=True)
    create_date = models.DateField(verbose_name="Дата створення документа",
                                   auto_now_add=True, editable=False,
                                   db_index=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name="Автор",
                               on_delete=models.PROTECT, null=True)
    request_trigger = models.CharField(verbose_name="Предмет заявки",
                                       choices=TemplateType.choices,
                                       max_length=100, db_index=True,
                                       unique=True,
                                       error_messages={
                                           'unique': _(
                                               "Шаблон цієї заявки вже існує!"), })

    class Meta:
        verbose_name = 'Шаблон'
        verbose_name_plural = 'Шаблони'

    def __str__(self):
        return f'{self.title} від  {self.create_date}'




    # def __str__(self):
    #     return self.сertificate_no + " " + self.applicant_fullname