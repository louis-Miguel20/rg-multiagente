# 🚀 Sistema Multiagente de Análisis de Documentos Empresariales

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-0089D6?style=for-the-badge&logo=microsoftazure&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

Una solución empresarial avanzada para la ingesta, análisis, validación y reporte automatizado de documentos (PDFs e imágenes) utilizando **Inteligencia Artificial Generativa** y **RAG (Retrieval-Augmented Generation)**.

---

## 💼 El Problema de Negocio

Las empresas procesan miles de documentos diariamente (contratos, facturas, reportes técnicos) de forma manual. Esto genera:
- **Cuellos de botella** operativos.
- **Errores humanos** en la extracción de datos críticos.
- **Información silenciada**: Datos valiosos que no se pueden buscar ni analizar.

### 📈 Métricas de Impacto (Estimadas)
- **Reducción del 85%** en el tiempo de procesamiento manual.
- **95% de precisión** en la extracción de entidades clave (fechas, montos, cláusulas).
- **100% de trazabilidad** y búsqueda semántica de la base documental.

---

## 🏗️ Arquitectura del Sistema

El sistema utiliza un diseño de **Orquestación Multiagente** donde cada componente tiene una responsabilidad única y aislada.

```text
                     +---------------------------+
                     |      Cliente (Web/API)    |
                     +-------------+-------------+
                                   |
                                   v
                     +-------------+-------------+
                     |    Orquestador Central    |
                     +-------------+-------------+
                                   |
         +-------------------------+-------------------------+
         |                         |                         |
+--------v---------+      +--------v---------+      +--------v---------+
| Extractor Agent  |      |  Analyzer Agent  |      | Validator Agent  |
| (Azure Doc Intel)|      | (GPT-4o + RAG)   |      | (Business Logic) |
+--------+---------+      +--------+---------+      +--------+---------+
         |                         |                         |
         |                +--------v---------+               |
         |                |  Reporter Agent  |               |
         |                | (Executive PDF)  |               |
         |                +--------+---------+               |
         |                         |                         |
         +-------------------------+-------------------------+
                                   |
                     +-------------v-------------+
                     |   Infraestructura (Cloud) |
                     | (Blob Storage + AI Search)|
                     +---------------------------+
```

### 🤖 Nuestros Agentes
1.  **ExtractorAgent**: Digitaliza documentos complejos usando OCR avanzado y análisis de layout.
2.  **AnalyzerAgent**: Interpreta el contexto, resume y extrae entidades usando LLMs y búsqueda vectorial.
3.  **ValidatorAgent**: Aplica reglas de negocio críticas (ej: alertas de vencimiento o montos altos).
4.  **ReporterAgent**: Genera reportes ejecutivos listos para la toma de decisiones.
5.  **Orchestrator**: Coordina el flujo de datos y garantiza la persistencia en la nube.

---

## 📸 Demo

![Screenshot Placeholder](https://via.placeholder.com/800x450.png?text=Demo+Sistema+Multiagente+Documental)
*Próximamente: Video demostrativo de la interfaz web y procesamiento en tiempo real.*

---

## 🛠️ Decisiones Técnicas

### 🔹 Azure AI Document Intelligence v4.0 vs Form Recognizer
Se optó por el SDK más reciente (`azure-ai-documentintelligence`) por su capacidad superior para manejar **estructuras no uniformes** y tablas complejas que el antiguo Form Recognizer solía omitir. Esto permite una precisión mayor en documentos financieros y legales.

### 🔹 ¿Por qué Búsqueda Vectorial (RAG)?
A diferencia de la búsqueda por palabras clave tradicional, la **Búsqueda Vectorial en Azure AI Search** permite:
- Encontrar documentos por **significado**, no solo por texto.
- Alimentar al LLM con el contexto exacto para evitar alucinaciones.
- Comparar nuevos documentos con casos históricos de forma instantánea.

---

## 🚀 Instalación y Uso

Para una guía detallada paso a paso sobre la configuración de servicios en Azure y el entorno local, consulta nuestra:

👉 [**GUIA_COMPLETA.md**](GUIA_COMPLETA.md)

---

## 📚 Documentación del Proyecto

Para conocer en detalle cada módulo, agente y las funciones disponibles, revisa la referencia técnica:

👉 [**DOCUMENTACION.md**](DOCUMENTACION.md)

---

## 🔒 Seguridad y Monitoreo

### 🔹 Autenticación
El sistema implementa una capa de seguridad simple pero efectiva mediante un **Header `X-API-Key`**. Las peticiones a los endpoints de procesamiento y consulta deben incluir una clave válida configurada en las variables de entorno.

### 🔹 Logging Estructurado
Cada paso del pipeline se registra con **tiempos de ejecución y trazabilidad completa** en `logs/pipeline.log`. El sistema utiliza rotación de archivos para optimizar el almacenamiento.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles.

---
*Desarrollado como parte de un portafolio de soluciones de IA aplicadas al sector corporativo.*
