from django.db import models

# Create your models here.

from datetime import datetime

from django.contrib.auth.models import User, Group, UserManager
from django.utils.html import format_html
from django.db.models import F
from django.db.models import Max


class Location(models.Model):
    name = models.CharField(max_length=50,verbose_name='Наименование локации')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"

class Company(models.Model):
    COMPANY_TYPES = (('ук','Управляющая компания'),('подряд','Подрядчик'),)

    location = models.ForeignKey(Location, on_delete= models.SET_NULL, null=True, blank= True, default=None, verbose_name='Локация')
    company_type = models.CharField(max_length=20, null=True, blank= True, default=None, verbose_name='Тип компании', choices=COMPANY_TYPES)
    name = models.CharField(max_length=50,verbose_name='Наименование компании')
    legal_name = models.CharField(max_length=150,null=True, blank= True, default=None, verbose_name='Полное наименование')
    phone = models.CharField(max_length=50,null=True, blank= True, default=None, verbose_name='Телефон')
    address = models.CharField(max_length=150,null=True, blank= True, default=None, verbose_name='Адрес')
    email = models.CharField(max_length=50,null=True, blank= True, default=None, verbose_name='Email')
    comment = models.TextField(null=True, blank= True, default=None, verbose_name='Комментарий')
    is_used = models.BooleanField(default=False, verbose_name='Использутся')
    logo = models.ImageField(null=True, blank= True, default=None, verbose_name='Логотип', upload_to='company')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

class District(models.Model):
    name = models.CharField(max_length=50,verbose_name='Наименование участка')
    company = models.ForeignKey(Company, null=True, blank=True, default=None, on_delete=models.SET_NULL, verbose_name = 'Компания')
    def __str__(self):
        return f'{self.name}/{self.company}'
    class Meta:
        verbose_name = "Участок"
        verbose_name_plural = "Участки"

class Street(models.Model):
    location = models.ForeignKey(Location, on_delete= models.SET_NULL, null=True, blank= True, default=None, verbose_name='Локация')
    name = models.CharField(max_length=50,verbose_name='Наименование улицы')
    legal_name = models.CharField(max_length=50, null=True, blank=True, default=None, verbose_name='Правильное наименование улицы')
    c1_name = models.CharField(max_length=50, null=True, blank=True, default=None, verbose_name='Наименование улицы в 1С')
    is_used = models.BooleanField(default=False, verbose_name='Использутся')
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ('name',)
        verbose_name = "Улица"
        verbose_name_plural = "Улицы"

class StreetInCompany(models.Model):
    street = models.ForeignKey(Street, on_delete=models.DO_NOTHING, verbose_name = 'Улица')
    company = models.ForeignKey(Company, null=True, blank=True, default=None, on_delete=models.CASCADE, verbose_name = 'Компания')
    def __str__(self):
        return f"{self.street}-{self.company}"

    class Meta:
        ordering = ('street',)
        verbose_name = "Обслуживаемые улицы"
        verbose_name_plural = "Обслуживаемые улицы"


class WorkSystem(models.Model):
    name = models.CharField(max_length=50,verbose_name='Наименование рабочей системы')
    pictogram = models.CharField(max_length=15, null=True, blank=True, default=None, verbose_name = 'Пиктограмма')
    is_used = models.BooleanField(default=False, verbose_name='Использутся')

    def __str__(self):
        return f"{self.pictogram if self.pictogram else ''}{self.name}"
    class Meta:
        verbose_name = "Рабочая система"
        verbose_name_plural = "Рабочие системы"


