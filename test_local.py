"""
Pruebas locales — ejecutar ANTES de conectar Azure para verificar que el código es correcto.

Comando: python test_local.py
No requiere credenciales de Azure ni OpenAI para las pruebas de lógica.
"""

import sys
import json
import unittest
from unittest.mock import MagicMock, patch


class TestValidatorAgent(unittest.TestCase):
    """Prueba el ValidatorAgent sin ningún servicio externo."""

    def setUp(self):
        from agents.validator_agent import ValidatorAgent
        self.validator = ValidatorAgent()

    def test_factura_alto_valor_detecta_critico(self):
        analisis = {
            "tipo_documento": "factura",
            "entidades": [{"nombre": "monto_total", "tipo": "monto", "valor": "75000"}],
            "alertas": [],
        }
        result = self.validator.validar(analisis)
        self.assertFalse(result["valido"])
        niveles = [f["nivel"] for f in result["flags"]]
        self.assertIn("critico", niveles)

    def test_factura_normal_pasa_validacion(self):
        analisis = {
            "tipo_documento": "factura",
            "entidades": [{"nombre": "monto_total", "tipo": "monto", "valor": "1500"}],
            "alertas": [],
        }
        result = self.validator.validar(analisis)
        self.assertTrue(result["valido"])

    def test_contrato_con_penalidad(self):
        analisis = {
            "tipo_documento": "contrato",
            "entidades": [{"nombre": "penalidad", "tipo": "clausula", "valor": "penalidad del 10%"}],
            "alertas": [],
        }
        result = self.validator.validar(analisis)
        self.assertGreater(result["total_alertas"], 0)

    def test_documento_sin_tipo_no_falla(self):
        analisis = {"tipo_documento": "otro", "entidades": [], "alertas": []}
        result = self.validator.validar(analisis)
        self.assertIn("valido", result)
        self.assertIn("flags", result)


class TestExtractorAgentMock(unittest.TestCase):
    """Prueba el ExtractorAgent con Document Intelligence mockeado."""

    @patch("agents.extractor_agent.DocumentIntelligenceClient")
    def test_extractor_devuelve_estructura_correcta(self, mock_di_class):
        mock_parrafo = MagicMock()
        mock_parrafo.content = "Contrato de servicio entre Empresa A y Empresa B."

        mock_pagina = MagicMock()

        mock_resultado = MagicMock()
        mock_resultado.paragraphs = [mock_parrafo]
        mock_resultado.tables = []
        mock_resultado.pages = [mock_pagina]

        mock_poller = MagicMock()
        mock_poller.result.return_value = mock_resultado

        mock_client = MagicMock()
        mock_client.begin_analyze_document.return_value = mock_poller
        mock_di_class.return_value = mock_client

        import os
        os.environ.setdefault("DOCUMENTINTELLIGENCE_ENDPOINT", "https://fake.cognitiveservices.azure.com/")
        os.environ.setdefault("DOCUMENTINTELLIGENCE_API_KEY", "fake-key")

        import tempfile, os as _os
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake content")
            ruta = f.name

        try:
            from agents.extractor_agent import ExtractorAgent
            extractor = ExtractorAgent()
            resultado = extractor.extraer(ruta)

            self.assertIn("texto", resultado)
            self.assertIn("tablas", resultado)
            self.assertIn("num_paginas", resultado)
            self.assertIn("tiene_texto", resultado)
            self.assertTrue(resultado["tiene_texto"])
            self.assertEqual(resultado["num_paginas"], 1)
        finally:
            _os.unlink(ruta)


