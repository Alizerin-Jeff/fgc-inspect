"""
This is a contracted version from the original FGC
experiemnt which wrote the eval pipline from scratch.
This eval uses Inspect AI and will only need the few
Classes for the data generation pipeline.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


# ---------- Enums: controlled vocabularies ----------


class AttackAlgorithm(str, Enum):
    """How the adversarial prompt was generated."""

    PAIR = "PAIR"  # LLM-generated social engineering (Chao et al.)
    GCG = "GCG"  # Gradient suffix (Zou et al.)
    JAILBREAKCHAT = "JBC"  # Human-crafted template
    DSN = "DSN"  # Do-Something-Now prompts
    PWRS = "prompt_with_random_search"  # Random token search
    DIRECT = "direct"  # No attack scaffolding — base behavior
    BENIGN = "benign"  # Not an attack; benign lookalike


class HarmCategory(str, Enum):
    """OpenAI-policy-style harm taxonomy, as used by JailbreakBench."""

    MALWARE = "Malware/Hacking"
    HARASSMENT = "Harassment/Discrimination"
    MISINFORMATION = "Disinformation"
    PRIVACY = "Privacy"
    FRAUD = "Fraud/Deception"
    EXPERT_ADVICE = "Expert advice"
    HARM = "Physical harm"
    ECONOMIC = "Economic harm"
    GOVERNMENT_DECISION_MAKING = "Government decision-making"
    SEXUAL_CONTENT = "Sexual/Adult content"
    NONE = "none"  # for benign prompts


class Source(str, Enum):
    """Which JailbreakBench split a prompt came from."""

    JBB_ARTIFACTS = "jbb_artifacts"  # attack-algorithm artifact prompts
    JBB_BASE = "jbb_base"  # direct harmful requests, no scaffolding
    JBB_BENIGN = "jbb_benign"  # benign lookalikes (false-positive control)


# ---------- Core data models ----------


class Prompt(BaseModel):
    """One row of the merged dataset."""

    prompt_id: str = Field(..., description="Stable ID, e.g. 'jbb_pair_042'")
    source: Source
    attack_algorithm: AttackAlgorithm
    harm_category: HarmCategory
    prompt_text: str
    is_benign: bool
