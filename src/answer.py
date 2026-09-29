"""The shared answer format returned by BOTH pipelines."""
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

Status = Literal["unique", "multiple", "none", "optimal"]


class Answer(BaseModel):
    """What run.py saves and evaluate.py checks.

    status:    "unique"   - exactly one solution exists
               "multiple" - more than one solution exists
               "none"     - no solution satisfies all conditions
               "optimal"  - optimisation problem; `solution` is the best one
    solution:  shape is defined by the problem's `answer_format`
    objective: value of the best solution (optimisation problems only)
    """
    status: Status
    solution: dict[str, Any] = Field(default_factory=dict)
    objective: Optional[int] = None


class ReasonedAnswer(BaseModel):
    """Answer with a free-text reasoning field placed FIRST, so the model reasons before it commits.

    Field order matters: the model generates JSON fields in schema order.
    """
    reasoning: str
    status: Status
    solution: dict[str, Any] = Field(default_factory=dict)
    objective: Optional[int] = None

    def to_answer(self) -> Answer:
        return Answer(status=self.status, solution=self.solution, objective=self.objective)
