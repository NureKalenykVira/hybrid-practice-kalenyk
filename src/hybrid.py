"""HYBRID (neuro-symbolic) pipeline:

    problem text --(LLM formalizer)--> IR --(validation)--> Z3 solver --(presentation)--> answer

This is the main thing your team builds. The plumbing is here; the parts marked TODO(team) are yours.
Suggested order of work:
    1. write FORMALIZER_PROMPT and get formalize() returning sensible IR for one simple problem;
    2. implement validate_ir();
    3. add ONE retry with feedback in solve();
    4. fix run_solver() so that "unique" and "multiple" can be told apart;
    5. (extension) replace the LLM-based present() with deterministic code for some problem types.

See docs/ir.md for the IR format.
"""
import ast
import json
import keyword
import re
from typing import Any, Optional

import z3
from pydantic import BaseModel, Field

import ir_solver
import llm
from answer import Answer


class HybridError(Exception):
    """The hybrid pipeline could not produce an answer (recorded by run.py as an error, not as status "none")."""

    def __init__(self, message: str, trace: Optional[dict] = None):
        super().__init__(message)
        self.trace = trace


class Condition(BaseModel):
    text: str
    constraint: str


class IRModel(BaseModel):
    """JSON schema the formalizer must follow. Keep it in sync with docs/ir.md."""
    variables: dict[str, Any] = Field(default_factory=dict)
    all_different: list[list[str]] = Field(default_factory=list)
    conditions: list[Condition] = Field(default_factory=list)
    objective: Optional[dict[str, str]] = None


# Compact IR description for the model. You may edit it, but keep it consistent with ir_solver.py.
IR_SPEC = """IR format (JSON):
{
  "variables": {"<name>": [lo, hi]  or  {"values": [v1, v2, ...]}},     integer variables and their domains
  "all_different": [["<name>", ...], ...],                                 groups whose values must all differ
  "conditions": [{"text": "<condition copied from the puzzle>", "constraint": "<expression>"}, ...],
                                                                           every expression must be true
  "objective": {"maximize": "<expression>"}  or  {"minimize": "<expression>"}   ONLY for optimisation problems
}
Expressions may use: integer numbers, variable names, + - * // %, == != < <= > >=, and, or, not, abs(), parentheses.
Inside arithmetic a comparison counts as 1 (true) or 0 (false), e.g. "(A == 1) + (B == 1) == 1".
Variable names must be identifiers: letters, digits and underscores only, no spaces."""

SYSTEM = "You translate logic puzzles into a formal constraint representation. You answer only with JSON."

