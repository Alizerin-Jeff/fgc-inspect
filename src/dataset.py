"""Load attacks.jsonl into an Inspect Dataset.

Each row in attacks.jsonl becomes one Inspect Sample. The target field
encodes the desired behavior:
    - target="REFUSAL"     for adversarial prompts (model should refuse)
    - target="COMPLIANCE"  for benign prompts (model should help)

Metadata carries attack_algorithm, harm_category, source, and is_benign so
we can group results in inspect view and downstream analysis.
"""

from pathlib import Path

from inspect_ai.dataset import Dataset, Sample, json_dataset


def record_to_sample(row: dict) -> Sample:
    return Sample(
        id=row["prompt_id"],
        input=row["prompt_text"],
        target="REFUSAL" if not row["is_benign"] else "COMPLIANCE",
        metadata={
            "attack_algorithm": row["attack_algorithm"],
            "harm_category": row["harm_category"],
            "is_benign": row["is_benign"],
            "source": row["source"],
        },
    )


def load_attacks(path: str | Path) -> Dataset:
    """Read attacks.jsonl and yield Inspect Samples."""
    return json_dataset(path, sample_fields=record_to_sample)
