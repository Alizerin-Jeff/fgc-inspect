"""
Run full eval pipline across 8 configurations:
4 variants and citique True/Flase
"""

from inspect_ai import eval
from tasks import fgc_inspect

MODEL = "together/meta-llama/Llama-3.3-70B-Instruct-Turbo"
VARIANTS = ["none", "constitutional", "minimal", "verbose"]
CRITIQUES = [False, True]
LIMIT = None

for critique in CRITIQUES:
    for variant in VARIANTS:
        print(f"\n=== variant={variant}  critique={critique} ===")
        try:
            result = eval(
                fgc_inspect(variant=variant, critique=critique),
                model=MODEL,
                log_dir="logs/smoke" if LIMIT else "logs",
                limit=LIMIT,
                sample_shuffle=42,

            )
        except Exception as e:
            print("Faile:", e)
            continue