# investigacion2

Proyecto de Investigación II — Maestría en Ciencias con mención en Inteligencia Artificial (FIIS–UNI).

Tema: enrutamiento predictivo de estrategias de atención para consultas académico-administrativas (caso UMA–SJL).

## Carpetas

| Ruta | Contenido |
|------|-----------|
| `semana2/` | Diseño del pipeline experimental (doce fases, A0–A5) |
| `semana3/` | Esqueleto previo / baseline BM25 |
| `semana4/` | Corpus UMA, banco piloto y EDA preliminar |
| `semana5/` | Feature engineering del banco piloto (texto, reglas de intención, BM25) |
| `semana6/` | A/B de conjuntos F0/F1/F2 |
| `semana7/` | Importancia de variables sobre F1 |
| `semana8/` | Optimización de hiperparámetros (Random + Optuna TPE) |

## Semana 4

```bash
cd semana4
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make eda
```

Documentación de partida: `semana4/README.md` y `semana4/reports/eda/`.
