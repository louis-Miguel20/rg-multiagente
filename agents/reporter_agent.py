import os
import tempfile
from fpdf import FPDF
from datetime import datetime

class ReporterAgent:
    """
    Agente 4: Genera reportes ejecutivos en PDF a partir del análisis.
    Usa: fpdf2
    """

    def generar_reporte(self, resultado: dict, doc_id: str) -> str:
        """
        Genera un reporte PDF con el resumen, entidades y alertas.
        Retorna la ruta local del PDF generado.
        """
        pdf = FPDF()
        pdf.add_page()
        
        # Título
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 15, "Reporte de Análisis Documental", ln=True, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"ID de Documento: {doc_id}", ln=True, align="C")
        pdf.cell(0, 10, f"Fecha de Procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(10)

        # Información del Archivo
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, "1. Información General", ln=True, fill=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, f"Nombre: {resultado.get('nombre_archivo', 'N/A')}", ln=True)
        pdf.cell(0, 8, f"Tipo: {resultado.get('tipo_documento', 'N/A').upper()}", ln=True)
        pdf.cell(0, 8, f"Páginas: {resultado.get('num_paginas', 0)}", ln=True)
        pdf.cell(0, 8, f"Confianza del Análisis: {int(resultado.get('confianza', 0) * 100)}%", ln=True)
        pdf.ln(5)

        # Resumen Ejecutivo
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "2. Resumen Ejecutivo", ln=True, fill=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, resultado.get("resumen", "No se generó resumen."))
        pdf.ln(5)

        # Entidades Detectadas
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "3. Datos Extraídos", ln=True, fill=True)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 8, "Campo", border=1)
        pdf.cell(130, 8, "Valor", border=1, ln=True)
        pdf.set_font("Arial", "", 10)
        
        for entidad in resultado.get("entidades", []):
            pdf.cell(60, 8, str(entidad.get("nombre")), border=1)
            pdf.cell(130, 8, str(entidad.get("valor")), border=1, ln=True)
        
        if not resultado.get("entidades"):
            pdf.cell(0, 8, "No se detectaron entidades específicas.", border=1, ln=True)
        pdf.ln(5)

        # Alertas y Validación
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "4. Validación y Alertas", ln=True, fill=True)
        pdf.set_font("Arial", "", 11)
        
        estado_valido = "VÁLIDO" if resultado.get("valido") else "REVISIÓN REQUERIDA"
        pdf.cell(0, 8, f"Estado del Documento: {estado_valido}", ln=True)
        
        for alerta in resultado.get("alertas", []):
            mensaje = alerta.get("mensaje") if isinstance(alerta, dict) else str(alerta)
            nivel = alerta.get("nivel", "info").upper() if isinstance(alerta, dict) else "INFO"
            pdf.set_text_color(200, 0, 0) if nivel in ["CRITICO", "URGENTE"] else pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 7, f"• [{nivel}] {mensaje}")
        
        pdf.set_text_color(0, 0, 0)

        # Guardar en temporal
        ruta_reporte = os.path.join(tempfile.gettempdir(), f"reporte_{doc_id}.pdf")
        pdf.output(ruta_reporte)
        return ruta_reporte
