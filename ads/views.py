
from re import search
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ads.models import Disconnect, DistrictInBuilding, Numbering, Order, OrderState, WorkSystemInBuilding
from ads.forms import DisconnectForm, FotoInOrderFormSet, OrderCloseForm, OrderForm, FotoInOrderForm
from django.urls import reverse_lazy
from django.utils import timezone
import datetime
from django.http import JsonResponse, FileResponse, HttpResponse, StreamingHttpResponse
import json
from dict.models import Building, Company, Employee, StandardDescription, Street, StreetInCompany, WorkSystem
from django.views.decorators.http import require_POST
from ads.reports.jobs import jobs_report
from ads.reports.jobs_short import jobs_report as jobs_short
from ads.reports.disconnect_list import generate_disconnects
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import requests



class OrderListView(LoginRequiredMixin, ListView):
    login_url = '/login' 
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'
    ordering = ['-id']  # Сначала новые
    paginate_by = 100 

    def get_queryset(self):
        qs = super().get_queryset()
        employee_obj = Employee.objects.get(user = self.request.user)
        if employee_obj.company.company_type == 'ук':
            qs = qs.filter(company_owner = employee_obj.company)

        
        if employee_obj.company.company_type == 'подряд':
            qs = qs.filter(company_exec = employee_obj.company)


        if employee_obj.post == 'master':
            qs = qs.filter(Q(worksystem__in = employee_obj.worksystem.all()) | Q(master = employee_obj))
        if employee_obj.post == 'worker':
            qs = qs.filter(employee = employee_obj)

        
        #TODO фильтрация в зависимости от должности и типа компаныии (УК, подрядчик)
        
        
        
        search = self.request.GET.get('search') if 'search' in self.request.GET else None
        order_date_at = self.request.GET.get('order_date_at', None) if 'order_date_at' in self.request.GET else None
        order_date_to = self.request.GET.get('order_date_to', None) if 'order_date_at' in self.request.GET else None
        order_state = self.request.GET.get('order_state', None) if 'order_state' in self.request.GET else None
        company_exec = self.request.GET.get('company_exec', None) if 'company_exec' in self.request.GET else None
        worksystem_filter = self.request.GET.get('worksystem_filter', None) if 'worksystem_filter' in self.request.GET else None

        if order_date_at:
            qs = qs.filter(order_date__gte = order_date_at)
        if order_date_to:
            qs = qs.filter(order_date__lte = order_date_to)
        if order_state:
            qs = qs.filter(state = order_state)
        if company_exec:
            qs = qs.filter(company_exec = Company.objects.get(pk = company_exec))

        if search:
            q = search.split(' ')
            if len(q) == 1:
                qs = qs.filter(Q(description__icontains = q[0]) | Q(number=q[0]) | Q(citizen__icontains = q[0]) | Q(phone__icontains = q[0]))
            if len(q) == 2:
                qs = qs.filter(street__name__icontains = q[0], house = q[1])
            if len(q) == 3:
                qs = qs.filter(street__name__icontains = q[0], house = q[1], flat = q[2])
        if worksystem_filter:
            qs = qs.filter(worksystem_id__in = worksystem_filter)
 
        return qs
        #return qs.filter(company_owner= employee_obj.company)

    def get_context_data(self, **kwargs):
        # 1. Получаем базовый контекст от родительского класса
        context = super().get_context_data(**kwargs)
        employee_obj = Employee.objects.get(user = self.request.user)
        # 2. Добавляем новые данные
        context['company_exec_list'] = Company.objects.filter(pk__in = WorkSystemInBuilding.objects.filter(company = employee_obj.company).values('company_exec'))
        context['order_state_list'] = OrderState.objects.all()
        context['worksystem_list'] = WorkSystem.objects.filter(is_used = 1)
        # 3. Возвращаем обновленный словарь контекста
        return context