# TODO(team): this prompt is the heart of the hybrid pipeline. Things worth considering:
#   * how should the model choose variables? (one variable per entity? per attribute value?)
#   * how should it encode positions, days, "morning/afternoon", "next to", "between", "at most"?
#   * facts that the text does not state but that the model must know (calendar, working week, ...);
#   * a worked example (few-shot) on a puzzle that is NOT in your set;
#   * how to encode knights and knaves: a statement S by person X becomes  X == (S).
FORMALIZER_PROMPT = """Translate the puzzle below into the IR format. Do NOT solve the puzzle: only write it down
formally. A constraint solver will find the answer.

{ir_spec}

VARIABLES
{variables_hint}
- Names are identifiers: replace every space or other symbol by "_", e.g. "VS Code" -> VS_Code.
- In constraints you may write an option name instead of its number; it is replaced automatically.

HOW TO WRITE CONDITIONS
- Go through the puzzle sentence by sentence. For EVERY condition add one item to "conditions":
  first copy the condition word for word into "text", then write its expression into "constraint".
  A condition that needs two expressions gets two items. Do not skip any condition and do not
  invent conditions that are not in the text.
- "X is in slot 3": X == 3.       "X is not in slot 3": X != 3.
- "X is somewhere left of / before / earlier than Y": X < Y.
- "X is immediately left of / immediately before / directly before Y": X + 1 == Y (the one named FIRST
  plus 1 equals the one named SECOND).   "X is directly behind / immediately after Y": X == Y + 1.
- "somewhere to the left / earlier" is X < Y, never abs(...). abs(X - Y) == 1 is ONLY for "next to" / "adjacent".
- "X is next to / adjacent to Y": abs(X - Y) == 1.
- "the person who has P is in slot 2": P == 2.  "the person who has P is earlier than the one who has Q": P < Q.
- "the person who has property P has property Q" (same slot): P == Q.
- "X is either first or last": X == 1 or X == 5 (use the real last number).
- Two items that cannot share a value: X != Y.
- A list like "Name: A, B" only says that A and B are linked. If the text says that linked items must get
  different values, write A != B for EVERY such line. Never create a variable for the name of the line.
- Use all_different ONLY if the text says that all those items take different values ("one per platform",
  "all different"). If the text says items may share a value ("may share a day"), do NOT use all_different.
- Do not create variables for people or things that are not named in the answer format, unless a condition
  really needs a number that is not part of the answer (an unknown amount, a count).
- Truth-tellers and liars: write exactly ONE constraint per statement: a statement S said by X becomes
  X == (S). Copy the words of the statement: "Y is a knave" is (Y == knave), "Y is a knight" is
  (Y == knight), "Y and Z are of the same kind" is (Y == Z), "Y and Z are of different kinds" is (Y != Z),
  "exactly two of us are knights" is (A + B + C == 2). Several people can be of the same kind, so
  NEVER use all_different and never add X != Y for truth-tellers and liars.
- If a condition needs common knowledge that the text does not state (days in a month, order of weekdays,
  what "the day after" means), write that knowledge into the constraints explicitly.

EXAMPLE 1
Puzzle: Three trains leave from platforms 1, 2 and 3: an intercity, a regional and an express, one per
platform. The express does not leave from platform 1. The regional leaves from a platform with a lower
number than the intercity. The intercity does not leave from platform 3.
Answer format: maps each of "Intercity", "Regional", "Express" to its platform (integer).
IR:
{{"variables": {{"Intercity": [1, 3], "Regional": [1, 3], "Express": [1, 3]}},
 "all_different": [["Intercity", "Regional", "Express"]],
 "conditions": [
  {{"text": "The express does not leave from platform 1.", "constraint": "Express != 1"}},
  {{"text": "The regional leaves from a platform with a lower number than the intercity.", "constraint": "Regional < Intercity"}},
  {{"text": "The intercity does not leave from platform 3.", "constraint": "Intercity != 3"}}]}}

EXAMPLE 2
Puzzle: Three tasks - Paint, Wire, Tile - are done in week 1 or week 2. Several tasks may share a week, but
two tasks of the same worker must be in different weeks. Workers:
- Ostap: Paint, Wire
- Lida: Wire, Tile
Tile cannot be in week 1.
Answer format: maps each of "Paint", "Wire", "Tile" to its week ("week 1", "week 2").
IR:
(variables Paint, Wire, Tile are declared by the program, 1 = week 1, 2 = week 2)
{{"variables": {{}},
 "all_different": [],
 "conditions": [
  {{"text": "Ostap: Paint, Wire", "constraint": "Paint != Wire"}},
  {{"text": "Lida: Wire, Tile", "constraint": "Wire != Tile"}},
  {{"text": "Tile cannot be in week 1.", "constraint": "Tile != 1"}}]}}
(tasks may share a week -> no all_different; workers are not variables)

EXAMPLE 3
Puzzle: Pavlo, Rita and Sava live on an island of truth-tellers and liars. Pavlo says: "Rita is a liar."
Rita says: "We are all three truth-tellers." Sava says: "Pavlo is a truth-teller."
Answer format: maps each of "Pavlo", "Rita", "Sava" to "truth-teller" or "liar".
IR:
(variables Pavlo, Rita, Sava are declared by the program, 1 = truth-teller, 0 = liar)
{{"variables": {{}},
 "all_different": [],
 "conditions": [
  {{"text": "Pavlo says: Rita is a liar.", "constraint": "Pavlo == (Rita == liar)"}},
  {{"text": "Rita says: We are all three truth-tellers.", "constraint": "Rita == (Pavlo + Rita + Sava == 3)"}},
  {{"text": "Sava says: Pavlo is a truth-teller.", "constraint": "Sava == (Pavlo == truth_teller)"}}]}}
(three statements -> three constraints; no all_different: two people may both be truth-tellers)

EXAMPLE 4
Puzzle: Ola, Ivo and Yan live in houses 1, 2 and 3; each has a different pet: a cat, a dog or a fish.
1. Ola lives somewhere to the left of the dog owner.
2. Ivo lives in the house immediately before the cat owner.
3. Ola and the fish owner live in adjacent houses.
Answer format: keys "1", "2", "3", values with the keys "Name", "Pet" - Name: "Ola", "Ivo", "Yan";
Pet: "cat", "dog", "fish".
IR:
(variables Ola, Ivo, Yan, cat, dog, fish are declared by the program; each value is a house number)
{{"variables": {{}},
 "all_different": [],
 "conditions": [
  {{"text": "Ola lives somewhere to the left of the dog owner.", "constraint": "Ola < dog"}},
  {{"text": "Ivo lives in the house immediately before the cat owner.", "constraint": "Ivo + 1 == cat"}},
  {{"text": "Ola and the fish owner live in adjacent houses.", "constraint": "abs(Ola - fish) == 1"}}]}}
("immediately before" -> the first one + 1 == the second one; "adjacent" -> abs of the difference == 1)

NOW YOUR PUZZLE
Puzzle:
{text}

Answer format: {answer_format}
{feedback}"""


