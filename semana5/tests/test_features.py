"""Pruebas del extractor de características de consultas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from thesis_routing.features.feature_pipeline import build_feature_table
from thesis_routing.features.intent_features import extract_intent_features
from thesis_routing.features.retrieval_features import build_retrieval_feature_table
from thesis_routing.features.text_features import extract_text_features


def test_text_features_direct_question() -> None:
    features = extract_text_features("¿Cuándo empiezan las clases?")
    assert features["query_length_words"] == 4
    assert features["question_mark_count"] == 1
    assert features["has_multiple_questions"] == 0
    assert features["contains_negation"] == 0
    assert features["contains_condition"] == 0
    assert features["contains_comparison"] == 0


def test_condition_is_a_word_not_a_substring() -> None:
    """'si' condicional no debe dispararse dentro de 'asistencia'."""
    plain = extract_text_features("¿Cómo puedo visualizar mi asistencia a clases?")
    conditional = extract_text_features("¿Puedo matricularme si desaprobé un curso?")
    assert plain["contains_condition"] == 0
    assert conditional["contains_condition"] == 1
    assert conditional["contains_negation"] == 0


def test_negation_and_multiple_questions() -> None:
    features = extract_text_features(
        "No he aprobado el curso. ¿Cuándo es la matrícula? ¿Qué requisitos necesito?"
    )
    assert features["contains_negation"] == 1
    assert features["has_multiple_questions"] == 1


def test_intent_prereq_and_payment() -> None:
    prereq = extract_intent_features("¿Puedo llevar un curso sin aprobar su prerrequisito?")
    payment = extract_intent_features("¿Cuánto cuesta el carné universitario?")
    assert prereq["intent_category"] == "prerrequisitos"
    assert prereq["requires_rule_validation"] == 1
    assert payment["intent_category"] == "pagos"
    assert payment["requires_calculation"] == 1
    assert payment["contains_administrative_entity"] == 1


def test_pipeline_keeps_labels_apart_from_features() -> None:
    frame = pd.DataFrame(
        {
            "query_id": ["Q1"],
            "pregunta": ["¿Qué requisitos tiene la matrícula?"],
            "complejidad": ["media"],
            "candidate_strategy": ["A1"],
        }
    )
    out = build_feature_table(frame)
    assert out.loc[0, "contains_condition"] == 0
    assert out.loc[0, "intent_category"] == "matricula"
    assert out.loc[0, "candidate_strategy"] == "A1"
    assert "top1_retrieval_score" not in out.columns


def test_bm25_prefers_the_document_that_shares_terms(tmp_path: Path) -> None:
    text_dir = tmp_path / "txt"
    text_dir.mkdir()
    (text_dir / "D001.txt").write_text(
        "reglamento de matricula requisitos de matricula regular del ciclo academico " * 8,
        encoding="utf-8",
    )
    (text_dir / "D004.txt").write_text(
        "reglamento economico pensiones cuotas de pago y tesoreria universitaria " * 8,
        encoding="utf-8",
    )
    (text_dir / "D012.txt").write_text(
        "preguntas frecuentes correo institucional wifi zoom horarios de clase " * 8,
        encoding="utf-8",
    )
    inventory = pd.DataFrame(
        {
            "doc_id": ["D001", "D004", "D012"],
            "estado_extraccion": ["ok", "ok", "ok"],
        }
    )
    queries = pd.Series(["¿Cuáles son los requisitos de matrícula del ciclo?"])
    features = build_retrieval_feature_table(queries, text_dir, inventory)
    assert features.loc[0, "top1_doc_id"] == "D001"
    assert float(features.loc[0, "top1_retrieval_score"]) > 0
    assert int(features.loc[0, "retrieved_document_count"]) >= 1
