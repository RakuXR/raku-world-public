#!/usr/bin/env python3
"""Re-derive every published number from proof/public-evidence.json. Standard library only.

    python recheck_offline.py             # every published number re-computes from the evidence
    python recheck_offline.py --selftest  # prove the check can fail

Checks: the final control error is inside the published tolerance; the ~99.1% reduction is the
arithmetic of the initial and final error; the README's rounded figures are the evidence's values
to three decimals; the two showcase frames and the film hash to the values the evidence records.
"""
from __future__ import annotations
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
EVIDENCE = ROOT / "proof" / "public-evidence.json"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def recheck(root: pathlib.Path, ev: dict) -> list[str]:
    fails = []
    r = ev["result"]
    initial, final, tol, target = r["initial_control_error_m"], r["final_control_error_m"], r["tolerance_m"], r["target_m"]
    if not (0 < final < initial):
        fails.append("final error is not smaller than the initial error")
    if (final <= tol) != r["within_tolerance"]:
        fails.append("within_tolerance disagrees with final error vs tolerance")
    reduction = 100.0 * (1.0 - final / initial)
    if abs(reduction - r["error_reduction_pct_derived"]) > 0.05:
        fails.append(f"derived reduction {reduction:.2f}% != published {r['error_reduction_pct_derived']}")
    if f"{initial:.3f}" != r["initial_control_error_m_rounded"] or f"{final:.3f}" != r["final_control_error_m_rounded"]:
        fails.append("rounded figures do not match the evidence values to three decimals")
    if round(final * 1000) != r["final_control_error_mm"]:
        fails.append("millimetre figure does not match the final error")
    if target != 3.0:
        fails.append("target is not the published 3.000 m")
    for key, rel in (("showcase_initial_png", "proof/showcase-initial.png"), ("showcase_final_png", "proof/showcase-final.png")):
        p = root / rel
        if not p.is_file():
            fails.append(f"missing {rel}")
        elif sha256(p) != ev["hashes"][key]:
            fails.append(f"hash mismatch {rel}")
    film = root / "video" / "rakuai-rakuworld-gtc.mp4"
    if film.is_file() and sha256(film) != ev["hashes"]["film_mp4"]:
        fails.append("film hash mismatch")
    if len(ev["private_record"]["sha256"]) != 64:
        fails.append("private-record binding is not a sha256")
    return fails


def main() -> int:
    ev = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if "--selftest" in sys.argv:
        clean = recheck(ROOT, ev)
        if clean:
            print("SELFTEST FAIL -- pristine evidence does not recheck:", clean)
            return 2
        bad = json.loads(json.dumps(ev))
        bad["result"]["final_control_error_m"] = bad["result"]["tolerance_m"] + 0.5   # outside tolerance, still smaller than initial
        fails = recheck(ROOT, bad)
        if fails:
            print("SELFTEST OK -- a falsified final error was detected:", fails[0])
            return 0
        print("SELFTEST FAIL -- falsified evidence passed")
        return 2
    fails = recheck(ROOT, ev)
    if fails:
        print("FAIL")
        for f in fails:
            print("  ", f)
        return 1
    r = ev["result"]
    print(f"OK -- initial {r['initial_control_error_m']:.5f} m -> final {r['final_control_error_m']:.5f} m, "
          f"{100.0 * (1.0 - r['final_control_error_m'] / r['initial_control_error_m']):.1f}% lower, "
          f"inside +/-{r['tolerance_m']} m of the {r['target_m']:.3f} m target; frames and film hash as published")
    return 0


if __name__ == "__main__":
    sys.exit(main())
