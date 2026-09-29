from cProfile import Profile
from django.db import models
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.utils import timezone

from dict.models import Building, Company, District, Employee, Street, WorkSystem

# Create your models here.

class OrderState(models.Model):
    id = models.CharField(primary_key=True, max_length=30, verbose_name='Ид')
    name = models.CharField(max_length=30, verbose_name='Наименование')
    color = models.CharField(max_length=10, null=True, blank=True, default=None, verbose_name='Цвет')
    pos = models.IntegerField(default=0,verbose_name='Порядок сортировки')
    сompleted = models.BooleanField(default=False, verbose_name='Признак завершения')
    
    def __str__(self):
        return self.name

    @property
    def state_color(self):
        return format_html('<div style="width: 50px; height: 20px; background: {}"></div>', self.color)
    state_color.fget.short_description = 'Цвет'

    class Meta:
        ordering = ('pos',)
        verbose_name = "Состояние заявки"
        verbose_name_plural = "Состояния заявок"

class Order(models.Model):
    #ORDER_STATE = [('accepted','Принята'),('inprogress','В работе'),('tocheck','Проверить'),('completed','Исполнена'),('cancel','Отмена'),('localized','Локализована'),('passed','Передана'),('worked','Отработана'),('paid','Исполнена платно'),]
    ORDER_TYPE = [('houses','Общедомовые'),('flats','Поквартирные'),('paid','Платная'),('repair','Текущий ремонт'),('household','Хознужды'),('emergency','Аварийная')]
    ORDER_PRIORITY = [('emergency','❗Аварийная'),('urgent','Срочная'),('current','Текущая')]
    PLAN_PERIODS = [('until','До полудня'),('after','После полудня'),('during','В течениe дня')]
    SOURCE_TYPE = [('disp','Диспетчер'),('site','Сайт'),('max','Max'),('auto','Автозаявка')]

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = 'Автор')
    
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name = 'Дата создания')
    modified_date = models.DateTimeField(null=True, blank=True, default=None, verbose_name = 'Дата изменения')
    last_printed_date = models.DateTimeField(null=True, blank=True, default=None, verbose_name = 'Дата последней печати')
    
    number = models.CharField(max_length=15, null=True, blank=True, default=None, verbose_name='Номер')
    order_date = models.DateField(null=True, blank=True, verbose_name = 'Дата заявки')
    
    state = models.ForeignKey(OrderState, on_delete=models.SET_NULL, null=True, blank=True, default='accepted', verbose_name = 'Состояние')


    ordertype = models.CharField(max_length=20, default='houses', verbose_name = 'Тип', choices=ORDER_TYPE)
    priority = models.CharField(max_length=20, default='current', verbose_name = 'Приоритет', choices=ORDER_PRIORITY)
    sourcetype = models.CharField(max_length=20, default='disp', verbose_name = 'Источник', choices=SOURCE_TYPE)

    #company = models.ForeignKey(Company, null=True, blank=True, default=None, on_delete=models.DO_NOTHING, verbose_name = 'Компания')
    district = models.ForeignKey(District, null=True, blank=True, default=None, on_delete=models.SET_NULL, verbose_name = 'Участок')

    citizen = models.CharField(max_length=50,null=True, blank=True, default=None, verbose_name='ФИО')
    phone = models.CharField(max_length=15,null=True, blank=True, default=None, verbose_name='Телефон')
    street = models.ForeignKey(Street, null=True, blank=True, default=None, on_delete=models.SET_NULL, verbose_name = 'Улица')
    house = models.CharField(max_length=15,null=True, default=None, verbose_name='Дом')
    flat = models.CharField(max_length=15,null=True, blank=True, default=None, verbose_name='Квартира')
    entrance = models.IntegerField(null=True, blank=True, default=None, verbose_name='Подъезд')
    floor = models.IntegerField(null=True, blank=True, default=None, verbose_name='Этаж')
    
    building = models.ForeignKey(Building, null=True, blank=True, default=None, on_delete=models.SET_NULL, verbose_name = 'Объект')

    plan_date = models.DateField(null=True, blank=True, default=None, verbose_name = 'Дата план')
    plan_period = models.CharField(max_length=20, null=True, blank=True, default='during', verbose_name = 'Период план', choices=PLAN_PERIODS)

    worksystem = models.ForeignKey(WorkSystem, null=True, blank=True, default=None, on_delete=models.SET_NULL, verbose_name = 'Рабочая система')
    description = models.TextField(max_length=500, verbose_name='Описание заяки')

    #worker = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.DO_NOTHING, verbose_name = 'Исполнитель', related_name='worker_user')
    master = models.ForeignKey(Employee, null=True, blank=True, default=None, on_delete=models.SET_NULL, verbose_name = 'Мастер', related_name='master_user')

    fact_date = models.DateTimeField(null=True, blank=True, default=None, verbose_name = 'Фактическая дата выполнения')
    fact_start_work_time = models.DateTimeField(null=True, blank=True, default=None, verbose_name = 'Фактическое время начала выполнения')
    fact_description = models.TextField(null=True, blank=True, default=None, verbose_name='Фактическое описание')

    employee = models.ManyToManyField(Employee, blank=True, verbose_name='Исполнитель')
    orderid = models.IntegerField(null=True, blank=True, default=None, verbose_name='Внешний ид')
    

    #scan = models.FileField(null=True, blank=True, default=None, upload_to='scan', verbose_name='Скан наряд-задания',
    #help_text='Выберите файл скана наряда и нажмите Сохранить и продолжить')

    #email = models.CharField(max_length=30, null=True, blank=True, default=None, verbose_name='Email')
    #can_selected = models.BooleanField(null=True, blank=True, default=None, verbose_name='Выбор исполнителем')
    summa = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, blank=True, null= True, verbose_name='Сумма')

    company_owner = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name='УК', related_name='company_owner')
    company_exec = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name='Подрядчик', related_name='company_exec')
    #source = models.JSONField(null=True, blank= True, default=None)    

    #routeorder = models.ForeignKey(RouteOrder, on_delete=models.SET_NULL, null=True, blank= True, default=None, verbose_name='Заявка на мехуборку')

    #parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None, verbose_name='Род.заявка')
    plan_text = models.CharField(max_length=30, null=True, blank=True, default=None, verbose_name='План текст')
    worker_text = models.CharField(max_length=50,null=True, blank=True, default=None, verbose_name='Исполнитель_')
    master_text = models.CharField(max_length=50,null=True, blank=True, default=None, verbose_name='Мастер_')


    @property
    def get_photo_count(self):
        return FotosInOrder.objects.filter(order=self).count()
    get_photo_count.fget.short_description = 'Кол-во фото'

    #@property
    #def get_results(self):
    #    return ";".join([ou.description for ou in OrderUpdate.objects.filter(order = self, update_type='text')])
    #get_results.fget.short_description = 'Результат'


    @property
    def get_profile_company(self):
        return Employee.objects.get(user = self.author).company
    get_profile_company.fget.short_description = 'Адрес'

    @property
    def get_profile_name(self):
        return Employee.objects.get(user = self.author).name
    get_profile_company.fget.short_description = 'ФИО'


    @property
    def address(self):
        s = ''
        street_name = self.street.name if self.street else 'не указано'
        if self.flat:
            s = f'{street_name}, {self.house} кв.{self.flat}'
        else:
            s = f'{street_name}, {self.house}' 
        
        return format_html(f'<div>{s}</div><div style="font-size:11px">{self.company_owner if self.company_owner else ""}</div>')
    address.fget.short_description = 'Адрес'

    @property
    def colored_state(self):
        color = ''
        name = ''
        st = ''

        if self.sourcetype == 'site':
            st = f'<img src="/static/site.png" title="Заявка с сайта">'
        if self.sourcetype == 'max':
            st = f'<img src="/static/telegram2.png" title="Заявка с телеграма">'
        
        #scan = f'<img src="/static/scan.png" title="Заявка отсканированна">' if self.scan else ''
        foto = f'<img src="/static/foto.png" title="Заявка с фото">' if FotosInOrder.objects.filter(order=self) else ''
        #priority = f'<nobr><img src="/static/urgent.png" title="Срочно">' if self.priority in ('urgent','emergency') else ''
        priority = f'<span style="font-size: 18px">❗</span>' if self.priority in ('urgent','emergency') else ''
        paid = f'<span style="font-size: 18px">₽</span>' if self.ordertype == 'paid' else ''

        if self.last_printed_date:
            lpd = f'<img src="/static/printer.png" title="Дата последней печати: {self.last_printed_date}">'
        else:
            lpd = ''

        if self.plan_date:
            if self.state in ['accepted','inprogress'] and self.plan_date < datetime.today().date():
                color = 'red'
                name = 'Просрочена'

        return format_html(
                '<div style="white-space: nowrap;"><small style="padding: 3px; border-radius: 3px; background-color: {}; color: white;">{}</small>'+lpd+priority+st+foto+paid+'</div>',
                self.state.color if self.state else 'black',
                self.state.name if self.state else '---',
            )    
    colored_state.fget.short_description = 'Статус'  
    
    @property
    def get_employees(self):
        s = "; ".join([e.name for e in self.employee.all()])
        return s+("; "+self.worker_text if self.worker_text else "")
    get_employees.fget.short_description = 'Исполнитель'
    
    @property
    def shot_description(self):
        d = self.description[:60]
        if self.fact_description:
            return format_html(f'<div>{self.worksystem.pictogram if self.worksystem and self.worksystem.pictogram else ""}{d}</div><div>🟢<span style="font-style: italic; color: grey">{self.fact_description[:60]}</span></div>')
        else:
            return format_html(f'<div>{self.worksystem.pictogram if self.worksystem and self.worksystem.pictogram else ""}{d}</div>')
    shot_description.fget.short_description = 'Описание заявки'
    
    @property
    def order_date_format(self):
        return self.order_date.strftime("%d.%m.%y") if self.order_date else "--"
    #order_date_format.admin_order_field = 'order_date'
    order_date_format.fget.short_description = 'Дата заявки'

    @property
    def creation_date_time_format(self):
        creation_date = timezone.localtime(self.creation_date)
        return format_html(f'<div>{creation_date.strftime("%d.%m.%y")}</div><div style="font-size: 12px">{creation_date.strftime("%H:%M")}</div>')
    #creation_date_time_format.admin_order_field = 'order_date'
    creation_date_time_format.fget.short_description = 'Дата заявки'

    #def dolg(self):
    #    return "Найдена задолженность"
    #dolg.fget.short_description = 'Задолженность'
