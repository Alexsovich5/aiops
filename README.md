# AIOps Platform with Natural Language Processing

AIOps platform using NLP and machine learning to automatically classify incidents, correlate alerts, and suggest resolutions based on historical patterns. Features BERT-based text classification and FastAPI backend.

Personal project, built to explore alert correlation and incident classification with transformers. It is not production software — see **Status** below for exactly what is and isn't implemented.

## Status

**Implemented**

- FastAPI entrypoint
- Alert correlator grouping related alerts by time window and service
- Incident classifier using a transformer model
- Dockerfile

**Not implemented / known limitations**

- No NLP engine or BERT classifier module (the earlier README claimed these; they did not exist)
- Model is used untuned — no training or evaluation code
- No tests

## Built with

- **Python** — tensorflow, transformers, fastapi, uvicorn, redis, numpy, scikit-learn, PyYAML

## Running it

```bash
pip install -r requirements.txt
python src/main.py
```

## Layout

```
Dockerfile
requirements.txt
src/
  alert_correlator.py
  incident_classifier.py
  main.py
```