class TestAnalyzerAgentMock(unittest.TestCase):
    """Prueba el AnalyzerAgent con OpenAI y Search mockeados."""

    @patch("agents.analyzer_agent.SearchTool")
    @patch("agents.analyzer_agent.OpenAI")
    def test_analyzer_parsea_json_correcto(self, mock_oai_class, mock_search_class):
        respuesta_json = json.dumps({
            "tipo_documento": "factura",
            "resumen": "Factura de servicios de TI por $2,500.",
            "entidades": [{"nombre": "monto_total", "tipo": "monto", "valor": "2500"}],
            "alertas": [],
            "confianza": 0.95,
        })

        mock_choice = MagicMock()
        mock_choice.message.content = respuesta_json
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]

        mock_oai = MagicMock()
        mock_oai.chat.completions.create.return_value = mock_completion
        mock_oai.embeddings.create.return_value = MagicMock(data=[MagicMock(embedding=[0.1] * 1536)])
        mock_oai_class.return_value = mock_oai

        mock_search = MagicMock()
        mock_search.buscar_similares.return_value = []
        mock_search_class.return_value = mock_search

        import os
        os.environ.setdefault("OPENAI_API_KEY", "fake-key")
        os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")

        from agents.analyzer_agent import AnalyzerAgent
        analyzer = AnalyzerAgent()
        resultado = analyzer.analizar("Factura por servicios de consultoría tecnológica.")

        self.assertEqual(resultado["tipo_documento"], "factura")
        self.assertGreater(resultado["confianza"], 0.9)
        self.assertIsInstance(resultado["entidades"], list)

    @patch("agents.analyzer_agent.SearchTool")
    @patch("agents.analyzer_agent.OpenAI")
    def test_analyzer_maneja_json_invalido(self, mock_oai_class, mock_search_class):
        mock_choice = MagicMock()
        mock_choice.message.content = "Respuesta inválida que no es JSON"
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]

        mock_oai = MagicMock()
        mock_oai.chat.completions.create.return_value = mock_completion
        mock_oai.embeddings.create.return_value = MagicMock(data=[MagicMock(embedding=[0.0] * 1536)])
        mock_oai_class.return_value = mock_oai

        mock_search = MagicMock()
        mock_search.buscar_similares.return_value = []
        mock_search_class.return_value = mock_search

        import os
        os.environ.setdefault("OPENAI_API_KEY", "fake-key")
        os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")

        from agents.analyzer_agent import AnalyzerAgent
        analyzer = AnalyzerAgent()
        resultado = analyzer.analizar("Texto cualquiera")

        self.assertIn("tipo_documento", resultado)
        self.assertIn("alertas", resultado)
        self.assertEqual(resultado["confianza"], 0.0)


class TestFlaskAPI(unittest.TestCase):
    """Prueba los endpoints de Flask sin servicios externos."""

    def setUp(self):
        with patch("agents.orchestrator.ExtractorAgent"), \
             patch("agents.orchestrator.AnalyzerAgent"), \
             patch("agents.orchestrator.ValidatorAgent"), \
             patch("agents.orchestrator.SearchTool"), \
             patch("agents.orchestrator.StorageTool"):
            import app as flask_app
            self.client = flask_app.app.test_client()

    def test_health_devuelve_ok(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "ok")

    def test_procesar_sin_archivo_devuelve_400(self):
        response = self.client.post("/procesar")
        self.assertEqual(response.status_code, 400)

    def test_preguntar_sin_body_devuelve_400(self):
        response = self.client.post("/preguntar", content_type="application/json", data="{}")
        self.assertEqual(response.status_code, 400)

    def test_preguntar_con_pregunta_vacia_devuelve_400(self):
        response = self.client.post(
            "/preguntar",
            json={"pregunta": "   "},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    print("🧪 Ejecutando pruebas locales (sin Azure ni OpenAI reales)...\n")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestValidatorAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractorAgentMock))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyzerAgentMock))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaskAPI))

    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)

    if resultado.wasSuccessful():
        print("\n✅ Todas las pruebas pasaron. El código está listo para conectar con Azure.")
        sys.exit(0)
    else:
        print(f"\n❌ {len(resultado.failures)} fallo(s) encontrado(s).")
        sys.exit(1)
