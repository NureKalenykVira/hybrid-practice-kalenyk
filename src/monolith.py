"""MONOLITHIC pipeline: the language model reads the puzzle and answers directly.

This baseline works out of the box. Run it first to make sure everything is wired up:
    python src/run.py --team A --pipeline monolith

TODO(team) - ideas for improving it (optional, see 7.2 in the practical plan):
    * improve the prompt (clearer instructions, a worked example);
    * self-consistency: ask several times with temperature > 0 and take the majority answer;
    * never let the monolith see the solver - it is the baseline you compare the hybrid against.
"""
import llm
from answer import ReasonedAnswer

SYSTEM = "You are a careful solver of logic puzzles. You answer only with JSON."

PROMPT = """Solve the following puzzle.

{text}

First reason step by step in the "reasoning" field. Check every condition against your candidate solution.
Then decide the status:
- "unique"   if exactly one solution satisfies all conditions;
- "multiple" if more than one solution satisfies all conditions;
- "none"     if no solution satisfies all conditions;
- "optimal"  if the problem asks for the best / smallest / largest solution.

{answer_format}
If the status is "none", leave "solution" empty. For optimisation problems, put the value of the best
solution into "objective".
"""


def solve(problem: dict) -> dict:
    """Returns {"answer": <Answer as dict>, "trace": <anything useful for your analysis>}."""
    prompt = PROMPT.format(text=problem["text"], answer_format=problem["answer_format"])
    parsed, raw = llm.ask_json(prompt, ReasonedAnswer, system=SYSTEM)
    return {"answer": parsed.to_answer().model_dump(), "trace": {"reasoning": parsed.reasoning}}
