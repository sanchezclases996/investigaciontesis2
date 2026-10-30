.PHONY: install eda prepare data index experiment evaluate report test lint tree features

install:
	python3.11 -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -e ".[dev]"

# Semana 4: datos ANTES del EDA
data:
	. .venv/bin/activate && python -m thesis_routing.pipeline.prepare_data

eda:
	bash scripts/run_eda.sh

features:
	. .venv/bin/activate && pytest -q tests/test_features.py

prepare: data
	bash scripts/prepare_dataset.sh

index:
	. .venv/bin/activate && python -m thesis_routing.pipeline.build_index

experiment:
	bash scripts/run_all_experiments.sh

evaluate:
	. .venv/bin/activate && python -m thesis_routing.pipeline.evaluate_results

report:
	. .venv/bin/activate && python -m thesis_routing.pipeline.generate_report

test:
	. .venv/bin/activate && pytest -q

lint:
	. .venv/bin/activate && ruff check src tests

tree:
	find . -path ./.venv -prune -o -path ./.git -prune -o -print | head -200
