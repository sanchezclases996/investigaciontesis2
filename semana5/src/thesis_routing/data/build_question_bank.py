"""Construye banco piloto (>=100) desde FAQ y documentación UMA.

Esquema alineado a temppp/gpt2: query_id, pregunta, categoria, complejidad,
doc_referencia, seccion_referencia, respuesta_esperada, requiere_herramienta,
requiere_multiples_fuentes, es_respondible, validacion_experta.

Reglas: sin duplicados, sin inventar respuestas, categorias N/R/M/A.
"""

from __future__ import annotations

import csv
import logging
import re
import unicodedata
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

LOGGER = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
FAQ_HTML = ROOT / "data" / "raw" / "public_documents" / "D012__faq.html"
OUT_CSV = ROOT / "data" / "processed" / "question_bank" / "consultas_piloto.csv"
OUT_SYN = ROOT / "data" / "synthetic" / "generated_questions" / "consultas_desde_faq.csv"
TARGET_N = 100

QueryType = Literal["N", "R", "M", "A"]
ValidationStatus = Literal["draft", "validated", "rejected", "no_verifiable_answer"]

FAQ_SKIP_SUBSTRINGS = (
    "cómo podemos ayudarte",
    "quieres trasladarte",
    "vas a terminar",
    "cómo la recupero",
    "postula",
)


class QuestionRecord(BaseModel):
    """Registro mínimo del banco de evaluación (piloto)."""

    query_id: str
    pregunta: str
    categoria: str
    complejidad: str = "media"
    doc_referencia: str = "D012"
    seccion_referencia: str = ""
    respuesta_esperada: str = ""
    requiere_herramienta: bool = False
    requiere_multiples_fuentes: bool = False
    es_respondible: bool = True
    validacion_experta: ValidationStatus = "draft"
    candidate_strategy: str | None = Field(default="A1")
    origen: str = "faq"  # faq | documento | malla_demo


