import os
import sqlite3
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = FastAPI(title="Consultoría Base de Diagnóstico - Vórtice Integration", version="1.0")
# --- AGREGA ESTO AQUÍ ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde cualquier origen (ideal para desarrollo local)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE BASE DE DATOS SQLITE ---
DB_NAME = "vortice_tokens.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            usado INTEGER DEFAULT 0,
            nombre_cliente TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Estructura de entrada actualizada que ahora exige el Token de Acceso
class EvaluacionRequest(BaseModel):
    token: str = Field(..., description="Token único de acceso proporcionado tras el pago")
    nombre_cliente: str = Field(..., description="Nombre de la clínica u organización evaluada")
    eficiencia: list[int] = Field(..., description="5 valores entre 1 y 5")
    cohesion: list[int] = Field(..., description="5 valores entre 1 y 5")
    digitalizacion: list[int] = Field(..., description="5 valores entre 1 y 5")

def obtener_prosa_comercial(igm: float, estadio: str) -> str:
    if igm <= 2.0:
        return (
            "<b>Diagnóstico de Impacto (Nivel Ignición):</b> La organización opera bajo un modelo altamente "
            "reactivo y dependiente del esfuerzo heroico individual. Las fugas de energía sistémica y la fragmentación "
            "operativa ponen en riesgo la continuidad del servicio y generan un desgaste crónico en los equipos. "
            "<b>Siguiente paso recomendado:</b> Se requiere con urgencia una intervención de estabilización mediante "
            "la implementación de una Célula Mínima Viable (CMV) y la reingeniería de flujos críticos."
        )
    elif igm <= 3.0:
        return (
            "<b>Interpretación Ejecutiva (Nivel Templado):</b> La organización ha superado el caos inicial y cuenta con rutinas básicas, "
            "pero su operación se ve frenada por la persistencia de 'silos' aislados y la dependencia de procesos manuales. "
            "Esto genera un techo invisible de crecimiento: los equipos apagan incendios diarios en lugar de escalar. "
            "<b>Oportunidad de Intervención:</b> Para romper este estancamiento y evitar el colapso ante aumentos de demanda, "
            "es imperativo estructurar una arquitectura de procesos conectada y una gobernanza unificada que nuestra consultoría especializada puede desplegar."
        )
    elif igm <= 4.0:
        return (
            "<b>Interpretación Ejecutiva (Nivel Óptimo):</b> Los flujos se encuentran estandarizados bajo parámetros sólidos y existe una "
            "baja fuga de energía sistémica. La organización opera de forma predecible y ordenada. "
            "<b>Oportunidad de Intervención:</b> El desafío actual no es sobrevivir, sino acelerar hacia la autorregulación avanzada "
            "y la optimización digital mediante analítica predictiva de alto nivel."
        )
    else:
        return (
            "<b>Interpretación Ejecutiva (Nivel Avanzado / Vórtice):</b> La organización opera como un centro de referencia con resiliencia "
            "y capacidad de innovación constante. "
            "<b>Oportunidad de Intervención:</b> Mantener este estatus exige blindar la soberanía del dato y escalar el modelo fractal "
            "hacia nuevos mercados o unidades de negocio."
        )

