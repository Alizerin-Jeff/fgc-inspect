"""Custom solvers for creating a multi agent system.

The starting point is just LlamaGuard 4 as an input
filter.
"""

from inspect_ai.solver import solver, Solver, TaskState, Generate
from inspect_ai.model import get_model,  ModelOutput

LLAMA_GUARD = "together/meta-llama/Llama-Guard-4-12B"

@solver
def llama_guard_filter() -> Solver:
    """ Simple small classifier model that
    will decide if the incoming prompt is safe
    or unsafe.  If unsafe, the conversation is
    terminated with a harded coded response."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        lg = get_model(LLAMA_GUARD)
        verdict = (await lg.generate(state.user_prompt.text)).completion
        if "unsafe" in verdict:
            state.output = ModelOutput.from_content(
                model=LLAMA_GUARD,
                content="I cannnot help with that request."
            )
            state.completed = True
        return state
    return solve
