# fgc-inspect

When architecting LLM defenses, can a paragraph in the system prompt do the same work as a dedicated safety classifier? Answer: it depends on the attack class. Verbose system prompts fully defend template-based jailbreaks but provide near-zero defense against optimization-based attacks (PWRS, 0.03 vs 0.95 with Llama Guard). Llama Guard provides the inverse profile but costs you ~12% over-refusal on benign prompts. The combination approaches a ceiling on attacks (97.6%) at a real helpfulness cost (20% over-refusal). Neither component is sufficient alone; the production architecture should compose them, and the choice of which to lean on should follow your application's harm model.

See [RESULTS.md](./RESULTS.md)

This is a follow-up to [filter-generator-complementarity](https://github.com/Alizerin-Jeff/filter-generator-complementarity), reusing the same 682-prompt JailbreakBench dataset and the same three-judge majority-vote evaluation. The intervention is now on the *generator* side. Instead of just filtering inputs with a separate classifier, we add a safety-oriented system prompt and test the generator's own refusal training.

Implemented in [Inspect AI](https://inspect.aisi.org.uk/). The original FGC was built from scratch, but in this eval I wanted to explore a widely used open source evaluation framework.

## Configurations under test

| Variant         | What it does                                                  |
|-----------------|---------------------------------------------------------------|
| `none`          | No system prompt. Control that measures the model alone.      |
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

Judges are intentionally drawn from different model families than the generator to avoid self-judgment confounds.

## Quick start

Install:

```bash
git clone https://github.com/Alizerin-Jeff/fgc-inspect.git
cd fgc-inspect
uv sync
```

Configure your Together API key, either as an environment variable:

```bash
export TOGETHER_API_KEY=<your_api_key>
```

or in a `.env` file at the repo root:

```
TOGETHER_API_KEY=<your_api_key>
```

Put the dataset in place (see `data/README.md`):

```bash
cd data && uv run generate_data.py
```

You can also copy `attacks.jsonl` from the original FGC repo; the datasets should be identical.

Run a single configuration:

```bash
inspect eval src/tasks.py@fgc_inspect \
    -T variant=constitutional -T filter=True \
    --model together/meta-llama/Llama-3.3-70B-Instruct-Turbo
```

Inspect results:

```bash
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
│   ├── solver.py           # creates custom solver for Llama Guard 4
│   ├── prompts.py          # SYSTEM_PROMPTS dict
│   ├── scorer.py           # three-judge majority-vote scorer
│   └── tasks.py            # @task fgc_inspect(variant, filter)
└── logs/                   # inspect log output (gitignored)
```

## Status

Ran evaluation and now have all data needed for analysis.  Generated a
summary of the main findings in RESULTS.md.  The metrics can be generated 
using analysis.py and are saved in results/summary.txt.  

Still in progress:  Gwet's AC1 for inter-rater analysis, chart/plot generation
and pdf writeup.