def generar_pdf_diagnostico(data_resultado: dict, nombre_cliente: str, ruta_salida: str = "informe_diagnostico.pdf"):
    doc = SimpleDocTemplate(ruta_salida, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    styles = getSampleStyleSheet()
    
    color_primario = colors.HexColor("#1A2B4C")
    color_secundario = colors.HexColor("#008080")
    color_gris_texto = colors.HexColor("#333333")
    
    estilo_titulo = ParagraphStyle('TituloPrincipal', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=color_primario, spaceAfter=4)
    estilo_subtitulo = ParagraphStyle('SubTitulo', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=13, textColor=color_secundario, spaceAfter=12)
    estilo_seccion = ParagraphStyle('SeccionTitulo', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=color_primario, spaceBefore=10, spaceAfter=4)
    estilo_cuerpo = ParagraphStyle('CuerpoTexto', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=color_gris_texto, spaceAfter=6)
    estilo_legal = ParagraphStyle('TextoLegal', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7, leading=10, textColor=colors.HexColor("#777777"), spaceBefore=15)

    story.append(Paragraph("VÓRTICE INTEGRATION HOLDING SpA", estilo_subtitulo))
    story.append(Paragraph("CONSULTORÍA BASE DE DIAGNÓSTICO EJECUTIVO", estilo_titulo))
    story.append(Paragraph(f"<b>Organización Evaluada:</b> {nombre_cliente}", estilo_cuerpo))
    story.append(HRFlowable(width="100%", thickness=1.5, color=color_secundario, spaceBefore=6, spaceAfter=12))

    story.append(Paragraph("1. Diagnóstico de Madurez Sistémica", estilo_seccion))
    igm = data_resultado["indice_global_madurez"]
    estadio = data_resultado["estadio_termico"]
    resumen = data_resultado["diagnostico_resumen"]
    
    tabla_resumen_data = [
        [Paragraph("<b>Índice Global de Madurez (IGM):</b>", estilo_cuerpo), Paragraph(f"<b>{igm} / 5.0</b>", estilo_cuerpo)],
        [Paragraph("<b>Estadio Térmico Actual:</b>", estilo_cuerpo), Paragraph(f"<b>{estadio}</b>", estilo_cuerpo)],
        [Paragraph("<b>Evaluación Preliminar:</b>", estilo_cuerpo), Paragraph(resumen, estilo_cuerpo)]
    ]
    t_resumen = Table(tabla_resumen_data, colWidths=[150, 354])
    t_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F9FBFD")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_resumen)
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. Análisis de Impacto y Brecha Sistémica", estilo_seccion))
    prosa_texto = obtener_prosa_comercial(igm, estadio)
    story.append(Paragraph(prosa_texto, estilo_cuerpo))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3. Gradiente por Dimensiones Propietarias", estilo_seccion))
    dims = data_resultado["detalles_dimensiones"]
    tabla_dims_data = [
        [Paragraph("<b>Dimensión Metodológica</b>", estilo_cuerpo), Paragraph("<b>Puntaje (1-5)</b>", estilo_cuerpo)],
        [Paragraph("Eficiencia Operativa (Flujos y Procesos)", estilo_cuerpo), Paragraph(str(dims["eficiencia_operativa"]), estilo_cuerpo)],
        [Paragraph("Cohesión Humana (Propósito y Alineación)", estilo_cuerpo), Paragraph(str(dims["cohesion_humana"]), estilo_cuerpo)],
        [Paragraph("Digitalización y Manejo de Datos", estilo_cuerpo), Paragraph(str(dims["digitalizacion"]), estilo_cuerpo)],
    ]
    t_dims = Table(tabla_dims_data, colWidths=[354, 150])
    t_dims.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EBF4FF")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_dims)
    story.append(Spacer(1, 8))

    story.append(Paragraph("4. Mapa de Alertas (Zonas Frías)", estilo_seccion))
    zonas_frias = data_resultado["alertas_zonas_frias"]
    texto_frias = f"Se han detectado <b>{zonas_frias} puntos críticos</b> (nivel 1 o 2) que requieren intervención prioritaria para evitar fugas de energía y fricción sistémica, estructurando la base para la sesión de devolución."
    story.append(Paragraph(texto_frias, estilo_cuerpo))
    story.append(Spacer(1, 10))

    legal_text = (
        "<b>AVISO DE PROPIEDAD INTELECTUAL Y CONFIDENCIALIDAD:</b><br/>"
        "Este informe y su motor subyacente de cálculo, gradientes térmicos y estructura metodológica "
        "están protegidos por las leyes de derechos de autor y propiedad industrial en favor de "
        "Vórtice Integration Holding SpA. Queda estrictamente prohibida su reproducción total o parcial "
        "o la copia de algoritmos sin autorización expresa de la titularidad de autoría."
    )
    story.append(Paragraph(legal_text, estilo_legal))

    doc.build(story)
    return ruta_salida

# Ruta auxiliar para generar tokens de prueba fácilmente
@app.get("/api/crear-token")
def crear_token(cliente: str):
    nuevo_token = str(uuid.uuid4())[:8].upper() # Genera un código alfanumérico de 8 caracteres
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tokens (token, usado, nombre_cliente) VALUES (?, 0, ?)", (nuevo_token, cliente))
    conn.commit()
    conn.close()
    return {"token_generado": nuevo_token, "cliente": cliente, "mensaje": "Token creado exitosamente para pruebas."}

@app.post("/api/generar-informe-pdf")
def calcular_y_generar_pdf(data: EvaluacionRequest):
    # 1. Validar Token en la Base de Datos
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT usado FROM tokens WHERE token = ?", (data.token,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=403, detail="Acceso denegado: El token ingresado no es válido.")
    
    if row[0] == 1:
        conn.close()
        raise HTTPException(status_code=403, detail="Acceso denegado: Este token ya fue utilizado para generar un informe previo.")

    # 2. Validaciones dimensionales
    for dim_name, dim_values in [("Eficiencia", data.eficiencia), ("Cohesión", data.cohesion), ("Digitalización", data.digitalizacion)]:
        if len(dim_values) != 5 or any(v < 1 or v > 5 for v in dim_values):
            conn.close()
            raise HTTPException(status_code=400, detail=f"La dimensión {dim_name} debe contener exactamente 5 valores entre 1 y 5.")

    pd_eficiencia = sum(data.eficiencia) / 5.0
    pd_cohesion = sum(data.cohesion) / 5.0
    pd_digitalizacion = sum(data.digitalizacion) / 5.0

    igm = (pd_eficiencia * 0.40) + (pd_cohesion * 0.30) + (pd_digitalizacion * 0.30)

    if igm <= 2.0:
        estadio = "Nivel 1: Ignición (Crítico)"
        diagnostico = "Alta dependencia de procesos manuales, alta fragmentación y silos operativos."
    elif igm <= 3.0:
        estadio = "Nivel 2: Templado (Funcional)"
        diagnostico = "Estabilización básica de flujos, pero con persistencia de silos y baja escalabilidad."
    elif igm <= 4.0:
        estadio = "Nivel 3: Óptimo (Integrado)"
        diagnostico = "Procesos estandarizados bajo el modelo CP2P y baja fuga de energía sistémica."
    elif igm <= 4.6:
        estadio = "Nivel 4: Radiante (Avanzado)"
        diagnostico = "Alta predictibilidad, automatización de procesos y capacidad de autorregulación."
    else:
        estadio = "Nivel 5: Vórtice (Excelencia)"
        diagnostico = "Innovación constante y resiliencia fractal absoluta, operando como centro de referencia."

    todas_respuestas = data.eficiencia + data.cohesion + data.digitalizacion
    zonas_frias_count = sum(1 for v in todas_respuestas if v <= 2)

    resultado_dict = {
        "indice_global_madurez": round(igm, 2),
        "estadio_termico": estadio,
        "diagnostico_resumen": diagnostico,
        "detalles_dimensiones": {
            "eficiencia_operativa": round(pd_eficiencia, 2),
            "cohesion_humana": round(pd_cohesion, 2),
            "digitalizacion": round(pd_digitalizacion, 2)
        },
        "alertas_zonas_frias": zonas_frias_count
    }

    # 3. Marcar el Token como UTILIZADO en la base de datos (Garantiza el uso único)
    cursor.execute("UPDATE tokens SET usado = 1 WHERE token = ?", (data.token,))
    conn.commit()
    conn.close()

    # 4. Generar el PDF
    ruta_pdf = f"informe_{data.nombre_cliente.replace(' ', '_')}.pdf"
    generar_pdf_diagnostico(resultado_dict, data.nombre_cliente, ruta_pdf)

    return FileResponse(ruta_pdf, media_type='application/pdf', filename=ruta_pdf)

# --- HITO 2: WEBHOOK DE PASARELA DE PAGO ---
class PagoExitosoRequest(BaseModel):
    transaccion_id: str = Field(..., description="ID de la transacción de la pasarela de pago")
    nombre_cliente: str = Field(..., description="Nombre del cliente o clínica que realizó el pago")
    email_cliente: str = Field(..., description="Correo electrónico del cliente")

@app.post("/api/webhook/pago-exitoso")
def registrar_pago_y_generar_token(data: PagoExitosoRequest):
    """
    Endpoint que recibe la confirmación de la pasarela de pago,
    genera un token único de un solo uso y lo registra en la base de datos.
    """
    # Generar token alfanumérico único de 8 caracteres
    nuevo_token = str(uuid.uuid4())[:8].upper()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tokens (token, usado, nombre_cliente) VALUES (?, 0, ?)", 
            (nuevo_token, data.nombre_cliente)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error al registrar el token: {str(e)}")
    finally:
        conn.close()

    # Aquí puedes conectar en el futuro un servicio de correo (como Resend o SendGrid) 
    # para enviar automáticamente 'nuevo_token' al 'email_cliente'.
    
    return {
        "status": "success",
        "mensaje": "Pago verificado y token generado exitosamente.",
        "transaccion_id": data.transaccion_id,
        "cliente": data.nombre_cliente,
        "token_asignado": nuevo_token,
        "accion_siguiente": "Enviar este token por correo electrónico al cliente para que realice su diagnóstico."
    }