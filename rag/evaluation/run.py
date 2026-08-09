import json
from pathlib import Path

from rag.store import LocalChroma


def reciprocal_rank(results: list[dict], expected_sections: list[str]) -> float:
    for index, result in enumerate(results, start=1):
        section = result["section"].lower()
        if any(term.lower() in section for term in expected_sections):
            return 1 / index
    return 0.0


def main() -> None:
    cases_path = Path(__file__).parent / "ground_truth.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    store = LocalChroma()
    rows = []
    for case in cases:
        results = store.search(case["question"], limit=4)
        top_text = " ".join(result["text"] for result in results).lower()
        terms_found = all(term.lower() in top_text for term in case["required_terms"])
        rr = reciprocal_rank(results, case["expected_sections"])
        rows.append({"id": case["id"], "hit_at_4": terms_found, "mrr": rr})

    hit_at_4 = sum(row["hit_at_4"] for row in rows) / len(rows)
    mrr = sum(row["mrr"] for row in rows) / len(rows)
    output = [
        "# Retrieval evaluation",
        "",
        f"- Cases: {len(rows)}",
        f"- Hit@4: {hit_at_4:.1%}",
        f"- MRR@4: {mrr:.3f}",
        "",
        "| Case | Hit@4 | RR |",
        "|---|---:|---:|",
    ]
    output.extend(
        f"| {row['id']} | {'yes' if row['hit_at_4'] else 'no'} | {row['mrr']:.3f} |"
        for row in rows
    )
    report = "\n".join(output) + "\n"
    target = Path(__file__).parent / "results.md"
    target.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
