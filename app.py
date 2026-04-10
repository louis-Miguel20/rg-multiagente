import os
import tempfile
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from agents.orchestrator import Orchestrator

app = Flask(__name__)
CORS(app)

orchestrator = Orchestrator()

EXTENSIONES_PERMITIDAS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


def requiere_api_key(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        api_key_valida = os.getenv("API_KEY")

        if not api_key or api_key != api_key_valida:
            return jsonify({"error": "No autorizado. API Key faltante o incorrecta"}), 401
        
        return f(*args, **kwargs)
    return decorado


def extension_valida(nombre: str) -> bool:
    return os.path.splitext(nombre)[1].lower() in EXTENSIONES_PERMITIDAS


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mensaje": "Sistema multiagente funcionando"})


@app.route("/procesar", methods=["POST"])
@requiere_api_key
def procesar():
    if "archivo" not in request.files:
        return jsonify({"error": "No se envió ningún archivo. Campo esperado: 'archivo'"}), 400

    archivo = request.files["archivo"]

    if archivo.filename == "":
        return jsonify({"error": "El archivo no tiene nombre"}), 400

    if not extension_valida(archivo.filename):
        return jsonify({"error": f"Extensión no permitida. Usa: {EXTENSIONES_PERMITIDAS}"}), 400

    sufijo = os.path.splitext(archivo.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=sufijo) as tmp:
        archivo.save(tmp.name)
        ruta_tmp = tmp.name

    try:
        resultado = orchestrator.procesar_documento(ruta_tmp)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(ruta_tmp):
            os.remove(ruta_tmp)


@app.route("/preguntar", methods=["POST"])
@requiere_api_key
def preguntar():
    datos = request.get_json()
    if not datos or "pregunta" not in datos:
        return jsonify({"error": "Cuerpo JSON esperado con campo 'pregunta'"}), 400

    pregunta = datos["pregunta"].strip()
    if not pregunta:
        return jsonify({"error": "La pregunta no puede estar vacía"}), 400

    try:
        resultado = orchestrator.responder_pregunta(pregunta)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def root():
    return app.send_static_file("index.html") if os.path.exists("frontend/index.html") else jsonify({
        "rutas": {
            "GET /health": "Estado del sistema",
            "POST /procesar": "Subir documento (form-data, campo: archivo)",
            "POST /preguntar": "Hacer pregunta (JSON: {pregunta: '...'})",
        }
    })


if __name__ == "__main__":
    print("🚀 Sistema multiagente iniciando en http://localhost:5000")
    app.run(debug=True, port=5000)