def _norm_question(text: str) -> str:
    """Normalize question text for near-duplicate detection."""
    text = unicodedata.normalize("NFKC", text).lower().strip()
    text = re.sub(r"[¿?¡!\.,;:\"'`´]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _infer_strategy(categoria: str) -> str:
    if categoria == "R":
        return "A3"
    if categoria == "A":
        return "A5"
    if categoria == "M":
        return "A3"
    return "A1"


def _flags(categoria: str, doc_referencia: str) -> dict[str, bool]:
    """Flags de diseño; respondible = hay evidencia en corpus actual (no pendiente/D010)."""
    doc = doc_referencia.strip()
    respondible = bool(doc) and not doc.startswith("pendiente_") and doc != "D010"
    # malla_demo: evidencia demo, no oficial; se marca respondible para pruebas A3 controladas
    return {
        "requiere_herramienta": categoria == "R",
        "requiere_multiples_fuentes": categoria == "M",
        "es_respondible": respondible,
    }


# --- Semillas curadas (FAQ + docs). respuesta vacía = sin gold aún ---
CURATED: list[dict[str, str]] = [
    # FAQ con respuesta conocida (borrador)
    {"pregunta": "¿Qué modalidades de estudio tiene la UMA?", "respuesta": "Presencial, Semipresencial y A Distancia; varían según la carrera.", "categoria": "N", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Pueden deshabilitarme por inasistencias?", "respuesta": "Hasta 30% de inasistencias a sesiones con horas lectivas implica desaprobación del curso (FAQ).", "categoria": "N", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Qué es el examen sustitutorio y quiénes pueden acceder?", "respuesta": "Evaluación extraordinaria opcional que reemplaza la menor nota de parcial o final; se programa en la semana 17 (FAQ).", "categoria": "N", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿En qué consiste el curso o examen de aplazados?", "respuesta": "Trámite para recuperar asignaturas desaprobadas en el periodo regular inmediato anterior, con condiciones (FAQ).", "categoria": "N", "complejidad": "alta", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Dónde reviso mis horarios de clase actualizados?", "respuesta": "En SIGU, opción matrícula.", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Qué hago si tengo cruce de horario o un curso no aparece en mi matrícula?", "respuesta": "Escribir a Coordinación Académica con código y detalle (FAQ).", "categoria": "A", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cuánto cuesta el carné universitario y cómo lo solicito?", "respuesta": "S/30.00; registrar pedido en SIGU UMA (FAQ).", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "Perdí mi carné, ¿puedo solicitar otro?", "respuesta": "Duplicado por SIGU adjuntando denuncia policial de pérdida o robo (FAQ).", "categoria": "A", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cómo visualizo mi avance curricular?", "respuesta": "SIGU → Académica / Avance curricular (FAQ).", "categoria": "R", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cuáles son los requisitos para tramitar el diploma de bachiller o título?", "respuesta": "", "categoria": "M", "complejidad": "alta", "doc_referencia": "D005", "origen": "faq"},
    {"pregunta": "¿Qué opciones de pago tengo?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Dónde queda tesorería?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cuáles son mis credenciales de ingreso al SIGU UMA?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cómo solicito la reprogramación de una clase o justifico mi inasistencia a una evaluación?", "respuesta": "", "categoria": "A", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cómo puedo visualizar mi asistencia a clases?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cómo puedo acceder a las notas de mis evaluaciones?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Qué debo hacer si no aparecen mis asistencias registradas correctamente?", "respuesta": "", "categoria": "A", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cómo se definen los criterios de evaluación en cada curso?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Qué hacer en caso tenga un reclamo respecto a la nota de una evaluación?", "respuesta": "", "categoria": "A", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Qué debo hacer si tengo problemas para ubicarme en un aula o no aparece el aula asignada?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Qué pasos debo seguir si tengo problemas académicos o necesito orientación adicional?", "respuesta": "", "categoria": "A", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cómo activar mi cuenta Zoom?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cómo accedo al Wi-Fi de la universidad?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Qué hago si no puedo acceder a mi correo institucional?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cuál es la página web para poder acceder a mi correo institucional?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Mis datos en la plataforma son erróneos, me puede ayudar a corregirlos?", "respuesta": "", "categoria": "A", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cómo ingreso mi trámite de diploma?", "respuesta": "", "categoria": "A", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cómo puedo ver el estado de mi trámite ingresado?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Dónde verifico si mi diploma ya está registrado en SUNEDU?", "respuesta": "", "categoria": "A", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cuáles son los requisitos para recoger mi diploma?", "respuesta": "", "categoria": "M", "complejidad": "alta", "doc_referencia": "D005", "origen": "faq"},
    {"pregunta": "¿Dónde puedo descargar mi cronograma de pagos?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Qué descuentos tienen para las cuotas?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Qué medios de pago hay para pagar mis cuotas?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cómo pago mis trámites?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cuál es el horario de atención de Tesorería?", "respuesta": "", "categoria": "A", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    {"pregunta": "¿Cuándo inicia el Proceso 2025-2?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D012", "origen": "faq"},
    # D001 reglamento académico
    {"pregunta": "¿Qué normas regula el reglamento académico de la UMA?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D001", "origen": "documento"},
    {"pregunta": "¿Cómo se organiza el sistema de evaluación según el reglamento académico?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D001", "origen": "documento"},
    {"pregunta": "¿Qué porcentaje de asistencia mínima exige el reglamento académico?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D001", "origen": "documento"},
    {"pregunta": "¿Qué ocurre si un estudiante desaprueba un curso según el reglamento académico?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D001", "origen": "documento"},
    {"pregunta": "¿Existe evaluación sustitutoria en el reglamento académico y bajo qué condiciones?", "respuesta": "", "categoria": "N", "complejidad": "alta", "doc_referencia": "D001", "origen": "documento"},
    {"pregunta": "¿Cómo se define el promedio ponderado en el reglamento académico?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D001", "origen": "documento"},
    {"pregunta": "¿Qué es la reserva de matrícula según la normativa académica?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D001", "origen": "documento"},
    {"pregunta": "¿Qué disposiciones hay sobre retiro de asignaturas?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D001", "origen": "documento"},
    {"pregunta": "¿Qué dice el reglamento académico sobre el régimen de estudios?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D001", "origen": "documento"},
    {"pregunta": "¿Cómo se trata la justificación de inasistencias en el reglamento académico?", "respuesta": "", "categoria": "N", "complejidad": "alta", "doc_referencia": "D001", "origen": "documento"},
    # D002 matrícula
    {"pregunta": "¿Qué condiciones establece el reglamento de matrícula para matricularme?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D002", "origen": "documento"},
    {"pregunta": "¿Cuáles son los requisitos previos a la matrícula según el reglamento general de matrícula?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D002", "origen": "documento"},
    {"pregunta": "¿Qué tipos de matrícula contempla el reglamento de matrícula?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D002", "origen": "documento"},
    {"pregunta": "¿Qué plazos o periodos de matrícula menciona el reglamento de matrícula?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D002", "origen": "documento"},
    {"pregunta": "¿Se puede rectificar la matrícula y bajo qué reglas?", "respuesta": "", "categoria": "N", "complejidad": "alta", "doc_referencia": "D002", "origen": "documento"},
    {"pregunta": "¿Qué obligaciones tiene el estudiante al matricularse?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D002", "origen": "documento"},
    {"pregunta": "¿Qué sucede si no me matriculo en el plazo establecido?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D002", "origen": "documento"},
    {"pregunta": "¿El reglamento de matrícula distingue matrícula regular y extemporánea?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D002", "origen": "documento"},
    # D003 reglamento general
    {"pregunta": "¿Cuál es la finalidad del reglamento general de la UMA 2025?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D003", "origen": "documento"},
    {"pregunta": "¿Qué órganos de gobierno menciona el reglamento general?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D003", "origen": "documento"},
    {"pregunta": "¿Qué derechos y deberes del estudiante recoge el reglamento general?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D003", "origen": "documento"},
    {"pregunta": "¿Cómo se vincula el reglamento general con otros reglamentos específicos?", "respuesta": "", "categoria": "M", "complejidad": "alta", "doc_referencia": "D003", "origen": "documento"},
    {"pregunta": "¿Qué disposiciones generales aplican a la comunidad universitaria según el reglamento general?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D003", "origen": "documento"},
    # D004 económico
    {"pregunta": "¿Qué regula el reglamento económico universitario?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D004", "origen": "documento"},
    {"pregunta": "¿Cuáles son las obligaciones de pago del estudiante según el reglamento económico?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D004", "origen": "documento"},
    {"pregunta": "¿Qué consecuencias tiene el incumplimiento de pagos según el reglamento económico?", "respuesta": "", "categoria": "N", "complejidad": "alta", "doc_referencia": "D004", "origen": "documento"},
    {"pregunta": "¿Existen fraccionamientos o facilidades de pago en el reglamento económico?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D004", "origen": "documento"},
    {"pregunta": "¿Cómo se relacionan las tasas del tarifario con el reglamento económico?", "respuesta": "", "categoria": "M", "complejidad": "alta", "doc_referencia": "D004", "origen": "documento"},
    # D005 grados y títulos
    {"pregunta": "¿Qué requisitos exige el reglamento de grados y títulos para el bachiller?", "respuesta": "", "categoria": "N", "complejidad": "alta", "doc_referencia": "D005", "origen": "documento"},
    {"pregunta": "¿Qué requisitos exige el reglamento de grados y títulos para el título profesional?", "respuesta": "", "categoria": "N", "complejidad": "alta", "doc_referencia": "D005", "origen": "documento"},
    {"pregunta": "¿Qué base legal cita el reglamento de grados y títulos?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D005", "origen": "documento"},
    {"pregunta": "¿Cómo se gestiona el trámite de grados a través del SIGU según el reglamento?", "respuesta": "", "categoria": "M", "complejidad": "alta", "doc_referencia": "D005", "origen": "documento"},
    {"pregunta": "¿Qué documentos debo presentar para optar el grado de bachiller?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D005", "origen": "documento"},
    {"pregunta": "¿Hay plazos o etapas en el procedimiento de grados y títulos?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D005", "origen": "documento"},
    # D006 admisión
    {"pregunta": "¿Qué modalidades de admisión contempla el reglamento de admisión de pregrado?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D006", "origen": "documento"},
    {"pregunta": "¿Cuáles son los requisitos generales para postular a pregrado?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D006", "origen": "documento"},
    {"pregunta": "¿Qué documentos se exigen en el proceso de admisión?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D006", "origen": "documento"},
    {"pregunta": "¿Cómo se determina el ingreso según el reglamento de admisión?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D006", "origen": "documento"},
    {"pregunta": "¿Existe admisión por traslado o egresados de otras instituciones?", "respuesta": "", "categoria": "N", "complejidad": "alta", "doc_referencia": "D006", "origen": "documento"},
    # D007 becas
    {"pregunta": "¿Qué tipos de beca contempla el reglamento de becas?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D007", "origen": "documento"},
    {"pregunta": "¿Cuáles son los requisitos para solicitar una beca?", "respuesta": "", "categoria": "N", "complejidad": "alta", "doc_referencia": "D007", "origen": "documento"},
    {"pregunta": "¿Cómo se solicita una beca según el reglamento?", "respuesta": "", "categoria": "A", "complejidad": "media", "doc_referencia": "D007", "origen": "documento"},
    {"pregunta": "¿Qué obligaciones mantiene el becario?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D007", "origen": "documento"},
    {"pregunta": "¿En qué casos se pierde o suspende una beca?", "respuesta": "", "categoria": "N", "complejidad": "alta", "doc_referencia": "D007", "origen": "documento"},
    # D008 tutoría
    {"pregunta": "¿Qué es el sistema de tutoría universitaria según el reglamento?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D008", "origen": "documento"},
    {"pregunta": "¿Cuáles son las funciones del docente tutor?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D008", "origen": "documento"},
    {"pregunta": "¿Cómo se asigna un tutor al estudiante?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D008", "origen": "documento"},
    {"pregunta": "¿La tutoría puede realizarse de forma virtual?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D008", "origen": "documento"},
    {"pregunta": "¿Qué obligaciones tiene el estudiante respecto a la tutoría?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D008", "origen": "documento"},
    # D009 convalidaciones
    {"pregunta": "¿Puedo convalidar un curso cursado en otra universidad?", "respuesta": "", "categoria": "N", "complejidad": "alta", "doc_referencia": "D009", "origen": "documento"},
    {"pregunta": "¿Qué principios rigen la convalidación o reconocimiento de cursos?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D009", "origen": "documento"},
    {"pregunta": "¿Qué documentos se requieren para solicitar convalidación?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D009", "origen": "documento"},
    {"pregunta": "¿Quién evalúa la equivalencia de contenidos en una convalidación?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D009", "origen": "documento"},
    {"pregunta": "¿Qué ocurre si faltan prerrequisitos al convalidar?", "respuesta": "", "categoria": "M", "complejidad": "alta", "doc_referencia": "D009", "origen": "documento"},
    # D011 tarifario
    {"pregunta": "¿Dónde consulto las tasas educativas vigentes 2025?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "D011", "origen": "documento"},
    {"pregunta": "¿Qué servicios académicos tienen tarifa publicada en el tarifario 2025?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D011", "origen": "documento"},
    {"pregunta": "¿El tarifario indica montos para trámites de grados o certificados?", "respuesta": "", "categoria": "N", "complejidad": "media", "doc_referencia": "D011", "origen": "documento"},
    {"pregunta": "¿Cómo se relaciona el costo del carné con el tarifario oficial?", "respuesta": "", "categoria": "M", "complejidad": "media", "doc_referencia": "D011", "origen": "documento"},
    # Malla demo / tools
    {"pregunta": "¿Cuáles son los prerrequisitos del curso C103 según el grafo de malla de demostración?", "respuesta": "Definidos en malla_demo_grafo.json (demostración).", "categoria": "R", "complejidad": "media", "doc_referencia": "malla_demo_grafo", "origen": "malla_demo"},
    {"pregunta": "¿Puedo llevar el curso C201 con el perfil demo P01 según el grafo?", "respuesta": "Depende de cursos aprobados en perfiles_demo.json y reglas del grafo.", "categoria": "R", "complejidad": "alta", "doc_referencia": "malla_demo_grafo", "origen": "malla_demo"},
    {"pregunta": "¿Qué cursos desbloquea C101 en el grafo de demostración?", "respuesta": "", "categoria": "R", "complejidad": "baja", "doc_referencia": "malla_demo_grafo", "origen": "malla_demo"},
    {"pregunta": "¿Existe un camino curricular sugerido hacia C301 en el grafo demo?", "respuesta": "", "categoria": "R", "complejidad": "alta", "doc_referencia": "malla_demo_grafo", "origen": "malla_demo"},
    # Mixtas / vacíos conocidos
    {"pregunta": "¿Qué dice el reglamento académico sobre evaluación y asistencia en conjunto con la FAQ?", "respuesta": "", "categoria": "M", "complejidad": "alta", "doc_referencia": "D001", "origen": "documento"},
    {"pregunta": "¿Puedo matricularme si tengo deuda según reglamento de matrícula y reglamento económico?", "respuesta": "", "categoria": "M", "complejidad": "alta", "doc_referencia": "D002", "origen": "documento"},
    {"pregunta": "¿Cuál es la fecha exacta de inicio de clases del ciclo actual en un calendario oficial de la facultad?", "respuesta": "", "categoria": "N", "complejidad": "baja", "doc_referencia": "pendiente_calendario", "origen": "documento"},
    {"pregunta": "¿Cuáles son los prerrequisitos oficiales del plan de estudios de Ingeniería de la facultad?", "respuesta": "", "categoria": "R", "complejidad": "alta", "doc_referencia": "pendiente_malla_oficial", "origen": "documento"},
    {"pregunta": "¿Cómo combino requisitos de bachiller del D005 con tasas del tarifario D011?", "respuesta": "", "categoria": "M", "complejidad": "alta", "doc_referencia": "D005", "origen": "documento"},
    {"pregunta": "¿La guía de proceso de matrícula D010 aporta pasos operativos adicionales al reglamento D002?", "respuesta": "", "categoria": "M", "complejidad": "alta", "doc_referencia": "D010", "origen": "documento"},
]


def _parse_faq_questions(html: str) -> list[str]:
    """Extract question-like strings from FAQ HTML, filtered."""
    found = re.findall(r"¿[^?<]{10,180}\?", html)
    seen: set[str] = set()
    out: list[str] = []
    for q in found:
        qn = re.sub(r"\s+", " ", q).strip()
        low = qn.lower()
        if any(s in low for s in FAQ_SKIP_SUBSTRINGS):
            continue
        if len(qn) < 15:
            continue
        key = _norm_question(qn)
        if key in seen:
            continue
        seen.add(key)
        out.append(qn)
    return out


def _classify_faq_question(pregunta: str) -> tuple[str, str, str]:
    """Return (categoria, complejidad, doc_referencia) heuristics for FAQ items."""
    p = pregunta.lower()
    if any(k in p for k in ("prerreq", "malla", "avance curricular", "curricul")):
        return "R", "media", "D012"
    if any(k in p for k in ("sigu", "correo", "zoom", "wi-fi", "wifi", "tesorer", "carné", "carnet", "aula", "horario", "pago", "cuota", "trámite", "tramite", "diploma", "sunedu")):
        return "A", "baja" if len(p) < 70 else "media", "D012"
    if any(k in p for k in ("beca", "convalid", "matrícul", "matricul", "inasist", "examen", "evalua", "admis")):
        return "N", "media", "D012"
    return "N", "baja", "D012"


def _to_record(item: dict[str, str], idx: int) -> QuestionRecord:
    cat = item["categoria"]
    resp = item.get("respuesta", "")
    doc = item.get("doc_referencia", "D012")
    flags = _flags(cat, doc)
    return QuestionRecord(
        query_id=f"Q{idx:03d}",
        pregunta=item["pregunta"],
        categoria=cat,
        complejidad=item.get("complejidad", "media"),
        doc_referencia=doc,
        seccion_referencia=item.get("seccion_referencia", ""),
        respuesta_esperada=resp,
        requiere_herramienta=flags["requiere_herramienta"],
        requiere_multiples_fuentes=flags["requiere_multiples_fuentes"],
        es_respondible=flags["es_respondible"],
        validacion_experta="draft",
        candidate_strategy=item.get("candidate_strategy") or _infer_strategy(cat),
        origen=item.get("origen", "documento"),
    )


def build_pilot_bank(*, target_n: int = TARGET_N) -> Path:
    """Build deduplicated piloto CSV with at least ``target_n`` rows when possible."""
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_SYN.parent.mkdir(parents=True, exist_ok=True)

    pool: list[dict[str, str]] = []
    seen: set[str] = set()

    def _add(item: dict[str, str]) -> None:
        key = _norm_question(item["pregunta"])
        if key in seen:
            return
        seen.add(key)
        pool.append(item)

    for item in CURATED:
        _add(item)

    faq_raw: list[str] = []
    if FAQ_HTML.exists():
        html = FAQ_HTML.read_text(encoding="utf-8", errors="replace")
        faq_raw = _parse_faq_questions(html)
        with OUT_SYN.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["query_id", "pregunta", "doc_referencia", "validacion_experta", "nota"],
            )
            writer.writeheader()
            for i, q in enumerate(faq_raw, start=1):
                writer.writerow(
                    {
                        "query_id": f"S{i:03d}",
                        "pregunta": q,
                        "doc_referencia": "D012",
                        "validacion_experta": "draft",
                        "nota": "Extraída de FAQ HTML; sin respuesta de referencia.",
                    }
                )
        LOGGER.info("synthetic FAQ list -> %s (%d)", OUT_SYN, len(faq_raw))

        for q in faq_raw:
            cat, comp, doc = _classify_faq_question(q)
            _add(
                {
                    "pregunta": q,
                    "respuesta": "",
                    "categoria": cat,
                    "complejidad": comp,
                    "doc_referencia": doc,
                    "origen": "faq",
                }
            )

    if len(pool) < target_n:
        LOGGER.warning(
            "piloto tiene %d filas tras deduplicar (objetivo %d); se exporta el máximo disponible",
            len(pool),
            target_n,
        )

    rows = [_to_record(item, i) for i, item in enumerate(pool, start=1)]
    # Drop `origen` from public CSV? Keep it — useful for EDA. Schema from GPT doesn't include it
    # but it's metadata; include for transparency.
    fieldnames = list(QuestionRecord.model_fields.keys())
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.model_dump())

    LOGGER.info("pilot bank -> %s (%d unique)", OUT_CSV, len(rows))
    return OUT_CSV


def main() -> None:
    """CLI entry."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    build_pilot_bank()


if __name__ == "__main__":
    main()