class Building(models.Model):
    location = models.ForeignKey(Location, on_delete= models.SET_NULL, null=True, blank= True, default=None, verbose_name='Локация')
    name = models.CharField(max_length=50, null=True, blank=True, default=None, verbose_name='Объект')
    street = models.ForeignKey(Street, on_delete=models.DO_NOTHING, verbose_name = 'Улица')
    house = models.CharField(max_length=15,null=True, default=None, verbose_name='Дом')
    lon = models.FloatField(null=True, blank=True, default=None, verbose_name='lon')
    lat = models.FloatField(null=True, blank=True, default=None, verbose_name='lat')
    channelid = models.BigIntegerField(null=True, blank=True, default=None, verbose_name='Ид. телеграмм канала')
    
    square = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, verbose_name='Площадь')
    #dogovor = models.CharField(max_length=50, null=True, blank=True, default=None, verbose_name='Договор управления')
    #protoсol = models.CharField(max_length=50, null=True, blank=True, default=None, verbose_name='Протокол ОСС')
    #senior = models.CharField(max_length=50, null=True, blank=True, default=None, verbose_name='Старший по дому')
    flat_count = models.IntegerField(default=0, verbose_name='Кол-во квартир')
    floor_count = models.IntegerField(default=0, verbose_name='Кол-во этажей')
    photo = models.ImageField(null=True, blank=True, default=None, verbose_name='Фото', upload_to = "buildings/")


    #senior_sign = models.CharField(max_length=50, null=True, blank=True, default=None, verbose_name='Старший по дому (в лице)')
    #flat_number = models.CharField(max_length=50, null=True, blank=True, default=None, verbose_name='Номер кв старшего')

    company = models.ForeignKey(Company, null=True, blank=True, default=None, on_delete=models.CASCADE, verbose_name = 'Компания')
    description = models.TextField(null=True, blank=True, default=None, verbose_name = 'Описание')
    comment = models.TextField(null=True, blank=True, default=None, verbose_name = 'Комментарий')
    source = models.JSONField(null=True, blank= True, default=None) 

    #gis_url = models.CharField(max_length=300, null=True, blank= True, default=None, verbose_name='Ссылка на ГИС ЖКХ')
    #uid = models.CharField(max_length=300, null=True, blank= True, default=None, verbose_name='UID')
       

    def __str__(self):
        return f"{self.name if self.name else '-'}"

    class Meta:
        ordering = ('name',)
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"

class Employee(models.Model):
    POSTS = [('boss','Генеральный'),
             ('secretary','Секретарь'),
             ('chief','Начальник участка'),
             ('itr','ИТР'),
             ('admin','Административный'),
             ('disp','Диспетчер участка'),
             ('master','Мастер участка'),
             ('worker','Рабочий участка'),]

    user = models.OneToOneField(User, null=True, blank=True, default=None, on_delete=models.DO_NOTHING, verbose_name = 'Пользователь')
    name = models.CharField(max_length=50,verbose_name='ФИО')
    post = models.CharField(max_length=20, default='worker', verbose_name = 'Должность', choices=POSTS)
    worksystem = models.ManyToManyField(WorkSystem, blank=True, default=None, verbose_name='Рабочая система')
    district = models.ManyToManyField(District, null=True, blank=True, default=None, verbose_name='Участок')
    company = models.ForeignKey(Company, null=True, blank=True, default=None, on_delete=models.DO_NOTHING, verbose_name = 'Компания')
    deleted = models.BooleanField(default=False, verbose_name='Уволен?')
    phone = models.CharField(max_length=12, null=True, blank=True, default=None, verbose_name='Телефон')
    telegram = models.CharField(max_length=12, null=True, blank=True, default=None, verbose_name='Телеграмм')
    district_main = models.ForeignKey(District, on_delete=models.SET_NULL,null=True, blank=True, default=None, verbose_name='Основной участок',related_name='district_main')
    #can_selected = models.BooleanField(null=True, blank=True, default=None, verbose_name='Может выбирать')
    comment = models.TextField(null=True, blank=True, default=None, verbose_name='Комментарий')
    #default_settings = models.JSONField(null=True, blank=True, default=None, verbose_name='Параметры по умолчанию')
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

class StandardDescription(models.Model):
    name = models.CharField(max_length=500, verbose_name = 'Описание')
    worksystem = models.ForeignKey(WorkSystem, on_delete=models.CASCADE, verbose_name = 'Рабочая система')
    class Meta:
        verbose_name = "Стандартное описание заявки"
        verbose_name_plural = "Стандартные описания заявок"






