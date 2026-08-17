import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generar_nota_entrega(datos, ruta_salida=None):
    if ruta_salida is None:
        notas_dir = tempfile.gettempdir()
        ruta_salida = os.path.join(notas_dir, f"nota_{datos['num_nota']}.pdf")

    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=letter,
        leftMargin=56.7,
        rightMargin=56.7,
        topMargin=56.7,
        bottomMargin=56.7
    )

    styles = getSampleStyleSheet()

    style_empresa = ParagraphStyle('Empresa', parent=styles['Normal'], fontSize=18, leading=22,
                                   fontName='Helvetica-Bold', textColor=colors.HexColor('#000000'))
    style_direccion = ParagraphStyle('Direccion', parent=styles['Normal'], fontSize=9.5, leading=13,
                                     textColor=colors.HexColor('#333333'))
    style_doc_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontSize=16, leading=19,
                                     fontName='Helvetica-Bold', alignment=2, textColor=colors.HexColor('#000000'))
    style_doc_num = ParagraphStyle('DocNum', parent=styles['Normal'], fontSize=11, leading=14,
                                   fontName='Helvetica-Bold', alignment=2, textColor=colors.HexColor('#333333'))
    style_fecha = ParagraphStyle('Fecha', parent=style_doc_num, fontName='Helvetica', fontSize=10, leading=13)
    style_field_title = ParagraphStyle('FieldTitle', parent=styles['Normal'], fontSize=9, leading=11,
                                       fontName='Helvetica-Bold', textColor=colors.HexColor('#000000'))
    style_field_val = ParagraphStyle('FieldVal', parent=styles['Normal'], fontSize=9.5, leading=12,
                                     textColor=colors.HexColor('#111111'))
    style_th = ParagraphStyle('TH', parent=styles['Normal'], fontSize=9, leading=11,
                              fontName='Helvetica-Bold', textColor=colors.HexColor('#000000'))
    style_th_r = ParagraphStyle('THR', parent=styles['Normal'], fontSize=9, leading=11,
                                fontName='Helvetica-Bold', alignment=2, textColor=colors.HexColor('#000000'))
    style_td = ParagraphStyle('TD', parent=styles['Normal'], fontSize=9, leading=12,
                              textColor=colors.HexColor('#111111'))
    style_td_r = ParagraphStyle('TDR', parent=styles['Normal'], fontSize=9, leading=12, alignment=2,
                                textColor=colors.HexColor('#111111'))
    style_total_lbl = ParagraphStyle('TotalLbl', parent=styles['Normal'], fontSize=10, leading=13,
                                     fontName='Helvetica-Bold', alignment=2, textColor=colors.HexColor('#000000'))
    style_total_val = ParagraphStyle('TotalVal', parent=styles['Normal'], fontSize=10, leading=13,
                                     fontName='Helvetica-Bold', alignment=2, textColor=colors.HexColor('#000000'))
    style_footer = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8.5, leading=11,
                                  fontName='Helvetica', alignment=1, textColor=colors.HexColor('#444444'))

    elements = []

    empresa_info = [
        [Paragraph(datos['empresa'].upper(), style_empresa)],
        [Paragraph(datos['direccion'], style_direccion)]
    ]
    t_empresa = Table(empresa_info, colWidths=[310])
    t_empresa.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))

    doc_info = [
        [Paragraph("NOTA DE ENTREGA", style_doc_title)],
        [Paragraph(f"N°: {datos['num_nota']}", style_doc_num)],
        [Paragraph(f"Fecha: {datos['fecha']}", style_fecha)]
    ]
    t_doc = Table(doc_info, colWidths=[190])
    t_doc.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))

    t_header = Table([[t_empresa, t_doc]], colWidths=[310, 190])
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(t_header)
    elements.append(Spacer(1, 15))

    cliente_data = [
        [Paragraph("Cliente:", style_field_title), Paragraph("C.I.:", style_field_title)],
        [Paragraph(f"|  {datos['cliente']}", style_field_val), Paragraph(f"|  {datos['ci']}", style_field_val)],
        [Spacer(1, 4), Spacer(1, 4)],
        [Paragraph("Metodo Pago:", style_field_title), Paragraph("Telefono:", style_field_title)],
        [Paragraph(f"|  {datos['metodo_pago']}", style_field_val), Paragraph(f"|  {datos['telefono']}", style_field_val)]
    ]
    t_cliente = Table(cliente_data, colWidths=[250, 250])
    t_cliente.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(t_cliente)
    elements.append(Spacer(1, 15))

    def fmt(n):
        return f"{n:.2f}".replace('.', ',')

    table_data = [[
        Paragraph("Descripcion", style_th),
        Paragraph("Cantidad", style_th_r),
        Paragraph("Precio Unit.", style_th_r),
        Paragraph("Subtotal", style_th_r)
    ]]

    for item in datos['items']:
        table_data.append([
            Paragraph(item['descripcion'], style_td),
            Paragraph(str(item['cantidad']), style_td_r),
            Paragraph(fmt(item['precio']), style_td_r),
            Paragraph(fmt(item['subtotal']), style_td_r)
        ])

    t_items = Table(table_data, colWidths=[260, 70, 85, 85])
    t_items.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 10))

    descuento = datos.get('descuento', 0) or 0
    totales_data = []
    if descuento > 0:
        totales_data.append([
            Paragraph("DESCUENTO $:", style_total_lbl),
            Paragraph(f"-{fmt(descuento)}", style_total_val)
        ])
    totales_data.append([
        Paragraph("TOTAL VENTA $:", style_total_lbl),
        Paragraph(fmt(datos['total']), style_total_val)
    ])
    totales_data.append([
        Paragraph("TOTAL CANCELADO $:", style_total_lbl),
        Paragraph(fmt(datos['total_cancelado']), style_total_val)
    ])
    t_totales = Table(totales_data, colWidths=[415, 85])
    t_totales.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
    ]))
    elements.append(t_totales)
    elements.append(Spacer(1, 30))

    elements.append(Paragraph("Documento de control interno - No genera credito fiscal", style_footer))

    doc.build(elements)
    return ruta_salida
