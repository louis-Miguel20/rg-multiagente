from datetime import datetime, timedelta


class ValidatorAgent:
    """
    Agente 3: Valida el análisis contra reglas de negocio configurables.
    No requiere servicios externos — es lógica pura.
    """

    REGLAS = {
        "factura": [
            {"campo": "monto_total", "max": 50000, "alerta": "Factura de alto valor (>$50,000)"},
            {"campo": "fecha_vencimiento", "dias": 7, "alerta": "Vencimiento en menos de 7 días"},
        ],
        "contrato": [
            {"campo": "penalidad", "palabra_clave": "penalidad", "alerta": "Cláusula de penalidad detectada"},
            {"campo": "duracion_meses", "max": 24, "alerta": "Contrato de larga duración (>24 meses)"},
            {"campo": "renovacion_automatica", "palabra_clave": "automática", "alerta": "Contrato con renovación automática"},
        ],
    }

    def validar(self, analisis: dict) -> dict:
        tipo = analisis.get("tipo_documento", "otro")
        entidades = {e["nombre"].lower(): e["valor"] for e in analisis.get("entidades", [])}
        alertas_del_analisis = analisis.get("alertas", [])

        flags = []
        reglas = self.REGLAS.get(tipo, [])

        for regla in reglas:
            campo = regla.get("campo", "")
            valor = entidades.get(campo, "")

            if "max" in regla:
                try:
                    num = float(str(valor).replace(",", "").replace("$", "").strip())
                    if num > regla["max"]:
                        flags.append({"nivel": "critico", "mensaje": regla["alerta"], "valor": str(valor)})
                except (ValueError, TypeError):
                    pass

            if "palabra_clave" in regla and regla["palabra_clave"] in str(valor).lower():
                flags.append({"nivel": "advertencia", "mensaje": regla["alerta"]})

            if "dias" in regla:
                try:
                    fecha = datetime.strptime(str(valor), "%Y-%m-%d")
                    if fecha <= datetime.now() + timedelta(days=regla["dias"]):
                        flags.append({"nivel": "urgente", "mensaje": regla["alerta"], "valor": str(valor)})
                except (ValueError, TypeError):
                    pass

        for alerta in alertas_del_analisis:
            if alerta and alerta not in [f["mensaje"] for f in flags]:
                flags.append({"nivel": "info", "mensaje": alerta})

        tiene_criticos = any(f["nivel"] == "critico" for f in flags)

        return {
            "valido": not tiene_criticos,
            "flags": flags,
            "total_alertas": len(flags),
        }
