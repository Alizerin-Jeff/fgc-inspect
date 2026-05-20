"""Aggregate and summarize the fgc-inspect runs.

Loads every successful .eval log from logs/, groups samples by population
(attack vs benign) and by attack algorithm, and prints three tables:

  1. Headline accuracy: variant × filter × {attacks, benign, all}
  2. Per-attack-algorithm accuracy (filter=False only — filter adds
     noise on top of the variant effect, so cleaner without it).
  3. Over-refusal vs attack-defense trade-off (filter=False only).

Run from the experiment root:

    uv run python analysis.py
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from inspect_ai.log import list_eval_logs, read_eval_log


LOG_DIR = "logs"
SCORER_NAME = "three_judge_majority"
VARIANTS = ["none", "minimal", "constitutional", "verbose"]


def load_runs() -> dict[tuple[str, bool], Any]:
    """Return {(variant, filter): latest_successful_log}."""
    runs: dict[tuple[str, bool], Any] = {}
    for info in list_eval_logs(LOG_DIR):
        log = read_eval_log(info.name)
        if log.status != "success":
            continue
        args = log.eval.task_args or {}
        variant = args.get("variant")
        if variant is None:
            continue
        key = (variant, bool(args.get("filter", False)))
        # Keep the most recent log per config — handles resumes / reruns.
        if key not in runs or log.eval.created > runs[key].eval.created:
            runs[key] = log
    return runs


def per_sample(log) -> list[tuple[float, dict]]:
    """Yield (score_value, sample_metadata) for every scored sample."""
    out = []
    for sample in log.samples:
        score = sample.scores.get(SCORER_NAME)
        if score is None:
            continue
        out.append((score.value, sample.metadata or {}))
    return out


def acc(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def by_population(log) -> dict[str, float]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for value, meta in per_sample(log):
        pop = "benign" if meta.get("is_benign") else "attack"
        buckets[pop].append(value)
        buckets["all"].append(value)
    return {k: acc(v) for k, v in buckets.items()}


def by_algorithm(log) -> dict[str, float]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for value, meta in per_sample(log):
        if meta.get("is_benign"):
            continue
        algo = meta.get("attack_algorithm", "unknown")
        buckets[algo].append(value)
    return {k: acc(v) for k, v in buckets.items()}


# ---------- printers ----------


def print_headline(runs):
    print("\n=== Accuracy: variant × filter × population ===\n")
    header = f"{'variant':<16}{'filter':<10}{'attacks':>10}{'benign':>10}{'all':>10}"
    print(header)
    print("-" * len(header))
    for variant in VARIANTS:
        for filter in (False, True):
            log = runs.get((variant, filter))
            if log is None:
                print(f"{variant:<16}{str(filter):<10}{'--':>10}{'--':>10}{'--':>10}")
                continue
            s = by_population(log)
            print(
                f"{variant:<16}{str(filter):<10}"
                f"{s.get('attack', float('nan')):>10.3f}"
                f"{s.get('benign', float('nan')):>10.3f}"
                f"{s.get('all', float('nan')):>10.3f}"
            )


def print_by_algorithm(runs):
    print("\n=== Attack-defense accuracy by algorithm (filter=False) ===\n")
    algos: set[str] = set()
    for variant in VARIANTS:
        log = runs.get((variant, False))
        if log is not None:
            algos.update(by_algorithm(log).keys())
    algo_list = sorted(algos)
    # Per-column width: at least 14, or enough to fit the label + 2 padding.
    widths = {a: max(14, len(a) + 2) for a in algo_list}

    header = f"{'variant':<16}" + "".join(f"{a:>{widths[a]}}" for a in algo_list)
    print(header)
    print("-" * len(header))
    for variant in VARIANTS:
        log = runs.get((variant, False))
        if log is None:
            continue
        s = by_algorithm(log)
        row = f"{variant:<16}" + "".join(
            f"{s.get(a, float('nan')):>{widths[a]}.3f}" for a in algo_list
        )
        print(row)


def print_tradeoff(runs):
    print("\n=== Attack-defense vs over-refusal (filter=False) ===\n")
    header = f"{'variant':<16}{'attack_defense':>16}{'over_refusal':>16}"
    print(header)
    print("-" * len(header))
    for variant in VARIANTS:
        log = runs.get((variant, False))
        if log is None:
            continue
        s = by_population(log)
        attack = s.get("attack", float("nan"))
        benign = s.get("benign", float("nan"))
        print(f"{variant:<16}{attack:>16.3f}{(1 - benign):>16.3f}")


def main():
    runs = load_runs()
    if not runs:
        raise SystemExit(f"No successful runs found in {LOG_DIR}/")
    print(f"Loaded {len(runs)} runs: {sorted(runs.keys())}")
    print_headline(runs)
    print_by_algorithm(runs)
    print_tradeoff(runs)


if __name__ == "__main__":
    main()
