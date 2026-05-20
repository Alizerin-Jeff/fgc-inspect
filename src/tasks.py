"""Inspect tasks for the system-prompt vs Llama-Guard comparison.

One parameterized task lets you swap the system prompt variant and toggle
self-critique without duplicating task definitions. Run from the CLI:

    inspect eval src/tasks.py@fgc_inspect \\
        -T variant=constitutional \\
        --model together/meta-llama/Llama-3.3-70B-Instruct-Turbo

Once the CLI flow works, parameterize from Python by calling eval() in a
loop over (variant, critique) tuples.
"""

from inspect_ai import Task, task
from inspect_ai.solver import generate, system_message, Solver

from prompts import SYSTEM_PROMPTS
from scorer import three_judge_majority
from solver import llama_guard_filter
from dataset import load_attacks


# Critic model for self_critique. Must differ from both the generator and
# the three judges to keep the comparison meaningful.
CRITIC_MODEL = "together/Qwen/Qwen3-235B-A22B-Instruct-2507-tput"


@task
def fgc_inspect(variant: str, filter: bool = False) -> Task:
    """One run of the eval with a given configuration
    (variant, critique).
    """

    solvers: list[Solver] = []
    if variant == "none":
        solvers.append(generate())
    else:
        solvers.extend([system_message(SYSTEM_PROMPTS[variant]), generate()])
    if filter:
        solvers.append(llama_guard_filter())
    return Task(
        dataset=load_attacks("../data/attacks.jsonl"),
        solver=solvers,
        scorer=three_judge_majority(),
    )
