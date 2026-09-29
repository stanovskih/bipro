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
    pdf.add_font("Arial", "", "static/arial.ttf", uni=True)
    pdf.add_font("Arial", "B", "static/arial_b.ttf", uni=True)

    pdf.set_margins(10, 10, -1)
    #pdf.add_page()
    #pdf.set_auto_page_break(False, margin = 0.0)  
    doc = 0 
    for q in qs:
        #Order.objects.filter(pk=q.id).update(last_printed_date = datetime.now())
        #works = WorksInOrder.objects.filter(order = q)
        doc = doc+1
        if doc % 2 !=0:
            pdf.add_page()
            pdf.set_auto_page_break(False, margin = 0.0)


        x1 = pdf.get_x()
        y1 = pdf.get_y()
        
        #border="TL"
        creation_date = timezone.localtime(q.creation_date)
        cd = creation_date.strftime("%d.%m.%Y %H:%M")
        pd = q.plan_date.strftime("%d.%m.%Y") if q.plan_date else ""
        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(130,5,f"РАСПОРЯЖЕНИЕ-НАПРАВЛЕНИЕ №{q.number} ({str(q.id)}) от {cd}", align="C", ln=0)
        pdf.set_font("Arial", '', size=10)
        
        pdf.cell(60,5, q.company_owner.legal_name if q.company_owner else "--", align="R", border=0,ln=1)
        
        pdf.cell(130,5, f"на ликвидацию аварии(неисправности)", border=0,align="C", ln=0)
        pdf.cell(60,5, f"тел: {q.company_owner.phone}", align="R",border=0, ln=1)
        pdf.ln(5)
        
        pdf.multi_cell(0,4,f"Адрес: {q.street.name} д.{q.house} кв.{is_None(q.flat)} п.{is_None(q.entrance)} этаж.{is_None(q.floor)} ({q.building.description if q.building else '--'})", border=0, ln=1)
        
        pdf.cell(65,5,f"Заявитель: {q.citizen}", border=0, ln=0)
        pdf.cell(65,5,f"Тел: {q.phone}", border=0, ln=1)
        
        pdf.cell(65,5,f"УК, ТСЖ: {q.company_owner}", border=0, ln=0)
        pdf.cell(65,5,f"Тел: {q.company_owner.phone}", border=0, ln=1)
        pdf.multi_cell(0,4,f"Комментарий: {q.building.comment if q.building else '--'}", border=0, ln=1)
        pdf.set_font("Arial", 'B', size=10)
        descr = f"Описание заявки: {q.worksystem.name} | {q.description}" if q.worksystem else f"Описание заявки: {q.description}"    
        pdf.multi_cell(0,4, txt = descr, border=0, ln=1)
        pdf.set_font("Arial", '', size=10)
        workers = "; ".join([w.name for w in q.employee.all()])
        pdf.cell(0,5,f"Исполнитель: {workers}", border=0, ln=1)
        pdf.cell(0,5,f"Распоряжение-направление выдал диспетчер: {Employee.objects.get(user=q.author).name}", border=0, ln=1)
        pdf.ln(3)
        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(0,5,f"Фактическое выполнение работ на объекте с  ___:___ до ___:___ «___»__________ 20___", border=0, ln=1)
        pdf.set_font("Arial", '', size=10)
        pdf.cell(0,5,f"Ремонтные работы:_______________________________________________________________________________", border=0, ln=1)
        for n in range(6):
            pdf.cell(0,5,"________________________________________________________________________________________________", border=0, ln=1) 

        pdf.ln(5)
        pdf.set_font("Arial", '', size=10)
        pdf.cell(100,6,f"Ответственный исполнитель:", border=0, align="L", ln=0)
        pdf.cell(90,6,f"________________{workers}", border=0, align="R", ln=1)

        pdf.cell(100,6,f"Заявитель:", border=0, align="L", ln=0)
        pdf.cell(90,6,f"________________{q.citizen}", border=0, align="R", ln=1)
        pdf.ln(10)

    return io.BytesIO(pdf.output())
    #return io.BytesIO(bytes(pdf.output(dest = 'S'), encoding='latin1'))
