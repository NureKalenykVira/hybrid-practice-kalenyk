"""Environment check for the neuro-symbolic practical.

Usage:
    python smoke_test.py              # checks Python, packages, solver, Ollama and the qwen2.5:3b model
    python smoke_test.py --skip-llm   # check everything except the language model
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

OK, FAIL, WARN = "[ OK ]", "[FAIL]", "[WARN]"
failures = 0


def report(status, msg, hint=None):
    global failures
    print(f"{status} {msg}")
    if hint:
        print(f"       -> {hint}")
    if status == FAIL:
        failures += 1


def check_python():
    v = sys.version_info
    if v >= (3, 10):
        report(OK, f"Python {v.major}.{v.minor}.{v.micro}")
    else:
        report(FAIL, f"Python {v.major}.{v.minor} is too old", "Install Python 3.10 or newer (step 1 of the guide).")


def check_packages():
    for name, pip_name in [("z3", "z3-solver==4.13.0.0"), ("ollama", "ollama"), ("pydantic", "pydantic")]:
        try:
            mod = __import__(name)
            ver = getattr(mod, "__version__", None)
            if name == "z3":
                ver = mod.get_version_string()
            report(OK, f"package {name} {ver or ''}".rstrip())
        except ImportError:
            report(FAIL, f"package {name} is not installed", f"pip install {pip_name}")


def check_solver():
    try:
        from ir_solver import solve
    except ImportError:
        report(FAIL, "src/ir_solver.py not found", "Run this script from the root of the starter repository.")
        return
    ir = {"variables": {"Intercity": [1, 3], "Regional": [1, 3], "Express": [1, 3]},
          "all_different": [["Intercity", "Regional", "Express"]],
          "constraints": ["Express != 1", "Regional < Intercity", "Intercity != 3"]}
    try:
        r = solve(ir, limit=2)
    except Exception as e:  # noqa: BLE001
        report(FAIL, f"solver raised an error: {e}")
        return
    expected = {"Intercity": 2, "Regional": 1, "Express": 3}
    if r["status"] == "unique" and r["solutions"][0] == expected:
        report(OK, "Z3 solver: test problem solved correctly")
    else:
        report(FAIL, f"Z3 solver returned an unexpected result: {r}")


def check_llm(model):
    try:
        import ollama
        from pydantic import BaseModel
    except ImportError:
        report(FAIL, "cannot test the model: ollama / pydantic missing")
        return
    try:
        installed = [m.model for m in ollama.list().models]
    except Exception as e:  # noqa: BLE001
        report(FAIL, f"Ollama is not reachable ({e.__class__.__name__})",
               "Start the Ollama app (macOS/Windows) or run `ollama serve` (Linux).")
        return
    report(OK, "Ollama server is running")
    if not any(m == model or m.startswith(model + ":") or m.split(":")[0] == model for m in installed):
        report(FAIL, f"model {model} is not downloaded (found: {', '.join(installed) or 'none'})",
               f"ollama pull {model}")
        return
    report(OK, f"model {model} is downloaded")

    class Answer(BaseModel):
        city: str
        country: str

    t = time.time()
    try:
        resp = ollama.chat(model=model,
                           messages=[{"role": "user", "content": "Name the capital of Ukraine. Answer in JSON."}],
                           format=Answer.model_json_schema(),
                           options={"temperature": 0})
        ans = Answer.model_validate_json(resp.message.content)
    except Exception as e:  # noqa: BLE001
        report(FAIL, f"model did not return valid JSON: {e}")
        return
    dt = time.time() - t
    report(OK, f"model returned structured JSON in {dt:.1f} s: {json.dumps(ans.model_dump(), ensure_ascii=False)}")
    if dt > 60:
        report(WARN, "the model is slow on this machine",
               "Close other heavy programs, or use the team's fastest laptop during the practical.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:3b", help=argparse.SUPPRESS)
    ap.add_argument("--skip-llm", action="store_true")
    args = ap.parse_args()

    print("Environment check for the neuro-symbolic practical\n")
    check_python()
    check_packages()
    check_solver()
    if args.skip_llm:
        report(WARN, "language model check skipped (--skip-llm)")
    else:
        check_llm(args.model)
    print()
    if failures:
        print(f"{failures} problem(s) found. Fix them using the hints above and run the check again.")
        sys.exit(1)
    print("All checks passed. You are ready for the practical.")


if __name__ == "__main__":
    main()