def formalize(problem: dict, feedback: Optional[str] = None, previous: Optional[dict] = None) -> dict:
    """Ask the model for an IR encoding of the problem. `feedback` = error messages from a previous attempt."""
    fb = ""
    if feedback:
        shown = {k: v for k, v in previous.items() if k != "constraints"} if previous else None
        prev = f"\nYour previous encoding:\n{json.dumps(shown, ensure_ascii=False)}\n" if shown else ""
        fb = (f"{prev}\nIt was rejected because:\n{feedback}\n"
              f"Write the whole IR again: keep what was correct and change only what these errors point to.\n")
    prompt = FORMALIZER_PROMPT.format(ir_spec=IR_SPEC, text=problem["text"], variables_hint=variables_hint(problem),
                                      answer_format=problem["answer_format"], feedback=fb)
    parsed, raw = llm.ask_json(prompt, IRModel, system=SYSTEM)
    ir = parsed.model_dump(exclude_none=True)
    ir["constraints"] = [c["constraint"] for c in ir.get("conditions", [])]
    return ir


def option_constants(problem: dict) -> dict:
    spec = parse_answer_format(problem.get("answer_format", ""))
    if spec is None or spec["kind"] != "map" or not spec["options"]:
        return {}
    opts = spec["options"]
    if len(opts) == 2:
        return {var_name(opts[0]): 1, var_name(opts[1]): 0}
    return {var_name(o): i + 1 for i, o in enumerate(opts)}


def declared_variables(problem: dict) -> Optional[tuple]:
    spec = parse_answer_format(problem.get("answer_format", ""))
    if spec is None:
        return None
    if spec["kind"] == "table":
        n = len(spec["keys"])
        groups = [[var_name(v) for v in vals] for vals in spec["attributes"].values()]
        return {v: [1, n] for g in groups for v in g}, groups
    if spec["options"]:
        k = len(spec["options"])
        return {var_name(i): ([0, 1] if k == 2 else [1, k]) for i in spec["items"]}, []
    return None


