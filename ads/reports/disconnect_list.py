def generate_disconnects(qs):
    from fpdf import FPDF, HTMLMixin
    import io
    from  django.utils import timezone

    pdf = FPDF()
    #pdf = FPDF('L')
    pdf.add_font("Arial", "", "static/arial.ttf", uni=True)
    pdf.add_font("Arial", "B", "static/arial_b.ttf", uni=True)

    pdf.set_margins(10, 10, -1)
    #pdf.set_auto_page_break(False, margin = 10)
    pdf.add_page()


    pdf.set_font("Arial", '', size=10)
    pdf.cell(0,5,f"", align="C", ln=1)
    pdf.ln()
    
    data = []
    data.append(('№','Период','Адрес','Система','Описание','Ответственный'))
    for q in qs:
        print(q)
        start_disconnect = timezone.localtime(q.start_disconnect)
        plan_connection_date = timezone.localtime(q.plan_connection_date) if q.plan_connection_date else None
        if plan_connection_date:
            plan_connection_date = plan_connection_date.strftime('%d.%m.%Y %H:%M')
        data.append(
                         (f"{q.number}",
                          f"{start_disconnect.strftime('%d.%m.%Y %H:%M')} - {plan_connection_date}",
                          f"{q.get_buildings_text}",
                          f"{q.get_worksystem_text}",
                          f"{q.description}",
                          f"{q.company_exec}",
                         )
            )

    with pdf.table(col_widths=(10, 30, 50, 20,35,30), line_height=pdf.font_size) as table:
        for data_row in data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)

    return io.BytesIO(pdf.output())
