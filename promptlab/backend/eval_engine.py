# backend/eval_engine.py
"""
LLM-as-judge evaluation engine.
Runs a prompt version against a test suite and scores each output.
"""
import json
import time
import argparse
import os
from typing import Any
import anthropic
import openai

client_anthropic = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
client_openai    = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

JUDGE_SYSTEM = """You are an expert evaluator assessing AI-generated outputs for quality.
Score the output on these dimensions (0-10 each):
- accuracy: Does it correctly address the prompt?
- completeness: Are all required elements present?
- clarity: Is the output clear and unambiguous?
- format: Is the output well-structured?

Return ONLY a JSON object: {"accuracy": N, "completeness": N, "clarity": N, "format": N, "overall": N, "issues": ["..."]}
No preamble."""


def run_prompt(version_config: dict, user_input: str) -> tuple[str, float, int]:
    """Run a prompt and return (output, latency_ms, tokens)."""
    start = time.time()
    model = version_config["model"]

    if "claude" in model:
        res = client_anthropic.messages.create(
            model=model,
            max_tokens=2048,
            system=version_config["system"],
            messages=[{"role": "user", "content": version_config["userTemplate"].replace("{{input}}", user_input)}],
        )
        output = res.content[0].text
        tokens = res.usage.input_tokens + res.usage.output_tokens
    else:
        res = client_openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": version_config["system"]},
                {"role": "user",   "content": version_config["userTemplate"].replace("{{input}}", user_input)},
            ],
        )
        output = res.choices[0].message.content or ""
        tokens = res.usage.total_tokens if res.usage else 0

    latency = (time.time() - start) * 1000
    return output, latency, tokens


def judge_output(prompt: str, output: str) -> dict[str, Any]:
    """Score an output using Claude as judge."""
    res = client_anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": f"Prompt: {prompt}\n\nOutput: {output}"}],
    )
    text = res.content[0].text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def run_eval(version_path: str, test_suite_path: str) -> dict[str, Any]:
    """Run full eval suite against a prompt version."""
    with open(version_path) as f:
        version = json.load(f)
    with open(test_suite_path) as f:
        test_cases = json.load(f)

    print(f"\n🔬 Running eval: {version['version']} | Model: {version['model']}")
    print(f"   Test cases: {len(test_cases)}\n")

    scores, latencies, token_counts = [], [], []

    for i, case in enumerate(test_cases):
        output, latency, tokens = run_prompt(version, case["input"])
        scores_raw = judge_output(case["input"], output)

        scores.append(scores_raw["overall"])
        latencies.append(latency)
        token_counts.append(tokens)

        status = "✅" if scores_raw["overall"] >= 7 else "⚠️" if scores_raw["overall"] >= 5 else "❌"
        print(f"  [{i+1:02}/{len(test_cases)}] {status} Score: {scores_raw['overall']}/10 | Latency: {latency:.0f}ms | Tokens: {tokens}")

    avg_score  = sum(scores) / len(scores)
    avg_lat    = sum(latencies) / len(latencies)
    avg_tokens = sum(token_counts) / len(token_counts)

    print(f"\n📊 Results for {version['version']}:")
    print(f"   Avg Score:   {avg_score:.2f}/10  ({avg_score * 10:.1f}/100)")
    print(f"   Avg Latency: {avg_lat:.0f}ms")
    print(f"   Avg Tokens:  {avg_tokens:.0f}")
    print(f"   Regressions: {sum(1 for s in scores if s < 6)}/{len(scores)}")

    return {"version": version["version"], "avgScore": avg_score, "avgLatency": avg_lat, "avgTokens": avg_tokens, "scores": scores}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version",    required=True, help="Path to version JSON")
    parser.add_argument("--test-suite", required=True, help="Path to test cases JSON")
    args = parser.parse_args()
    run_eval(args.version, args.test_suite)