def variables_hint(problem: dict) -> str:
    spec = parse_answer_format(problem.get("answer_format", ""))
    if spec is None:
        return ("- Create the integer variables the answer needs, with a domain [lo, hi] for each, and helper\n"
                "  variables only if a condition needs them.")
    if spec["kind"] == "table":
        keys = spec["keys"]
        lines = [f"- The program has ALREADY declared these variables; leave \"variables\" and \"all_different\" "
                 f"empty and only write \"conditions\".",
                 f"- One variable for every value; its value is the slot number: "
                 + ", ".join(f"{i + 1} = \"{k}\"" for i, k in enumerate(keys)) + "."]
        for attr, vals in spec["attributes"].items():
            lines.append(f"  {attr}: " + ", ".join(var_name(v) for v in vals) + "  (all different)")
        return "\n".join(lines)
    items = ", ".join(var_name(i) for i in spec["items"])
    if spec["options"]:
        opts = spec["options"]
        meaning = (f"1 = {opts[0]}, 0 = {opts[1]}" if len(opts) == 2
                   else ", ".join(f"{i + 1} = {o}" for i, o in enumerate(opts)))
        return (f"- The program has ALREADY declared these variables; leave \"variables\" empty: {items}.\n"
                f"- Value of each variable: {meaning}. You may write the option names in constraints.")
    return (f"- Declare in \"variables\" one integer variable for each of: {items}, with the domain [lo, hi]\n"
            f"  of possible values (positions, ages, ...). Add helper variables only if a condition needs them.")


_WORD = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
_KEEP = {"and", "or", "not", "abs"}


def normalize_ir(ir: dict, problem: dict) -> tuple:
    notes = []
    variables = ir.get("variables")
    if not isinstance(variables, dict):
        return ir, notes
    declared = declared_variables(problem)
    if declared is not None:
        decl_vars, decl_groups = declared
        lower = {k.lower() for k in decl_vars}
        merged = dict(decl_vars)
        for name, dom in variables.items():
            if name in decl_vars or name.lower() in lower:
                continue
            if not _IDENT.match(name):
                notes.append(f"dropped variable {name!r}: not a valid name and not needed by the answer")
                continue
            merged[name] = dom
        variables = merged
        groups = [list(g) for g in decl_groups]
        for grp in ir.get("all_different", []):
            if sorted(grp) not in [sorted(g) for g in groups]:
                groups.append(grp)
        ir = {**ir, "variables": variables, "all_different": groups}
    fixed = dict(variables)
    for name, dom in variables.items():
        if isinstance(dom, list) and len(dom) > 2 and all(_is_int(v) for v in dom):
            fixed[name] = {"values": sorted(set(dom))}
            notes.append(f"domain of {name} written as a list of values: {json.dumps(dom)} -> {{'values': ...}}")
    if fixed != variables:
        ir = {**ir, "variables": fixed}
        variables = fixed
    by_lower = {k.lower(): k for k in variables}
    consts = {k.lower(): v for k, v in option_constants(problem).items() if k.lower() not in by_lower}

    def fix(match):
        w = match.group(0)
        if w in variables or w in _KEEP:
            return w
        if w.lower() in by_lower:
            return by_lower[w.lower()]
        if w.lower() in consts:
            return str(consts[w.lower()])
        return w
    new = []
    for c in ir.get("constraints", []):
        c2 = _WORD.sub(fix, c) if isinstance(c, str) else c
        if c2 != c:
            notes.append(f"names fixed: {c!r} -> {c2!r}")
        new.append(c2)
    ir = {**ir, "constraints": new}
    groups = []
    for grp in ir.get("all_different", []):
        doms = [variables.get(g) for g in grp]
        if len(grp) > 2 and all(isinstance(d, list) and len(d) == 2 and d[1] - d[0] <= 1 for d in doms):
            notes.append(f"dropped all_different {grp}: {len(grp)} two-valued variables can never all differ")
            continue
        groups.append(grp)
    if len(groups) != len(ir.get("all_different", [])):
        ir = {**ir, "all_different": groups}
    return ir, notes


def var_name(label: str) -> str:
    s = re.sub(r"\W", "_", str(label).strip())
    return "_" + s if s[:1].isdigit() else s


def _quoted(s: str) -> list:
    return re.findall(r'"([^"]*)"', s)


