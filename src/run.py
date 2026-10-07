"""Run the pipelines on your team's problems and save every run to results/<team>/.

Examples:
    python src/run.py --team A                          # both pipelines, all 5 problems, 2 runs each
    python src/run.py --team A --pipeline monolith      # only the monolithic pipeline
    python src/run.py --team A --problem A3 --runs 1    # one problem, one run (handy while debugging)
"""
import argparse
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import llm          # noqa: E402
import hybrid       # noqa: E402
import monolith     # noqa: E402

PIPELINES = {"monolith": monolith, "hybrid": hybrid}


def load_problems(team: str) -> list:
    data = json.loads((ROOT / "problems" / "problems.json").read_text(encoding="utf-8"))
    probs = [dict(id=pid, **p) for pid, p in data.items() if p["team"] == team.upper()]
    if not probs:
        sys.exit(f"No problems found for team {team!r}.")
    return sorted(probs, key=lambda p: p["id"])


def run_one(problem: dict, name: str, k: int, out_dir: Path) -> dict:
    llm.reset_stats()
    t0 = time.time()
    record = {"problem": problem["id"], "pipeline": name, "run": k, "model": llm.model_name(),
              "timestamp": datetime.now().isoformat(timespec="seconds"),
              "answer": None, "trace": None, "error": None}
    try:
        out = PIPELINES[name].solve(problem)
        record["answer"], record["trace"] = out["answer"], out.get("trace")
    except Exception as e:  # noqa: BLE001 - every failure is data for the analysis
        record["error"] = f"{e.__class__.__name__}: {e}"
        record["traceback"] = traceback.format_exc()
        if isinstance(e, llm.LLMError):
            record["raw_model_output"] = e.raw
        if getattr(e, "trace", None) is not None:
            record["trace"] = e.trace
    record["seconds"] = round(time.time() - t0, 1)
    record["llm_calls"] = llm.STATS["calls"]
    path = out_dir / f"{problem['id']}__{name}__run{k}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    return record


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--team", required=True, help="team letter, A-H")
    ap.add_argument("--pipeline", choices=["monolith", "hybrid", "both"], default="both")
    ap.add_argument("--problem", help="run a single problem, e.g. A3")
    ap.add_argument("--runs", type=int, default=2, help="runs per problem and pipeline (default 2)")
    args = ap.parse_args(argv)

    problems = load_problems(args.team)
    if args.problem:
        problems = [p for p in problems if p["id"] == args.problem.upper()]
        if not problems:
            sys.exit(f"Problem {args.problem} is not in team {args.team}'s set.")
    names = ["monolith", "hybrid"] if args.pipeline == "both" else [args.pipeline]
    out_dir = ROOT / "results" / args.team.upper()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Model: {llm.model_name()}   results -> {out_dir.relative_to(ROOT)}/")
    if not llm.VERBOSE:
        print("Tip: set LLM_VERBOSE=1 to watch the model's output live (see README).")
    print()
    for p in problems:
        for name in names:
            for k in range(1, args.runs + 1):
                print(f"{p['id']:4} {name:9} run {k} ... ", end="", flush=True)
                r = run_one(p, name, k, out_dir)
                if r["error"]:
                    print(f"ERROR ({r['seconds']} s, {r['llm_calls']} LLM calls): {r['error'][:100]}")
                else:
                    print(f"status={r['answer']['status']:8} ({r['seconds']} s, {r['llm_calls']} LLM calls)")
    print("\nDone. After the answer key is released, run:  python evaluate.py --team", args.team.upper())


if __name__ == "__main__":
    main()
