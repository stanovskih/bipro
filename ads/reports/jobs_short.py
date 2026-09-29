from datetime import datetime

from time import sleep

from fpdf import FPDF, HTMLMixin
import io
from django.db import connection
from  django.utils import timezone
from ads.models import Employee

def is_None(s):
    if s is None:
        return "-"
    else:
        return s

def jobs_report(qs):
    pdf = FPDF()
    #pdf = FPDF('L')
    pdf.add_page()
    pdf.add_font("Arial", "", "static/arial.ttf", uni=True)
    pdf.add_font("Arial", "B", "static/arial_b.ttf", uni=True)

    p = 0

    pdf.set_margins(10, 10, -1)
    for q in qs:
        q.last_printed_date = timezone.now()
        q.save()
        creation_date = timezone.localtime(q.creation_date)
        cd = creation_date.strftime("%d.%m.%Y")
        pd = q.plan_date.strftime("%d.%m.%Y") if q.plan_date else ""
        
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(22,5,f"{q.get_priority_display() if q.priority in ('emergency','urgent') else ''} {' Платная' if q.ordertype == 'paid' else ''}", align="L", ln=0)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(140,5,f"НАРЯД-ЗАДАНИЕ №{q.number} ({str(q.id)}) от {cd}", align="C", ln=0)
        
        pdf.set_font("Arial", '', size=12)
        pdf.cell(30,5, f'{q.company_exec.legal_name if q.company_exec else ""}', align="R", border=0, ln=1)
        pdf.cell(0,5, f'тел:{q.company_exec.phone if q.company_exec else ""}', align="R", border=0, ln=1)
        
        pdf.cell(95,6,f"Диспетчер: {Employee.objects.get(user=q.author).name}", border=1, ln=0)
        pdf.cell(95,6,f"Срок: {pd}, {q.get_plan_period_display()}", border=1, ln=1)
        pdf.set_font("Arial", '', size=10)
        pdf.multi_cell(95,6,f"Заявитель: {q.citizen if q.citizen else '--'} {q.phone}", border=1, new_y="TOP")
        pdf.multi_cell(95,6,f"Адрес: {q.street.name} д.{q.house} кв.{is_None(q.flat)} п.{is_None(q.entrance)} этаж.{is_None(q.floor)}", border=1, new_y="NEXT", new_x="LEFT")
        pdf.set_font("Arial", '', size=12)
        if pdf.get_string_width(f"Заявитель: {q.citizen if q.citizen else '--'} {q.phone}") > 95:
            pdf.ln()
        else:
            pdf.set_x(10)
        
        
        pdf.set_font("Arial", 'B', size=12)
        workers = "; ".join([w.name for w in q.employee.all()])
        #pdf.multi_cell(0,6,f"Исполнитель: {workers}", border=1, ln=1)
        pdf.multi_cell(0,6,f"Исполнитель: {q.get_employees}", border=1, ln=1)
        
        pdf.set_font("Arial", '', size=12)
        descr = f"Описание заявки: {q.worksystem.name} | {q.description}" if q.worksystem else f"Описание заявки: {q.description}"    
        pdf.multi_cell(0,6, txt = descr, border=1, ln=1)
        if q.fact_description:
            pdf.multi_cell(0,6, txt = f'Выполненные работы: {q.fact_description}', border=1, new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.multi_cell(0,6, txt = 'Выполненные работы: \n\n', border=1)
            pdf.set_y(pdf.get_y()-6)
        
        pdf.multi_cell(0,6, txt = 'Израсходованные материалы: \n\n', border=1)
        
        
        pdf.cell(0,5,f"Фактическое выполнение работ на объекте с  ___:___ до ___:___ «___»__________ 20___", border=0, ln=1)
        pdf.cell(100,10,f"Претензий к объему и качеству выполненных работ не имею:", border=0, align="L", ln=0)
        pdf.cell(90,10,f"__________________________", border=0, align="R", ln=1)
        pdf.set_font("Arial", '', size=8)
        pdf.set_y(pdf.get_y()-3)
        pdf.cell(0,3,f"подпись заявителя/расшифровка/           ", border=0, align="R", ln=1)
        pdf.ln(3)
        pdf.cell(0,3,f"", border="T", ln=1)

        p += 1
        if p == 3:
            pdf.add_page()
            p = 0



    return io.BytesIO(pdf.output())
    #return io.BytesIO(bytes(pdf.output(dest = 'S'), encoding='latin1'))
