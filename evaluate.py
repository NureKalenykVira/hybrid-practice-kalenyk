"""Compare your saved runs with the answer key.

The answer key (answers.json) is handed out by the instructor during the evaluation stage.
Put it in the repository root, then:
    python evaluate.py --team A
    python evaluate.py --team A --answers path/to/answers.json

Prints a summary table and writes results/<team>/evaluation.csv (one row per run) for your slides.

How a run is judged:
  * status must match the expected status ("unique", "multiple", "none", "optimal");
  * "unique":   the solution must match exactly (case and surrounding spaces are ignored);
  * "multiple" / "none": the status is what counts;
  * optimisation problems: the objective must match and the solution must be valid/optimal.
A run that ended with an error is counted as incorrect.
"""
import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------- normalisation
def norm(x):
    if isinstance(x, bool):
        return x
    if isinstance(x, int):
        return x
    if isinstance(x, float) and x.is_integer():
        return int(x)
    if isinstance(x, str):
        s = x.strip()
        return int(s) if re.fullmatch(r"-?\d+", s) else s.lower()
    if isinstance(x, dict):
        return {str(k).strip().lower(): norm(v) for k, v in x.items()}
    if isinstance(x, list):
        return sorted((norm(v) for v in x), key=repr)
    return x


def flatten(d, prefix=()):
    if isinstance(d, dict):
        out = {}
        for k, v in d.items():
            out.update(flatten(v, prefix + (k,)))
        return out
    return {prefix: d}


def match_pct(expected, got):
    """Share of expected leaf values reproduced by `got` (useful partial measure for grids)."""
    e, g = flatten(norm(expected)), flatten(norm(got or {}))
    if not e:
        return None
    return round(100 * sum(1 for k, v in e.items() if g.get(k) == v) / len(e))


# ---------------------------------------------------------------- checks
def check_run(exp, ans):
    """Returns (correct: bool, match: int|None, reason: str)."""
    status = (ans or {}).get("status")
    sol = (ans or {}).get("solution") or {}
    obj = (ans or {}).get("objective")
    kind = exp["check"]

    if kind == "exact":
        m = match_pct(exp["solution"], sol)
        if status != exp["status"]:
            return False, m, f"status {status}, expected {exp['status']}"
        if norm(sol) != norm(exp["solution"]):
            return False, m, f"solution differs ({m}% of values correct)"
        return True, 100, ""

    if kind == "status":
        if status != exp["status"]:
            return False, None, f"status {status}, expected {exp['status']}"
        if exp["status"] == "multiple" and sol:
            valid = norm(sol) in [norm(s) for s in exp["solutions"]]
            return True, None, "" if valid else "status correct; the example solution given is not a valid one"
        return True, None, ""

    if kind == "exact_optimum":
        canon = {c.lower(): c for c in exp["solution"]["build"]}
        for c, alts in exp.get("aliases", {}).items():
            for a in alts + [c]:
                canon[a.lower()] = c
        got = sorted(canon.get(str(f).strip().lower(), str(f)) for f in sol.get("build", []))
        reasons = []
        if status != exp["status"]:
            reasons.append(f"status {status}, expected {exp['status']}")
        if norm(obj) != exp["objective"]:
            reasons.append(f"objective {obj}, expected {exp['objective']}")
        if got != sorted(exp["solution"]["build"]):
            reasons.append("the chosen set of features is not the optimal one")
        return (not reasons), None, "; ".join(reasons)

    if kind == "coloring":
        stations = sorted({s for e in exp["edges"] for s in e})
        a = {str(k).strip().lower(): norm(v) for k, v in sol.items()}
        reasons = []
        if status != exp["status"]:
            reasons.append(f"status {status}, expected {exp['status']}")
        if norm(obj) != exp["objective"]:
            reasons.append(f"objective {obj}, expected {exp['objective']}")
        missing = [s for s in stations if s.lower() not in a]
        if missing:
            reasons.append("no frequency for " + ", ".join(missing))
        else:
            clashes = [f"{x}–{y}" for x, y in exp["edges"] if a[x.lower()] == a[y.lower()]]
            if clashes:
                reasons.append("interfering stations share a frequency: " + ", ".join(clashes))
            used = len({a[s.lower()] for s in stations})
            if isinstance(obj, int) and used > obj:
                reasons.append(f"assignment uses {used} frequencies but objective says {obj}")
        return (not reasons), None, "; ".join(reasons)

    return False, None, f"unknown check type {kind}"


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--team", required=True)
    ap.add_argument("--answers", default=str(ROOT / "answers.json"))
    args = ap.parse_args(argv)
    team = args.team.upper()

    ans_path = Path(args.answers)
    if not ans_path.exists():
        sys.exit(f"Answer key not found: {ans_path}\nIt is handed out by the instructor at the evaluation stage.")
    key = json.loads(ans_path.read_text(encoding="utf-8"))
    res_dir = ROOT / "results" / team
    files = sorted(res_dir.glob("*__*__run*.json")) if res_dir.exists() else []
    if not files:
        sys.exit(f"No saved runs in {res_dir}. Run  python src/run.py --team {team}  first.")

    rows = []
    for f in files:
        r = json.loads(f.read_text(encoding="utf-8"))
        exp = key.get(r["problem"])
        if exp is None:
            continue
        if r.get("error"):
            ok, m, reason = False, None, "ERROR: " + r["error"][:120]
        else:
            ok, m, reason = check_run(exp, r["answer"])
        rows.append({"problem": r["problem"], "title": exp.get("title", ""), "pipeline": r["pipeline"],
                     "run": r["run"], "correct": ok,
                     "status": None if r.get("error") else r["answer"].get("status"),
                     "expected_status": exp["status"], "match_pct": m, "llm_calls": r.get("llm_calls"),
                     "seconds": r.get("seconds"), "reason": reason})

    out = res_dir / "evaluation.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # summary: problem x pipeline
    agg = defaultdict(list)
    for r in rows:
        agg[(r["problem"], r["pipeline"])].append(r)
    problems = sorted({r["problem"] for r in rows})
    print(f"Team {team}: {len(rows)} runs evaluated\n")
    print(f"{'problem':8}{'title':34}{'monolith':>10}{'hybrid':>10}")
    for p in problems:
        cells = []
        for name in ("monolith", "hybrid"):
            rs = agg.get((p, name), [])
            cells.append(f"{sum(x['correct'] for x in rs)}/{len(rs)}" if rs else "—")
        title = next(r["title"] for r in rows if r["problem"] == p)[:32]
        print(f"{p:8}{title:34}{cells[0]:>10}{cells[1]:>10}")
    for name in ("monolith", "hybrid"):
        rs = [r for r in rows if r["pipeline"] == name]
        if rs:
            print(f"\n{name}: {sum(r['correct'] for r in rs)}/{len(rs)} runs correct")
    print("\nFailures:")
    for r in rows:
        if not r["correct"]:
            print(f"  {r['problem']} {r['pipeline']:9} run {r['run']}: {r['reason']}")
    print(f"\nPer-run details: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
