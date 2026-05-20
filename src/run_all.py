"""
Run full eval pipline across 8 configurations:
4 variants and citique True/Flase
"""

from inspect_ai import eval
from tasks import fgc_inspect

MODEL = "together/meta-llama/Llama-3.3-70B-Instruct-Turbo"
VARIANTS = ["none", "constitutional", "minimal", "verbose"]
FILTER = [False, True]
LIMIT = 50

for filter in FILTER:
    for variant in VARIANTS:
        print(f"\n=== variant={variant}  filter={filter} ===")
        try:
            result = eval(
                fgc_inspect(variant=variant, filter=filter),
                model=MODEL,
                log_dir="logs/smoke" if LIMIT else "logs",
                limit=LIMIT,
                sample_shuffle=42,

            )
        except Exception as e:
            print("Faile:", e)
            continue