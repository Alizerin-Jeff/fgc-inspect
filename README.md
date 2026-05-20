# fgc-inspect

Can a simple system prompt match Llama Guard at blocking jailbreaks?

Follow-up to [filter-generator-complementarity](../filter-generator-complementarity), reusing the same 682-prompt JailbreakBench dataset and the same three-judge majority-vote evaluation. The intervention is on the *generator* side: instead of filtering inputs with a separate classifier, we add a safety-oriented system prompt and let the generator's own refusal training do the work.

Implemented in [Inspect AI](https://inspect.aisi.org.uk/) so this also serves as a working example of an Inspect-native safety eval.

## Configurations under test

| Variant         | What it does                                                  |
|-----------------|---------------------------------------------------------------|
| `none`          | No system prompt. Control — measures the model alone.         |
| `minimal`       | One-sentence refusal rule.                                    |
| `constitutional`| Asks the model to check for harm and framing before answering.|
| `verbose`       | Explicit harm-category list with anti-framing clause.         |

Each variant is run with and without `self_critique`, for 8 runs total.

## Models

| Role      | Model                                                  |
|-----------|--------------------------------------------------------|
| Generator | Llama 3.3 70B Instruct Turbo (Together)                |
| Critic    | Qwen3 235B A22B Instruct 2507 FP8 (Together)           |
| Judges    | Gemma 3n E4B, Kimi K2.5, MiniMax M2.7 (Together)       |

Critic and judges are intentionally drawn from different model families than the generator to avoid self-judgment confounds.

## Quick start

```bash
# Install
uv venv && source .venv/bin/activate
uv pip install -e .

# Configure API keys
cp ../filter-generator-complementarity/.env .env   # or create fresh

# Put the dataset in place (see data/README.md)
cp ../filter-generator-complementarity/data/attacks.jsonl data/attacks.jsonl

# Run a single configuration
inspect eval src/tasks.py@fgc_inspect \
    -T variant=constitutional \
    --model together/meta-llama/Llama-3.3-70B-Instruct-Turbo

# Inspect results
inspect view
```

## Layout

```
fgc-inspect/
├── data/
│   └── attacks.jsonl       # 682 rows from FGC (gitignored)
├── src/
│   ├── dataset.py          # attacks.jsonl -> Inspect Samples
│   ├── prompts.py          # SYSTEM_PROMPTS dict
│   ├── scorer.py           # three-judge majority-vote scorer
│   └── tasks.py            # @task fgc_inspect(variant, critique)
└── logs/                   # inspect log output (gitignored)
```

## Status

Scaffold only. Implementation in progress.