# 2. Создание заявки
class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'order_form.html'
    success_url = reverse_lazy('order_list')
    
    def get_initial(self):
        # 1. Получаем базовый словарь начальных значений
        initial = super().get_initial()   
        initial['order_date'] = timezone.now().date()
        initial['plan_date'] = timezone.now().date() + datetime.timedelta(days=1)
        # 2. Извлекаем GET-параметр (например, 'company_id') из URL
        #deal_id = self.request.GET.get('deal')
        ## 3. Если параметр передан, устанавливаем его как значение по умолчанию для поля
        #if deal_id:
        #    deal_obj = Deal.objects.get(pk = deal_id)
        #    initial['deal'] = deal_id
        #    initial['company'] = deal_obj.company
        #    initial['point'] = deal_obj.point
        
            
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        employee_obj = Employee.objects.get(user = self.request.user)
        #profile = Profile.objects.get(user = self.request.user)
        ## Пример 1: Фильтрация по фиксированному условию (например, только активные компании)
        form.fields['street'].queryset = Street.objects.filter(pk__in = StreetInCompany.objects.filter(company = employee_obj.company).values('street'))
        form.fields['building'].queryset = Building.objects.filter(company = employee_obj.company)
        #все подрядчики УК
        company_list = Company.objects.filter(pk__in = WorkSystemInBuilding.objects.filter(company = employee_obj.company).values('company_exec'))
        form.fields['company_exec'].queryset = company_list
        #фильтрация сотрудников
        if employee_obj.company.company_type == 'ук':
            employee_list = Employee.objects.filter(post__in = ['worker','master'], deleted = False)
            form.fields['employee'].queryset = employee_list.filter(Q(company__in = company_list) | Q(company = employee_obj.company))
            form.fields['master'].queryset = employee_list.filter(Q(company__in = company_list) | Q(company = employee_obj.company), post = 'master')
        #
        ## Пример 2: Фильтрация на основе текущего пользователя (если у компании есть связь с юзером)
        ## if self.request.user.is_authenticated:
        ##     form.fields['company'].queryset = Company.objects.filter(owner=self.request.user)
            
        return form

    def form_valid(self, form):
        # Автоматически назначаем текущего пользователя автором, если он авторизован
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        #TODO добавить учет parent_id and (obj.parent is None)

        if form.instance.building is None:
            building_obj = Building.objects.filter(street = form.instance.street, house = form.instance.house)
            if building_obj:
                building_obj = building_obj.first()
                form.instance.building = building_obj
                form.instance.company_owner = building_obj.company
                district_obj = DistrictInBuilding.objects.filter(company = building_obj.company, building = building_obj)
                if district_obj:
                    district_obj = district_obj.first()
                    form.instance.district = district_obj.district

        if (form.instance.number is None) and (form.instance.district):
            n = Numbering.objects.filter(district = form.instance.district)
            if n:
                prefix = "" if n[0].prefix is None else n[0].prefix
                suffix = "" if n[0].suffix is None else n[0].suffix
                form.instance.number = prefix+str(n[0].current_number)+suffix
                Numbering.objects.filter(district=form.instance.district).update(current_number=n[0].current_number+1)

        #if form.instance.district is None:
        #    employee = Employee.objects.get(user=request.user)
        #    
        #    if building:
        #        obj.district = building[0].district
        #        obj.company = building[0].company
        #    else:
        #        if employee: #выставить участок по умолчанию от участка автора
        #            obj.district = employee.district.first()

            
            #profile = Profile.objects.get(user = self.request.user)
            #form.instance.project = profile.project
        return super().form_valid(form)


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'order_form.html'
    success_url = reverse_lazy('order_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        employee_obj = Employee.objects.get(user = self.request.user)
        form.fields['street'].queryset = Street.objects.filter(pk__in = StreetInCompany.objects.filter(company = employee_obj.company).values('street'))
        form.fields['building'].queryset = Building.objects.filter(company = employee_obj.company)
        #все подрядчики УК
        company_list = Company.objects.filter(pk__in = WorkSystemInBuilding.objects.filter(company = employee_obj.company).values('company_exec'))
        form.fields['company_exec'].queryset = company_list
        #фильтрация сотрудников
        if employee_obj.company.company_type == 'ук':
            employee_list = Employee.objects.filter(post__in = ['worker','master'], deleted = False)
            form.fields['employee'].queryset = employee_list.filter(Q(company__in = company_list) | Q(company = employee_obj.company))
            form.fields['master'].queryset = employee_list.filter(Q(company__in = company_list) | Q(company = employee_obj.company), post = 'master')
            
        return form

class OrderCloseView(UpdateView):
    model = Order
    form_class = OrderCloseForm
    template_name = 'order_close_form.html'
    success_url = reverse_lazy('order_list')
    
    def get_initial(self):
        # 1. Получаем базовый словарь начальных значений
        initial = super().get_initial()   
        order = self.get_object()
        # Если в базе данных fact_date не заполнено (None), задаем текущую дату
        if not order.fact_date:
            initial['fact_date'] = timezone.now()
        
        initial['state'] = 'completed'
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
            
        return form





class FotoInOrderUpdateView(UpdateView):
    model = Order
    form_class = FotoInOrderForm
    template_name = 'order_foto_form.html'
    success_url = reverse_lazy('order_list')

    def get_context_data(self, **kwargs):
        # Добавляем формсет в контекст шаблона
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = FotoInOrderFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['formset'] = FotoInOrderFormSet(instance=self.object)
        return data


    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        # Оборачиваем в транзакцию: если упадет формсет, родитель тоже не сохранится
        with transaction.atomic():
            self.object = form.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                # Если формсет невалиден, заново рендерим форму с ошибками
                return self.form_invalid(form)
                
        return super().form_valid(form)

def reports(request):
    if request.method == 'POST':
        order_date_at = request.POST.get('order_date_at', None) if 'order_date_at' in request.POST else None
        order_date_to = request.POST.get('order_date_to', None) if 'order_date_at' in request.POST else None
        order_state = request.POST.get('order_state', None) if 'order_state' in request.POST else None
        company_exec = request.POST.get('company_exec', None) if 'company_exec' in request.POST else None

        employee_obj = Employee.objects.get(user = request.user)

        qs = Order.objects.filter(company_owner = employee_obj.company)
        if order_date_at:
            qs = qs.filter(order_date__gte = order_date_at)
        if order_date_to:
            qs = qs.filter(order_date__lte = order_date_to)
        if order_state:
            qs = qs.filter(state = order_state)
        if company_exec:
            qs = qs.filter(company_exec = Company.objects.get(pk = company_exec))
        qs = qs[:1000]
        from .reports.order_list import order_list2
        buffer = order_list2(qs)
        return StreamingHttpResponse(buffer, content_type="application/pdf")   

    context = {}
    return render(request, 'reports.html', context)



def get_address_from_phone(request):
    phone = request.GET.get('phone')
    order = Order.objects.filter(phone__contains = phone).order_by("-id").first()
    data = {'result':0, 'debt':0}
    if order:
        data = {'result':1, 'debt':0, 'street_id': order.street_id, 'street_name': order.street.name, 'house': order.house, 'flat': order.flat, 'entrance': order.entrance,
            'floor': order.floor, 'citizen': order.citizen}

        #d = Debt.objects.filter(street = order.street, house = order.house, flat = order.flat).first()
        #if d:
        #    data['debt'] = int(d.debt_value)

    return HttpResponse(json.dumps(data, indent = 4))
    return JsonResponse(data)

def get_company_exec(request):
    street_id = request.GET.get('street_id')
    house = request.GET.get('house')
    worksystem_id = request.GET.get('worksystem_id')
    data = {'result': 1}
    building_obj = Building.objects.filter(street = Street.objects.get(pk = street_id), house = house)
    if building_obj:
        building_obj = building_obj.first()
        company_exec_obj = WorkSystemInBuilding.objects.filter(building = building_obj, worksystem = WorkSystem.objects.get(pk = worksystem_id))
        if company_exec_obj:
            company_exec_obj = company_exec_obj.first()
            data['company_exec'] = company_exec_obj.company_exec.id
    
    sds = StandardDescription.objects.filter(worksystem_id = worksystem_id)
    s = []
    for sd in sds:
        s.append(sd.name)
    data['standart_description'] = s

    return HttpResponse(json.dumps(data, indent = 4))

def get_orders_history(request):
    street_id = request.GET.get('street_id')
    house = request.GET.get('house')
    flat = request.GET.get('flat')
    if street_id and house and flat:
        orders = Order.objects.filter(street_id = street_id, house = house, flat = flat).order_by("-id")[:10]
        html = '<table class="table table-hover table-striped align-middle m-0 w-100 table-sm"><tr><th>Номер</th><th>Дата заявки</th><th>Состояние</th><th>Заявитель</th><th>Телефон</th><th>Описание</th><th>Дата выполнения</th><th>Выполненные работы</th></tr>'
        for o in orders:
            order_date = o.order_date.strftime("%d.%m.%Y")
            fact_date = o.fact_date.strftime("%d.%m.%Y %H:%M") if o.fact_date else ""
            html = html + f'<tr><td>{o.number}</td><td>{order_date}</td><td>{o.colored_state}</td><td>{o.citizen}</td><td>{o.phone}</td><td>{o.description}</td><td>{fact_date}</td><td>{o.fact_description if o.fact_description else "--"}</td></tr>'
        html = html + '</table>'
    else:
        html = 'история с данного адреса недоступна'   
    return HttpResponse(html)







@require_POST
def print(request):
    try:
        # Декодируем JSON из тела запроса
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        if not ids:
            return JsonResponse({'status': 'error', 'message': 'Список ID пуст'}, status=400)
        
        orders_list = Order.objects.filter(id__in=ids)
        buffer = jobs_short(orders_list)
        #buffer = jobs_report(orders_list)
        return StreamingHttpResponse(buffer, content_type="application/pdf")
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
def print_disconnect(request):
    
    try:
        # Декодируем JSON из тела запроса
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        if not ids:
            return JsonResponse({'status': 'error', 'message': 'Список ID пуст'}, status=400)
        
        disconnect_list = Disconnect.objects.filter(id__in=ids)
        buffer = generate_disconnects(disconnect_list)
        #buffer = jobs_report(orders_list)
        return StreamingHttpResponse(buffer, content_type="application/pdf")
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


#=============================ОТКЛЮЧЕНИЯ==========================================

class DisconnectListView(LoginRequiredMixin, ListView):
    login_url = '/login' 
    model = Disconnect
    template_name = 'disconnect_list.html'
    context_object_name = 'disconnects'
    ordering = ['-id']  # Сначала новые
    paginate_by = 100 

    def get_queryset(self):
        qs = super().get_queryset()
        employee_obj = Employee.objects.get(user = self.request.user)
        qs = qs.filter(company_owner = employee_obj.company)

        disconnect_date_at = self.request.GET.get('disconnect_date_at', None) if 'disconnect_date_at' in self.request.GET else None
        disconnect_date_to = self.request.GET.get('disconnect_date_to', None) if 'disconnect_date_to' in self.request.GET else None
        disconnect_plan_date_at = self.request.GET.get('disconnect_plan_date_at', None) 
        disconnect_plan_date_to = self.request.GET.get('disconnect_plan_date_to', None) 
        disconnect_fact_date_at = self.request.GET.get('disconnect_fact_date_at', None)
        disconnect_fact_date_to = self.request.GET.get('disconnect_fact_date_to ', None)

        disconnect_state = self.request.GET.get('disconnect_state', None) if 'disconnect_state' in self.request.GET else None
        company_exec = self.request.GET.get('company_exec', None) if 'company_exec' in self.request.GET else None
        
        if disconnect_date_at:
            qs = qs.filter(start_disconnect__gte = disconnect_date_at)
        if disconnect_date_to:
            qs = qs.filter(start_disconnect__lte = disconnect_date_to)
        if disconnect_plan_date_at:
            qs = qs.filter(plan_connection_date__gte = disconnect_plan_date_at)
        if disconnect_plan_date_to:
            qs = qs.filter(plan_connection_date__lte = disconnect_plan_date_to)
        if disconnect_fact_date_at:
            qs = qs.filter(fact_connection_date__gte = disconnect_fact_date_at)
        if disconnect_fact_date_to:
            qs = qs.filter(fact_connection_date__lte = disconnect_fact_date_to)
        if disconnect_state:
            qs = qs.filter(connected = disconnect_state)
        if company_exec:
            qs = qs.filter(company_exec = Company.objects.get(pk = company_exec))
        return qs
        #return qs.filter(company_owner= employee_obj.company)

    def get_context_data(self, **kwargs):
        # 1. Получаем базовый контекст от родительского класса
        context = super().get_context_data(**kwargs)
        employee_obj = Employee.objects.get(user = self.request.user)
        # 2. Добавляем новые данные
        context['company_exec_list'] = Company.objects.all()
        #context['company_exec_list'] = Company.objects.filter(pk__in = WorkSystemInBuilding.objects.filter(company = employee_obj.company).values('company_exec'))
        # 3. Возвращаем обновленный словарь контекста
        return context

class DisconnectCreateView(CreateView):
    model = Disconnect
    form_class = DisconnectForm
    template_name = 'disconnect_form.html'
    success_url = reverse_lazy('disconnect_list')
    
    def get_initial(self):
        # 1. Получаем базовый словарь начальных значений
        initial = super().get_initial()   
        initial['start_disconnect'] = timezone.now()        
            
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        employee_obj = Employee.objects.get(user = self.request.user)        
        form.fields['building'].queryset = Building.objects.filter(company = employee_obj.company)
        form.fields['company_exec'].queryset = Company.objects.all()
        return form

    def form_valid(self, form):
        # Автоматически назначаем текущего пользователя автором, если он авторизован
        form.instance.author = self.request.user
        employee = Employee.objects.get(user=self.request.user)
        form.instance.company_owner = employee.company

        response = super().form_valid(form)

        if form.instance.published and form.instance.data is None and form.instance.disconnection_type in ('Ухудшение','Аварийное','Отключение'):
            if form.instance.disconnection_type == 'Ухудшение':
                txt = f'Уважаемые жители! В вашем доме будет ухудшенный режим подачи {form.instance.get_worksystem_text} в период с {form.instance.start_disconnect.strftime("%d.%m.%Y %H:%M")} по {form.instance.plan_connection_date.strftime("%d.%m.%Y %H:%M")} в связи с плановыми ремонтными работами. '
            if form.instance.disconnection_type == 'Аварийное':
                txt = f'Уважаемые жители! В вашем доме будет отсутствовать {form.instance.get_worksystem_text} в период с {form.instance.start_disconnect.strftime("%d.%m.%Y %H:%M")} по {form.instance.plan_connection_date.strftime("%d.%m.%Y %H:%M")} в связи с проведением аварийно-восстановительных работ. '
            if form.instance.disconnection_type == 'Отключение':
                txt = f'Уважаемые жители! В вашем доме будет отсутствовать {form.instance.get_worksystem_text} в период с {form.instance.start_disconnect.strftime("%d.%m.%Y %H:%M")} по {form.instance.plan_connection_date.strftime("%d.%m.%Y %H:%M")} в связи c плановыми ремонтными работами. '
            if form.instance.company_exec:
                txt = txt+ f"Работы производит {form.instance.company_exec}. "
            if form.instance.description:
                txt = txt + f"({form.instance.description})"
            data = []

            for b in form.instance.building.all():
                TOKEN = "f9LHodD0cOJ5ySMLDgmGAlGxOpYdKKSRsla7fydwq93KoGp7mfwTo2kwpdqAHQGX9Sdi17Stz7WDkJdKMLPL" #мой бот 
                if b.channelid:
                    header= {'Authorization': TOKEN, 'Content-Type': 'application/json'}
                    body = {"text": txt}
                    host = f"https://platform-api.max.ru/messages?chat_id={b.channelid}"
                    r = requests.post(host ,json=body, headers=header)
                    data.append(r.json())
                Disconnect.objects.filter(pk = form.instance.id).update(data = data)

        return response

class DisconnectUpdateView(UpdateView):
    model = Disconnect
    form_class = DisconnectForm
    template_name = 'disconnect_form.html'
    success_url = reverse_lazy('disconnect_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        employee_obj = Employee.objects.get(user = self.request.user)
        form.fields['building'].queryset = Building.objects.filter(company = employee_obj.company)
        form.fields['company_exec'].queryset = Company.objects.all()
        #фильтрация сотрудников
        #if employee_obj.company.company_type == 'ук':
        #    employee_list = Employee.objects.filter(post__in = ['worker','master'])
        #    form.fields['employee'].queryset = employee_list.filter(Q(company__in = WorkSystemInBuilding.objects.filter(company = employee_obj.company).values('company_exec')) | Q(company = employee_obj.company))
        #    form.fields['master'].queryset = employee_list.filter(post = 'master')
        #form.fields['point'].queryset = Point.objects.filter(pk__in = profile.point.all())
        #form.fields['deal'].queryset = Deal.objects.filter(point__in = profile.point.all()).order_by("-id")
        ## Пример 2: Фильтрация на основе текущего пользователя (если у компании есть связь с юзером)
        ## if self.request.user.is_authenticated:
        ##     form.fields['company'].queryset = Company.objects.filter(owner=self.request.user)
            
        return form
