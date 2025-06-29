# AI Paper Evaluator

A modular toolkit that scores scientific papers (0-100) based on how well each paper’s **Conclusions** are backed up by its **Results** and supporting **Figures**.

Five loosely-coupled sub-packages allow a distributed team to work in parallel:

| Module | Owner | Purpose |
| ------ | ----- | ------- |
| `extractor` | Person A | Convert PDF → structured text sections |
| `parser` | Person B | Locate *Results*, *Conclusions*, figure captions |
| `evaluator` | Person C | Use an LLM to score consistency |
| `figmatcher` | Person D | Check which conclusion claims are backed by figures |
| `pipeline` | Person E | Glue everything together & expose CLI / dashboard |

## Quick start (local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then add your API keys
python -m paper_eval.pipeline.run_pipeline /path/to/paper.pdf
```

## Folder layout
```
ai-paper-evaluator/
├── src/paper_eval/ …  (package code)
├── data/             …  small sample PDFs & outputs
├── tests/            …  pytest suites
```

Each source file is < 400 LOC for readability.

## Environment variables
See `.env.example` for the exact names.  We **never** commit secrets.

---
© 2025 Paper-Eval Team – MIT License