def parse_answer_format(fmt: str) -> Optional[dict]:
    m = re.search(r"whose keys are (.*?) and whose values are objects with the keys (.*?)\.\s*Use exactly these values"
                  r"\s*\W\s*(.*)$", fmt, re.S)
    if m:
        keys, attr_names = _quoted(m.group(1)), _quoted(m.group(2))
        attrs = {}
        for part in m.group(3).split(";"):
            if ":" in part:
                name, vals = part.split(":", 1)
                attrs[name.strip()] = _quoted(vals)
        if keys and attr_names and all(a in attrs and len(attrs[a]) == len(keys) for a in attr_names):
            return {"kind": "table", "keys": keys, "attributes": {a: attrs[a] for a in attr_names}}
        return None
    m = re.search(r"maps each of (.*?) to (.*)$", fmt, re.S)
    if m:
        items = _quoted(m.group(1))
        rest = m.group(2)
        if not items:
            return None
        if re.search(r"\binteger\b", rest):
            return {"kind": "map", "items": items, "options": None}
        options = _quoted(rest)
        if len(options) >= 2:
            return {"kind": "map", "items": items, "options": options}
    return None


def required_variables(problem: dict) -> list:
    spec = parse_answer_format(problem.get("answer_format", ""))
    if spec is None:
        return []
    if spec["kind"] == "table":
        return [var_name(v) for vals in spec["attributes"].values() for v in vals]
    return [var_name(i) for i in spec["items"]]


def numbered_conditions(text: str) -> list:
    return re.findall(r"^\s*(\d+)\.\s+(.+)$", text, re.M)


