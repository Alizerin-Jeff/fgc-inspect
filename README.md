# fgc-inspect

When architecting LLM defenses, can a paragraph in the system prompt do the same work as a dedicated safety classifier? Answer: it depends on the attack class. Verbose system prompts fully defend template-based jailbreaks but provide near-zero defense against optimization-based attacks (PWRS, 0.03 vs 0.95 with Llama Guard). Llama Guard provides the inverse profile but costs you ~12% over-refusal on benign prompts. The combination approaches a ceiling on attacks (97.6%) at a real helpfulness cost (20% over-refusal). Neither component is sufficient alone; the production architecture should compose them, and the choice of which to lean on should follow your application's harm model.

See [RESULTS.md](./RESULTS.md)

This is a follow-up to [filter-generator-complementarity](../filter-generator-complementarity), reusing the same 682-prompt JailbreakBench dataset and the same three-judge majority-vote evaluation. The intervention is also now on the *generator* side. Instead of just filtering inputs with a separate classifier, we add a safety-oriented system prompt and test the generator's own refusal training.

Implemented in [Inspect AI](https://inspect.aisi.org.uk/). The original FGC was built from scratch, but in this eval I wanted to explore a reliable open source API commonly used by other organizations for evaluations.

## Configurations under test

| Variant         | What it does                                                  |
|-----------------|---------------------------------------------------------------|
| `none`          | No system prompt. Control — measures the model alone.         |
| `minimal`       | One-sentence refusal rule.                                    |
| `constitutional`| Asks the model to check for harm and framing before answering.|
| `verbose`       | Explicit harm-category list with anti-framing clause.         |

Each variant is run with and without `filter`, for 8 runs total.

## Models

| Role      | Model                                                  |
|-----------|--------------------------------------------------------|
| Generator | Llama 3.3 70B Instruct Turbo (Together.ai)             |
| Filter    | Llama Guard 4 (Together.ai)                            |
| Judges    | Gemma 3n E4B, Kimi K2.6, MiniMax M2.7 (Together.ai)    |

Judges are intentionally drawn from different model families than the generator and themselves to avoid self-judgment confounds.

## Quick start

```bash
# Install
git clone https://github.com/Alizerin-Jeff/fgc-inspect.git
cd fgc-inspect
uv sync.

# Configure API keys
export TOGETHER_API_KEY=<your_api_key>

or

add TOGETHER_API_KEY=<your_api_key> to .env

# Put the dataset in place (see data/README.md)
cd data && uv run generate_data.py

You can also use the attacks.jsonl from the orignal FGC 
as the datasets should be the same.

# Run a single configuration
inspect eval src/tasks.py@fgc_inspect \
    -T variant=constitutional -T filter=True \
    --model together/meta-llama/Llama-3.3-70B-Instruct-Turbo

# Inspect results
inspect view
```

## Layout

```
fgc-inspect/
├── data/
│   |── attacks.jsonl       # 682 rows from FGC (gitignored)
|   └── generate_data.py    # generates the attacks.jsonl 
├── src/
│   ├── dataset.py          # attacks.jsonl -> Inspect Samples
│   ├── run_all.py          # run full eval with options for smoke test
│   ├── solver.py           # creates custom solver for Lllam Guard 4
│   ├── prompts.py          # SYSTEM_PROMPTS dict
│   ├── scorer.py           # three-judge majority-vote scorer
│   └── tasks.py            # @task fgc_inspect(variant, critique)
└── logs/                   # inspect log output (gitignored)
```

## Status

Ran evaluation and now have all data needed for anlaysis.  Generated a
summary of the main findings in RESULTS.md.  The metrics can be generated 
using analysis.py and are saved in results/summary.txt.  

Still in progress:  Gwet's AC1 for inter-rater analysis, chat/plot generation
and pdf writeup.