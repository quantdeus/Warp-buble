#!/usr/bin/env python3
"""Консервативный бинарный QA-классификатор варп-гипотез.

PASS = существует ограниченное свидетельство для конкретного вопроса;
FAIL = конкретный отрицательный результат в заявленной модели;
UNKNOWN = ни проверка, ни опровержение пока не выполнены.
Никогда не делает утверждение о реально построенном сверхсветовом двигателе.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = HERE / "trek-ftl-branches.json"
VALID = {"PASS", "FAIL", "UNKNOWN"}


def validate(registry: dict) -> None:
    ids = [item["id"] for item in registry["gates"]]
    assert len(ids) == len(set(ids)) == 8, "Eight unique decision gates required"
    refs = {item["id"] for item in registry["citations"]}
    for candidate in registry["candidates"]:
        assert set(candidate["gates"]) == set(ids), "Missing or unexpected scientific gate"
        for name, detail in candidate["gates"].items():
            assert detail["status"] in VALID, (candidate["id"], name)
            if detail["status"] == "PASS":
                assert detail["evidence"], f"{candidate['id']} {name}: PASS without evidence"
            assert all(r in refs for r in detail["evidence"]), "Unknown reference ID"
    assert registry["audit"]["matched"] <= registry["audit"]["checked_total"]


def classify(candidate: dict) -> dict:
    g = candidate["gates"]
    path = []
    for k in ("metric", "formal_ftl", "energy_conditions", "quantum_bounds",
              "horizon_causality", "stability", "engineerability", "experiment"):
        path.append({"gate": k, "branch": g[k]["status"]})
    if g["metric"]["status"] != "PASS":
        verdict = "METRIC_NOT_ESTABLISHED"
    elif g["formal_ftl"]["status"] == "FAIL":
        verdict = "SUBLUMINAL_NOT_FTL"
    elif g["formal_ftl"]["status"] == "UNKNOWN":
        verdict = "FTL_NOT_DEFINED"
    elif g["energy_conditions"]["status"] == "FAIL":
        verdict = "ENERGY_CONDITION_BARRIER"
    elif any(x["status"] == "FAIL" for x in g.values()):
        verdict = "SCIENTIFIC_GATE_BLOCKED"
    elif any(x["status"] == "UNKNOWN" for x in g.values()):
        verdict = "INCOMPLETE_EVIDENCE"
    else:
        # Even a fully-marked registry is only a candidate for independent
        # review. A JSON label cannot establish a physical discovery.
        verdict = "REQUIRES_INDEPENDENT_EXPERIMENTAL_REVIEW"
    return {
        "candidate": candidate["id"],
        "binary_path": path,
        "verdict": verdict,
        "scientific_gates_passed": sum(x["status"] == "PASS" for x in g.values()),
        "scientific_gates_failed": sum(x["status"] == "FAIL" for x in g.values()),
        "scientific_gates_unknown": sum(x["status"] == "UNKNOWN" for x in g.values()),
        "physical_ftl_verified": False,
    }


def report(registry: dict) -> dict:
    validate(registry)
    return {
        "project": registry["project"],
        "documentary_audit": registry["audit"],
        "physical_ftl_verified": False,
        "candidates": [classify(c) for c in registry["candidates"]],
        "limitations": "Ссылки проверены, но модель не равна аппарату. Литературный аудит не заменяет измерения.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    obj = report(json.loads(args.input.read_text(encoding="utf-8")))
    output = json.dumps(obj, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)