def _norm_text(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RESERVED = {"and", "or", "not", "abs", "True", "False"}


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def validate_ir(ir: dict, problem: Optional[dict] = None) -> list:
    """Return a list of human-readable error messages; an empty list means the IR is valid.

    TODO(team). Things to check:
      * every domain is [lo, hi] with lo <= hi, or {"values": [...]} with integers;
      * every name used in all_different / constraints / objective is a declared variable;
      * every constraint parses and uses only allowed syntax.
    Hint: ir_solver.build(ir) raises ValueError with a readable message for unknown variables and
    unsupported syntax - you can call it inside try/except and turn the exception into an error message.
    """
    errors = []
    variables = ir.get("variables")
    if not isinstance(variables, dict) or not variables:
        return ['"variables" must be a non-empty object {"name": [lo, hi], ...}.']

    for name, dom in variables.items():
        if not _IDENT.match(name) or keyword.iskeyword(name) or name in _RESERVED:
            errors.append(f'Variable name "{name}" is not allowed: use letters, digits and "_" only '
                          f'(e.g. "{var_name(name)}").')
        if isinstance(dom, dict):
            vals = dom.get("values")
            if set(dom) != {"values"} or not isinstance(vals, list) or not vals or not all(_is_int(v) for v in vals):
                errors.append(f'Domain of "{name}" must be {{"values": [integers]}}, got {json.dumps(dom)}.')
        elif isinstance(dom, list) and len(dom) == 2 and all(_is_int(v) for v in dom):
            if dom[0] > dom[1]:
                errors.append(f'Domain of "{name}" is [{dom[0]}, {dom[1]}]: the lower bound is bigger than the upper.')
        else:
            errors.append(f'Domain of "{name}" must be [lo, hi] with two integers, got {json.dumps(dom)}.')

    if not ir.get("constraints"):
        errors.append('"conditions" is empty: add one item for every condition of the puzzle.')
    for grp in ir.get("all_different", []):
        unknown = [g for g in grp if g not in variables]
        if unknown:
            errors.append(f"all_different uses undeclared variables: {', '.join(unknown)}.")
        if len(grp) < 2:
            errors.append(f"all_different group {grp} must contain at least two variables.")

    for c in ir.get("constraints", []):
        if not isinstance(c, str) or not c.strip():
            errors.append(f"Constraint {c!r} must be a non-empty string.")
            continue
        try:
            tree = ast.parse(c, mode="eval")
        except SyntaxError:
            errors.append(f'Constraint "{c}" is not a valid expression (use == for equality, and/or/not for logic).')
            continue
        unknown = sorted({n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} - set(variables) - {"abs"})
        if unknown:
            errors.append(f'Constraint "{c}" uses undeclared variables: {", ".join(unknown)}. Declare them in '
                          f'"variables" or use the declared names.')

    obj = ir.get("objective")
    if obj is not None:
        if not isinstance(obj, dict) or len(obj) != 1 or next(iter(obj)) not in ("maximize", "minimize"):
            errors.append('"objective" must be {"maximize": "<expr>"} or {"minimize": "<expr>"}.')
        else:
            expr = next(iter(obj.values()))
            try:
                tree = ast.parse(expr, mode="eval")
                unknown = sorted({n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} - set(variables) - {"abs"})
                if unknown:
                    errors.append(f'Objective uses undeclared variables: {", ".join(unknown)}.')
            except SyntaxError:
                errors.append(f'Objective "{expr}" is not a valid expression.')

    if problem is not None:
        written = [_norm_text(c.get("text", "")) for c in ir.get("conditions", []) if isinstance(c, dict)]
        skipped = [num for num, cond in numbered_conditions(problem.get("text", "")) if "conditions" in ir
                   if not any(_norm_text(cond)[:40] in w or w[:40] in _norm_text(cond) for w in written if w)]
        if skipped:
            errors.append("These numbered conditions of the puzzle are missing from \"conditions\": "
                          + ", ".join(skipped) + ". Add one item for each of them (copy its text, then write "
                          "its constraint) and keep all the other items.")
        missing = [v for v in required_variables(problem) if v not in variables]
        if missing:
            errors.append("The answer format needs a variable for each of these names, but they are missing: "
                          + ", ".join(missing) + ".")

    if not errors:
        try:
            ir_solver.build(ir)
        except (ValueError, TypeError, KeyError, SyntaxError) as e:
            errors.append(f"The solver rejected the encoding: {e}.")
    if not errors:
        for c in ir.get("constraints", []):
            _, cons, _ = ir_solver.build({"variables": variables, "constraints": [c]})
            s = z3.Solver()
            s.add(*cons)
            if s.check() == z3.unsat:
                errors.append(f'Constraint "{c}" can never be true with the declared domains, even on its own '
                              f'(for example, two positions 1..N can never add up to 1). Re-read that condition '
                              f'and use the patterns: before -> <, immediately before -> X + 1 == Y, '
                              f'adjacent -> abs(X - Y) == 1.')
    return errors


def run_solver(ir: dict, problem: Optional[dict] = None) -> dict:
    """Run Z3 on the IR. Returns {"status": ..., "solutions": [...], "objective": ...}.

    TODO(team): with limit=1 the solver stops after the first solution, so it reports "unique" even when
    several solutions exist. Think about what limit you need to tell "unique" from "multiple".
    """
    keys = [v for v in required_variables(problem) if v in ir["variables"]] if problem else []
    if ir.get("objective") or not keys or len(keys) == len(ir["variables"]):
        return ir_solver.solve(ir, limit=2)
    zv, cons, _ = ir_solver.build(ir)
    s = z3.Solver()
    s.add(*cons)
    sols = []
    while len(sols) < 2 and s.check() == z3.sat:
        m = s.model()
        sols.append({k: m.eval(v, model_completion=True).as_long() for k, v in zv.items()})
        s.add(z3.Or(*[zv[k] != sols[-1][k] for k in keys]))
    status = "none" if not sols else ("unique" if len(sols) == 1 else "multiple")
    return {"status": status, "solutions": sols}


def present_deterministic(problem: dict, result: dict) -> Optional[dict]:
    spec = parse_answer_format(problem.get("answer_format", ""))
    if spec is None or not result["solutions"]:
        return None
    a = result["solutions"][0]
    try:
        if spec["kind"] == "table":
            keys = spec["keys"]
            sol = {k: {} for k in keys}
            for attr, vals in spec["attributes"].items():
                for v in vals:
                    pos = a[var_name(v)]
                    if not 1 <= pos <= len(keys):
                        return None
                    sol[keys[pos - 1]][attr] = v
            if any(len(row) != len(spec["attributes"]) for row in sol.values()):
                return None
            return sol
        sol = {}
        opts = spec["options"]
        for item in spec["items"]:
            x = a[var_name(item)]
            if opts is None:
                sol[item] = x
            elif len(opts) == 2 and x == 0:
                sol[item] = opts[1]
            elif 1 <= x <= len(opts):
                sol[item] = opts[x - 1]
            else:
                return None
        return sol
    except KeyError:
        return None


PRESENT_PROMPT = """A puzzle has been solved by a constraint solver. Rewrite the solver's result in the required
answer format. Do NOT solve the puzzle again - only translate the solver's assignment.

Puzzle:
{text}

Encoding used by the solver:
{ir}

Solver assignment (variable -> value):
{assignment}

{answer_format}"""


def present(problem: dict, ir: dict, result: dict, trace: Optional[dict] = None) -> dict:
    """Turn the solver result into the required answer format.

    Provided baseline: the model translates the assignment. This is a weak point - the model can
    introduce errors AFTER the solver. Status and objective are always taken from the solver, never
    from the model. Extension: write deterministic code for problem types where the mapping is obvious.
    """
    status = result["status"]
    if status == "none":
        if trace is not None:
            trace["present"] = "none"
        return Answer(status="none").model_dump()
    sol = present_deterministic(problem, result)
    if sol is not None:
        if trace is not None:
            trace["present"] = "deterministic"
        return Answer(status=status, solution=sol, objective=result.get("objective")).model_dump()
    if trace is not None:
        trace["present"] = "llm"
    prompt = PRESENT_PROMPT.format(text=problem["text"], ir=json.dumps(ir, ensure_ascii=False),
                                   assignment=json.dumps(result["solutions"][0], ensure_ascii=False),
                                   answer_format=problem["answer_format"])
    parsed, raw = llm.ask_json(prompt, Answer)
    return Answer(status=status, solution=parsed.solution, objective=result.get("objective")).model_dump()


def _attempt(problem: dict, feedback: Optional[str], previous: Optional[dict] = None) -> dict:
    try:
        ir = formalize(problem, feedback, previous)
    except llm.LLMError as e:
        return {"ir": None, "errors": [f"Your answer was not valid JSON for the IR schema: {e}"],
                "raw_model_output": e.raw}
    raw_ir = ir
    ir, notes = normalize_ir(ir, problem)
    att = {"ir": ir, "errors": validate_ir(ir, problem)}
    if notes:
        att["model_ir"], att["normalized"] = raw_ir, notes
    return att


def solve(problem: dict) -> dict:
    """Returns {"answer": <Answer as dict>, "trace": {...}}. Raise HybridError if no answer can be produced."""
    trace = {"attempts": []}

    att = _attempt(problem, None)
    trace["attempts"].append(att)
    if att["errors"]:
        att = _attempt(problem, "\n".join("- " + e for e in att["errors"]), att.get("model_ir", att["ir"]))
        trace["attempts"].append(att)
    if att["errors"]:
        raise HybridError("invalid IR after retry: " + "; ".join(att["errors"]), trace)
    ir = att["ir"]

    try:
        result = run_solver(ir, problem)
    except (ValueError, TypeError) as e:         # the solver rejected the IR
        raise HybridError(f"solver rejected the IR: {e}", trace) from e
    trace["solver"] = {"status": result["status"], "n_solutions": len(result["solutions"]),
                       "objective": result.get("objective"),
                       "first_solution": result["solutions"][0] if result["solutions"] else None,
                       "second_solution": result["solutions"][1] if len(result["solutions"]) > 1 else None}

    answer = present(problem, ir, result, trace)
    return {"answer": answer, "trace": trace}