#
    #def building_description(self):
    #    if self.building:
    #         return format_html(f"<div><b>{self.building.company}</b><br>{self.building.description}<br><br>{self.building.comment}</div>")
    #    else:
    #        return format_html(f'<div><b>Объект не найден</b></div>')
    #building_description.short_description = 'Описание объекта'
#
    #def history(self):
    #    return format_html('<div id="hist" class="button" style="width:120px">Получить историю</div><div id="hist-table"></div>')
    #history.short_description = 'История'
    #
    #def workschedule(self):
    #    return format_html('<div id="workschedule" class="button" style="width:120px">Получить график</div><div id="workschedule-table"></div>')
    #workschedule.short_description = 'График исполнителя'
    
    @property
    def plan_date_format(self):
        pt=""
        #if self.plan_text:
        #    pt = f'<br><span style="font-size:12px">{self.plan_text}</span>'
        if self.plan_date:
            pd = self.plan_date.strftime("%d.%m.%y")
        else:
            pd = "-"
        if self.plan_period == 'until':
            pd = '🕘'+pd
        if self.plan_period == 'after':
            pd = pd+'🕞'
        if self.plan_period == 'during':
            pd = pd

        
        #cp = OrderUpdate.objects.filter(order = obj, update_type = 'plan').count()
        #if cp > 0:
        #    return format_html(f'<span style="white-space: nowrap;">{pd}</span><span>🔄{cp}</span>{pt}')
        #else:
        return format_html(f'<span style="white-space: nowrap;">{pd}</span>{pt}')

    #plan_date_format.admin_order_field = 'plan_date'
    plan_date_format.fget.short_description = 'Дата план'
    #def form_valid(self, form):
    #    form.instance.author = self.request.user
      

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return '№'+str(self.number)+' от '+self.order_date.strftime("%d.%m.%Y") if self.order_date else "--"

