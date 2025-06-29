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

## Module API contracts

| Module | Public call | Input type(s) | Output |
| ------ | ----------- | ------------- | ------ |
| extractor | `extract_sections(pdf_path)` | `pdf_path`: `str` or `Path` to a local PDF file | `dict[str, str]` mapping section name → raw text |
| parser | `get_target_sections(sections)` | `sections`: dict from extractor | `(results:str, conclusion:str, fig_caps:list[str])` |
| evaluator | `score(results, conclusion)` | two strings from parser | `(score:int, justification:str)` |
| figmatcher | `supports(conclusion, figure_captions)` | `conclusion`: str sentence(s); `figure_captions`: list[str] | `dict[str,bool]` mapping each claim → support flag |
| pipeline | `_process(pdf_path)` / Typer CLI | `pdf_path`: Path | dict with keys `score`, `justification`, `fig_support`, `pdf` |

Use these simple, pure-function contracts to keep modules decoupled.

## Environment variables
See `.env.example` for the exact names.  We **never** commit secrets.

---
© 2025 Paper-Eval Team – MIT License
