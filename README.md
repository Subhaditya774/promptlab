# PromptLab — LLM Prompt Evaluation & Benchmarking Platform

> A/B test prompt versions across Claude and GPT-4o. Track quality, cost, latency, and regressions — with a versioned prompt registry and automated LLM-as-judge scoring.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green?style=flat-square)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square)
![Claude](https://img.shields.io/badge/Anthropic-Claude_API-orange?style=flat-square)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green?style=flat-square)

---

## What It Does

PromptLab lets you:

1. **Register** prompt versions with metadata (model, temperature, system prompt, user template)
2. **Run** them against a test suite and score each output using LLM-as-judge
3. **Compare** versions side-by-side — quality score, token cost, latency
4. **Track regressions** automatically — alerts when new version scores below threshold
5. **Roll back** to any previous version instantly

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Chart.js |
| Backend | FastAPI (Python) |
| AI | Claude API + OpenAI API |
| Database | PostgreSQL |
| Eval | LLM-as-judge (Claude claude-sonnet-4-20250514) |

## Getting Started

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
promptlab/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── eval_engine.py       # LLM-as-judge scorer
│   ├── registry.py          # Prompt version registry
│   └── requirements.txt
├── app/                     # Next.js frontend
│   ├── api/
│   │   ├── run/             # Trigger eval run
│   │   └── results/         # Fetch results
│   └── dashboard/           # Comparison UI
├── evals/
│   └── test_cases.json      # 80 structured test cases
└── prompts/
    └── registry.json        # Versioned prompt store
```

## Prompt Registry Format

```json
{
  "version": "v2.1.0",
  "model": "claude-sonnet-4-20250514",
  "temperature": 0.3,
  "system": "You are an expert contract writer...",
  "userTemplate": "Generate a SOW for: {{projectName}}",
  "createdAt": "2025-03-10",
  "evalScore": 89.2,
  "tokenAvg": 1240,
  "latencyAvgMs": 2100,
  "notes": "Added scope ambiguity detection"
}
```

## Running an Eval

```bash
# Run all test cases against current prompt version
python backend/eval_engine.py --version v2.1.0 --test-suite evals/test_cases.json

# Compare two versions
python backend/eval_engine.py --compare v2.0.0 v2.1.0
```

## Results

- Regression detection: 2 hours manual → under 4 minutes automated
- 80 structured test cases across SOW generation, clause analysis, rate benchmarking
- Supports Claude + GPT-4o side-by-side comparison

## License

MIT