#class Debt(models.Model):
#    on_the_date = models.DateField(null=True, blank=True, default=None, verbose_name = 'На дату')
#    citizen = models.CharField(max_length=50,null=True, blank=True, default=None, verbose_name='ФИО')
#    street = models.ForeignKey(Street, on_delete=models.DO_NOTHING, verbose_name = 'Улица')
#    house = models.CharField(max_length=15, verbose_name='Дом')
#    flat = models.CharField(max_length=15, verbose_name='Квартира')
#    debt_value = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, verbose_name='Сумма задолженности')
#    class Meta:
#        verbose_name = "Задолженность"
#        verbose_name_plural = "Задолженности"

class FotosInOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name = 'Заявка')
    name = models.CharField(max_length=150, blank=True, null = True, default=None, verbose_name='Описание')
    foto = models.ImageField(blank=True, null = True, default=None, verbose_name='Фото', upload_to = "fotos/")
    max_token = models.CharField(max_length=200, null = True, default=None, blank=True)
    max_url = models.URLField(max_length=500, null = True, default=None, blank=True)
    
    @property
    def admin_image(self):
        from django.utils.safestring import mark_safe
        return mark_safe('<a href="{url}" target="_blank"><img src="{url}" width="{width}" height={height} /></a>'.format(
            url = '/media/'+str(self.foto) if self.foto else self.max_url,
            width=60,
            height=40,
            )
        )   
    admin_image.fget.short_description = 'Предпросмотр'            

    @property
    def preview_image(self):
        from django.utils.safestring import mark_safe
        return mark_safe('<a href="{url}" target="_blank"><img src="{url}" width="{width}" height={height} /></a>'.format(
            url = '/media/'+str(self.foto) if self.foto else self.max_url,
            width=60,
            height=40,
            )
        )   
    admin_image.fget.short_description = 'Предпросмотр'            


    class Meta:
        verbose_name = "Фото в заявке"
        verbose_name_plural = "Фото в заявке"
    def __str__(self):
        return str(self.id)

