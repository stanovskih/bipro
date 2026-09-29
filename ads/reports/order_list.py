from datetime import datetime
from fpdf import FPDF, HTMLMixin
import io
from django.db import connection
import math
from  django.utils import timezone


from ads.models import Building, Company, FotosInOrder, Order


def is_None(s):
    if s is None:
        return "-"
    else:
        return s

def order_list(qs):
    q = qs[0]
    #pdf = FPDF()
    pdf = FPDF('L')
    pdf.add_font("Arial", "", "arial.ttf", uni=True)
    pdf.add_font("Arial", "B", "arial_b.ttf", uni=True)

    pdf.set_margins(10, 10, -1)
    #pdf.set_auto_page_break(False, margin = 10)
    pdf.add_page()


    pdf.set_font("Arial", 'B', size=10)
    #pdf.cell(0,5,f"Отчет по заявкам за период с {timezone.localtime(q.date_at).strftime('%d.%m.%Y %H:%M')} по {timezone.localtime(q.date_to).strftime('%d.%m.%Y %H:%M')}", align="C", ln=1)
    pdf.ln()

    total_order_count = 0
    total_total_diff_time = 0
    
    if q.date_at:
        order_list = Order.objects.filter(creation_date__gte = q.date_at, creation_date__lte = q.date_to)
    if q.plan_at:
        order_list = Order.objects.filter(plan_date__gte = q.plan_at, plan_date__lte = q.plan_to)
    if q.building.all():
        order_list = order_list.filter(building__in = q.building.all())
    if q.ordertype:
        order_list = order_list.filter(ordertype = q.ordertype)
    if q.district.all():
        order_list = order_list.filter(district__in = q.district.all())
    if q.company.all():
        order_list = order_list.filter(company__in = q.company.all())
    if q.worksystem.all():
        order_list = order_list.filter(worksystem__in = q.worksystem.all())
    if q.flat:
        order_list = order_list.filter(flat = q.flat)

    order_list = order_list.order_by('creation_date')
    pdf.set_font("Arial", '', size=9)
    max_line_height=pdf.font_size
    total_diff_time = 0
    data = []
    data.append(('№','Дата заявки','Адрес','Заявитель','Рабочая система','Описание', 'Выполненные работы','План','Состояне'))
    for o in order_list:
        creation_date = timezone.localtime(o.creation_date)
        try:
            state = o.state.name
        except:
            state = '-'
        worker = "; ".join([e.name for e in o.employee.all()])
        data.append(
                         (o.number,
                         creation_date.strftime('%d.%m.%Y %H:%M'),
                         f"{o.street}, {o.house}, кв.{o.flat if o.flat else '--'}",
                         f"{o.citizen}, {o.phone}",
                         f"{o.worksystem}",
                         f"{o.description}",
                         f"{o.fact_description[:1500]}",
                         f"{o.plan_date.strftime('%d.%m.%Y') if o.plan_date else '--'} {o.plan_period if o.plan_period else ''} {o.plan_text if o.plan_text else ''}",
                         f"{state} {worker}"
                         )
            )
        
    print(data)

    with pdf.table(col_widths=(10, 20, 30, 20,25,50,70,20,26), line_height=pdf.font_size) as table:
        for data_row in data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)

            
        #pdf.set_font("Arial", 'B', size=10)
        #pdf.cell(0,5,f"Итого {order_list.count()} заявок. Трудозатраты: {int(math.modf(total_diff_time/3600)[1])} ч. {int(math.modf(total_diff_time/3600)[0]*60)} м.",border=1, ln=1)
        #pdf.add_page()


    return io.BytesIO(pdf.output())
    #return io.BytesIO(bytes(pdf.output(dest = 'S'), encoding='latin1'))


def order_list2(qs): 
    #pdf = FPDF()
    pdf = FPDF('L')
    pdf.add_font("Arial", "", "static/arial.ttf", uni=True)
    pdf.add_font("Arial", "B", "static/arial_b.ttf", uni=True)

    pdf.set_margins(10, 10, -1)
    #pdf.set_auto_page_break(False, margin = 10)
    pdf.add_page()


    pdf.set_font("Arial", 'B', size=10)
    #pdf.cell(0,5,f"Отчет по заявкам за период с {timezone.localtime(q.date_at).strftime('%d.%m.%Y %H:%M')} по {timezone.localtime(q.date_to).strftime('%d.%m.%Y %H:%M')}", align="C", ln=1)
    pdf.ln()

    total_order_count = 0
    total_total_diff_time = 0
    

    pdf.set_font("Arial", '', size=9)
    max_line_height=pdf.font_size
    total_diff_time = 0
    data = []
    data.append(('№','Дата заявки','Адрес','Заявитель','Рабочая система','Описание', 'Выполненные работы','План','Состояне'))
    for o in qs:
        creation_date = timezone.localtime(o.creation_date)
        try:
            state = o.state.name
        except:
            state = '-'
        worker = "; ".join([e.name for e in o.employee.all()])
        data.append(
                         (o.number,
                         creation_date.strftime('%d.%m.%Y %H:%M'),
                         f"{o.street}, {o.house}, кв.{o.flat if o.flat else '--'}",
                         f"{o.citizen}, {o.phone}",
                         f"{o.worksystem}",
                         f"{o.description}",
                         f"{o.fact_description[:1500] if o.fact_description else '--'}",
                         f"{o.plan_date.strftime('%d.%m.%Y') if o.plan_date else '--'} {o.plan_period if o.plan_period else ''}",
                         f"{state} {worker}"
                         )
            )
        
    print(data)

    with pdf.table(col_widths=(10, 20, 30, 20,25,50,70,20,26), line_height=pdf.font_size) as table:
        for data_row in data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)

    return io.BytesIO(pdf.output())
    #return io.BytesIO(bytes(pdf.output(dest = 'S'), encoding='latin1'))