class Numbering(models.Model):
    suffix = models.CharField(max_length=5, default=None, null=True, blank=True, verbose_name="Суффикс")
    prefix = models.CharField(max_length=5, default=None, null=True, blank=True, verbose_name="Префикс")
    current_number = models.IntegerField(default=1, verbose_name="Текущий номер")
    district = models.ForeignKey(District, on_delete=models.CASCADE, verbose_name="Участок")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=None, null=True, blank=True, verbose_name="Компания")
    class Meta:
        verbose_name = "Нумерация"
        verbose_name_plural = "Нумерация"

class DistrictInBuilding(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания")
    building = models.ManyToManyField(Building, verbose_name = 'Объекты')
    district = models.ForeignKey(District, on_delete=models.CASCADE, verbose_name = 'Участок')

    class Meta:
        verbose_name = "Закрепление участков УК за домами"
        verbose_name_plural = "Закрепление участков УК за домами"


class WorkSystemInBuilding(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания")
    building = models.ManyToManyField(Building, default=None, null=True, blank=True, verbose_name = 'Объект')
    worksystem = models.ManyToManyField(WorkSystem, verbose_name = 'Рабочая система')
    company_exec = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания", related_name='company_exec_building')

    @property
    def get_buildings(self):
        return "; ".join([e.name for e in self.building.all()])
    get_buildings.fget.short_description = 'Объекты'

    @property
    def get_worksystems(self):
        return "; ".join([e.name for e in self.worksystem.all()])
    get_worksystems.fget.short_description = 'Рабочие системы'


    class Meta:
        verbose_name = "Закрепления подрядчика за объектами"
        verbose_name_plural = "Закрепления подрядчика за объектами"


#class OrderReport(models.Model):
#    ORDER_STATE = [('accepted','Только НЕвыполненные'),('completed','Только выполненные'),('tocheck','Проверить'),('overdue','Просроченные'),]
#    FORMAT_TYPES = [('pdf','pdf'),('xlsx','xlsx'),]
#    #ORDER_TYPE = [('maintenance,repairs','Содержание+Текущий ремонт'),('paid','Платная')]
#    ORDER_TYPE = [('houses','Общедомовые'),('flats','Поквартирные'),('houses,flats','Общедомовые+Поквартирные'),('paid','Платная'),('repair','Текущий ремонт'),('household','Хознужды'),('emergency','Аварийная')]
#    author = models.ForeignKey(User, default = 1, on_delete=models.CASCADE, verbose_name = 'Автор')
#    name = models.CharField(max_length=50, null=True, blank=True, default=None, verbose_name = 'Название')
#    format_type = models.CharField(max_length=10, default='pdf', verbose_name = 'Тип',choices = FORMAT_TYPES)
#    
#    state = models.CharField(max_length=20, null=True, blank=True, default=None, verbose_name = 'Состояние', choices = ORDER_STATE)
#    ordertype = models.CharField(max_length=30, null=True, blank=True, default=None, verbose_name = 'Тип', choices=ORDER_TYPE)
#    district = models.ManyToManyField(District, blank=True, default=None, verbose_name = 'Участок')
#    worksystem = models.ManyToManyField(WorkSystem, blank=True, default=None, verbose_name = 'Система')
#    employee = models.ManyToManyField(Employee, blank=True, default=None, verbose_name = 'Сотрудник')
#    date_at = models.DateTimeField(null=True, blank=True, default=None, verbose_name = 'Дата заявки от')
#    date_to = models.DateTimeField(null=True, blank=True, default=None, verbose_name = 'Дата заявки до')
#    plan_at = models.DateField(null=True, blank=True, default=None, verbose_name = 'Дата план от')
#    plan_to = models.DateField(null=True, blank=True, default=None, verbose_name = 'Дата план до')
#    fact_at = models.DateField(null=True, blank=True, default=None, verbose_name = 'Дата факт от')
#    fact_to = models.DateField(null=True, blank=True, default=None, verbose_name = 'Дата факт до')
#
#    building = models.ManyToManyField(Building, blank=True, default=None, verbose_name = 'Объекты')
#    flat = models.CharField(max_length=50, null=True, blank=True, default=None, verbose_name = 'Квартира')
#    description = models.CharField(max_length=100, null=True, blank=True, default=None, verbose_name = 'Описание заявки')
#    fact_description = models.CharField(max_length=100, null=True, blank=True, default=None, verbose_name = 'Фактическое описание')
#    company = models.ManyToManyField(Company, blank=True, default=None, verbose_name = 'Компании')
#    class Meta:
#        verbose_name = "Журнал заявок"
#        verbose_name_plural = "Журнал заявок"
#
#
##class Pinning(models.Model):
##    street = models.ForeignKey(Street, on_delete=models.DO_NOTHING, verbose_name = 'Улица')
##    houses = models.CharField(max_length=100, verbose_name='Дома')
#    worksystem = models.ForeignKey(WorkSystem, on_delete=models.DO_NOTHING, verbose_name = 'Рабочая система')
#    employee = models.ManyToManyField(Employee, verbose_name='Исполнитель')
#    class Meta:
#        verbose_name = "Закрепления исполнителей"
#        verbose_name_plural = "Закрепления исполнителей"
#


class Disconnect(models.Model):
    DISCONNECTS_TYPES = [('Отключение','Отключение'),('Аварийное','Аварийное'),('Ухудшение','Ухудшение'),('Информация','Информация'),]
    SOURCE = [('Входящее','Входящее'),('Исходящее','Исходящее'),('Внутренее','Внутренее'),] 

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = 'Автор')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name = 'Дата создания')
    number = models.CharField(max_length=15, null=True, blank=True, default=None, verbose_name='Номер')
    start_disconnect = models.DateTimeField(verbose_name='Дата начала отключения')
    plan_connection_date = models.DateTimeField(verbose_name='Плановая дата подключения') #null=True, blank=True, default=None,
    fact_connection_date = models.DateTimeField(null=True, blank=True, default=None, verbose_name='Фактическая дата подключения')
    building = models.ManyToManyField(Building, null=True, blank=True, default=None, verbose_name = 'Объекты')
    worksystem = models.ManyToManyField(WorkSystem, null=False, blank=False, default=None, verbose_name = 'Рабочая система')
    description = models.TextField(max_length=500, null=True, blank=True, default=None, verbose_name='Описание')
    connected = models.BooleanField(default=False, verbose_name='Подключено?')

    sender = models.CharField(max_length=150, null=True, blank=True, default=None, verbose_name='Ответственный от подрятчика')
    disconnection_type = models.CharField(max_length=50, null=True, blank=True, default='Отключение', choices=DISCONNECTS_TYPES, verbose_name='Тип')
    source = models.CharField(max_length=50, null=True, blank=True, default='Входящее', choices=SOURCE, verbose_name='Источник')
    published = models.BooleanField(default=False, verbose_name="Опубликовать")

    company_owner = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name='УК', related_name='disc_company_owner')
    company_exec = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name='Подрядчик', related_name='disc_company_exec')

    data = models.JSONField(null=True, blank=True, default=None)


    class Meta:
        verbose_name = "Отключение"
        verbose_name_plural = "Отключения"
    
    @property
    def get_buildings_text(self):
        return ";\n".join([b.name for b in self.building.all()])
    
    @property
    def get_worksystem_text(self):
        return ",\n".join([ws.name for ws in self.worksystem.all()])
    get_worksystem_text.fget.short_description = 'Система'   

    @property
    def get_period(self):
        return format_html(f'<span style="font-size:12px;white-space: nowrap;">{timezone.localtime(self.start_disconnect).strftime("%d.%m.%Y %H:%M")}</span><br><span style="font-size:12px;white-space: nowrap;">{timezone.localtime(self.plan_connection_date).strftime("%d.%m.%Y %H:%M") if self.plan_connection_date else "--"}</span>')
    get_period.fget.short_description = 'Период'   



    def __str__(self):
        return '№'+str(self.number)+' от '+self.start_disconnect.strftime("%d.%m.%Y")
