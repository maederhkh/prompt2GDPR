"""
Reproduce the summary figures reported in the paper
"Evaluating Reasoning, Grounding, and Stability in LLM-Based GDPR Compliance Assessment".

Reads:
  - scripts/outputs/GDPR_thesis_analysis_results.xlsx (sheet Master_Table)
  - gemini_judge_output/**.json (judge labels after human correction)
  - data/rubric.csv (reference labels)

Prints:
  - Evidence Error Rate (EER), pooled per run, per model, and for data minimisation
  - Article 5 text accuracy per run
  - Label agreement with the reference labels per run
  - Pairwise flip rates per model
  - RAS and JJS per run, recomputed from the judge files
  - Judge validation counts (judge label vs. human-corrected label)

Run from anywhere:  python scripts/compute_paper_metrics.py
"""

import csv
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
EXCEL = ROOT / "scripts" / "outputs" / "GDPR_thesis_analysis_results.xlsx"
JUDGE_DIR = ROOT / "gemini_judge_output"
RUBRIC = ROOT / "data" / "rubric.csv"

CONDITIONS = ["ZS", "ZS-Ext", "FS1", "FS2", "FS3", "FS3-Ext"]
MODELS = ["GPT-5.2", "Grok"]

# Filenames as they appear in the Excel workbook (names used before the
# outputs were renamed) -> (model, paper condition)
EXCEL_FILES = {
    "zero_shot_gpt5.3rd.json": ("GPT-5.2", "ZS"),
    "Zero-shot.3rd.GPT5.EXTENDED.THINKING.JSON": ("GPT-5.2", "ZS-Ext"),
    "1st few shot output.GPT5.json": ("GPT-5.2", "FS1"),
    "2nd few shot output.GPT5.json": ("GPT-5.2", "FS2"),
    "3rd few shot output.GPT5.json": ("GPT-5.2", "FS3"),
    "3rd few shot output.GPT5.EXTENDED THINKING.JSON": ("GPT-5.2", "FS3-Ext"),
    "zero_shot_grok.3rd.json": ("Grok", "ZS"),
    "zero-shot.3rd.grok.expert.json": ("Grok", "ZS-Ext"),
    "1st few shot output.Grok.json": ("Grok", "FS1"),
    "2nd few shot output.Grok.json": ("Grok", "FS2"),
    "3rd few shot output.Grok.json": ("Grok", "FS3"),
    "3rd few shot output.Grok.Expert.json": ("Grok", "FS3-Ext"),
}

# Judge output files (repository paths) -> (model, paper condition)
JUDGE_FILES = {
    "gpt5.2/zero_shot/3rd_output.json": ("GPT-5.2", "ZS"),
    "gpt5.2/zero_shot/3rd_output_thinking_extended.json": ("GPT-5.2", "ZS-Ext"),
    "gpt5.2/few_shot/1st_output.json": ("GPT-5.2", "FS1"),
    "gpt5.2/few_shot/2nd_output.json": ("GPT-5.2", "FS2"),
    "gpt5.2/few_shot/3rd_output.json": ("GPT-5.2", "FS3"),
    "gpt5.2/few_shot/3rd_output_thinking_extended.json": ("GPT-5.2", "FS3-Ext"),
    "grok/zero_shot/3rd_output.json": ("Grok", "ZS"),
    "grok/zero_shot/3rd_output_expert.json": ("Grok", "ZS-Ext"),
    "grok/few_shot/1st_output.json": ("Grok", "FS1"),
    "grok/few_shot/2nd_output.json": ("Grok", "FS2"),
    "grok/few_shot/3rd_output.json": ("Grok", "FS3"),
    "grok/few_shot/3rd_output_expert.json": ("Grok", "FS3-Ext"),
}

JJS_DIMENSIONS = ["traceability", "principle_correctness", "calibration", "no_overreach"]

# Spelling variants of RAS labels typed during the manual review
RAS_LABEL_FIXES = {"ENTAIL": "ENTAILS", "CONTRADICS": "CONTRADICTS"}


def normalize_ras_label(label):
    label = str(label).strip().upper().replace(" ", "_")
    return RAS_LABEL_FIXES.get(label, label)


def round2(x):
    """Round half up to two decimals (not truncate, not banker's rounding)."""
    return Decimal(str(float(x))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def pct(num, den):
    return round2(Fraction(num, den) * 100) if den else Decimal("0")


def normalize_label(label):
    label = str(label).strip().lower().replace("-", " ")
    if label.startswith("partially"):
        return "Partially compliant"
    if label.startswith("non") or label.startswith("not compliant"):
        return "Non-compliant"
    if label.startswith("compliant"):
        return "Compliant"
    raise ValueError(f"Unknown compliance label: {label!r}")


def parse_errors(value, num_sections):
    """Column 'section_result FGS' holds 'errors/total' or '0'."""
    text = str(value).strip()
    if "/" in text:
        errors, total = (int(x) for x in text.split("/"))
        if total != num_sections:
            print(f"   ! note: grounding total {total} differs from Num_Sections {num_sections}")
        return errors, total
    return int(text), num_sections


def parse_text_accuracy(status):
    """Official_Text_Status: a percentage, or 'Correct (Substring)' = exact containment = 100%."""
    match = re.search(r"(\d+)\s*%", str(status))
    if match:
        return int(match.group(1))
    if "substring" in str(status).lower():
        return 100
    raise ValueError(f"Cannot parse Official_Text_Status: {status!r}")


def load_master_table():
    df = pd.read_excel(EXCEL, sheet_name="Master_Table")
    df = df[df["Filename"].isin(EXCEL_FILES)].copy()
    df["Model"] = df["Filename"].map(lambda f: EXCEL_FILES[f][0])
    df["Condition"] = df["Filename"].map(lambda f: EXCEL_FILES[f][1])
    df["Principle_ID"] = df["Principle_ID"].astype(int)
    df["Label"] = df["Rating"].map(normalize_label)
    parsed = [parse_errors(v, n) for v, n in zip(df["section_result FGS"], df["Num_Sections"])]
    df["Errors"] = [e for e, _ in parsed]
    df["Citations"] = [t for _, t in parsed]
    df["TextAccuracy"] = df["Official_Text_Status"].map(parse_text_accuracy)
    assert len(df) == 84, f"expected 84 rows (12 runs x 7 principles), got {len(df)}"
    return df


def load_reference_labels():
    with open(RUBRIC, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {int(r["principle_id"]): r["reference_label"] for r in rows if r["question_no"] == "1"}


def load_judge_runs():
    runs = {}
    for rel, key in JUDGE_FILES.items():
        with open(JUDGE_DIR / rel, encoding="utf-8") as f:
            runs[key] = json.load(f)
    return runs


def print_table(title, rows, header):
    print(f"\n=== {title}")
    print(pd.DataFrame(rows, columns=header).to_string(index=False))


def report_grounding(df):
    rows = []
    for model in MODELS:
        for cond in CONDITIONS:
            run = df[(df["Model"] == model) & (df["Condition"] == cond)]
            e, n = run["Errors"].sum(), run["Citations"].sum()
            rows.append([model, cond, f"{e}/{n}", pct(e, n)])
    print_table("Evidence Error Rate (EER) per run, pooled over principles", rows,
                ["Model", "Condition", "Errors/Citations", "EER %"])

    rows = []
    for model in MODELS:
        m = df[df["Model"] == model]
        e, n = m["Errors"].sum(), m["Citations"].sum()
        dm = m[m["Principle_ID"] == 3]
        de, dn = dm["Errors"].sum(), dm["Citations"].sum()
        rows.append([model, f"{e}/{n}", pct(e, n), f"{de}/{dn}", pct(de, dn)])
    print_table("Overall EER per model (pooled) and data minimisation", rows,
                ["Model", "All", "EER %", "Data minimisation", "DM EER %"])


def report_text_accuracy(df):
    rows = []
    for model in MODELS:
        for cond in CONDITIONS:
            run = df[(df["Model"] == model) & (df["Condition"] == cond)]
            rows.append([model, cond, round2(run["TextAccuracy"].mean())])
    print_table("Article 5 text accuracy (mean similarity %, 'Substring' = 100)", rows,
                ["Model", "Condition", "Accuracy %"])


def report_label_agreement(df, reference):
    rows = []
    for model in MODELS:
        for cond in CONDITIONS:
            run = df[(df["Model"] == model) & (df["Condition"] == cond)]
            hits = sum(row.Label == reference[row.Principle_ID] for row in run.itertuples())
            rows.append([model, cond, f"{hits}/7", pct(hits, 7)])
    print_table("Label agreement with reference labels", rows,
                ["Model", "Condition", "Agree", "Agree %"])


def report_flip_rates(df):
    rows = []
    for model in MODELS:
        labels = {
            cond: df[(df["Model"] == model) & (df["Condition"] == cond)]
            .set_index("Principle_ID")["Label"]
            for cond in CONDITIONS
        }
        for a, b in combinations(CONDITIONS, 2):
            flips = int((labels[a] != labels[b]).sum())
            rows.append([model, a, b, flips, pct(flips, 7)])
    print_table("Pairwise flip rates (share of the 7 principles whose label differs)", rows,
                ["Model", "Condition A", "Condition B", "Flips", "Flip %"])


def report_judge(runs):
    rows = []
    for model in MODELS:
        for cond in CONDITIONS:
            principles = runs[(model, cond)]
            ras = [
                Fraction(sum(normalize_ras_label(b["human"]["final_label"]) == "ENTAILS"
                             for b in p["judge_ras"]["bullets"]),
                         len(p["judge_ras"]["bullets"]))
                for p in principles
            ]
            entails = sum(int(r * 5) for r in ras)
            # Per-principle JJS = exact mean of the four 1-5 sub-scores (always a quarter value);
            # the judge's own jjs_principle_score is rounded to one decimal and is not used.
            jjs = [Fraction(sum(p["jjs"][d] for d in JJS_DIMENSIONS), 4) for p in principles]
            rows.append([model, cond, f"{entails}/35", round2(sum(ras) / len(ras)),
                         round2(sum(jjs) / len(jjs)),
                         " ".join(f"{float(j):.2f}" for j in jjs)])
    print_table("RAS and JJS per run (after human correction)", rows,
                ["Model", "Condition", "ENTAILS", "RAS", "JJS", "JJS per principle (P1..P7)"])

    total = errors = 0
    by_model = {m: 0 for m in MODELS}
    transitions = {}
    unflagged = []
    for (model, cond), principles in runs.items():
        for i, p in enumerate(principles, start=1):
            for q, b in enumerate(p["judge_ras"]["bullets"], start=1):
                total += 1
                before = normalize_ras_label(b["label"])
                after = normalize_ras_label(b["human"]["final_label"])
                if before == after:
                    continue
                if not b["human"]["override"]:
                    # final_label differs but the override flag was left false
                    unflagged.append(f"{model} {cond} P{i} Q{q}: {before} -> {after}")
                    continue
                errors += 1
                by_model[model] += 1
                transitions[(before, after)] = transitions.get((before, after), 0) + 1
    print("\n=== Judge validation (RAS labels: judge vs. human-corrected, override = true)")
    print(f"Judgements reviewed: {total}")
    print(f"Corrected: {errors} ({pct(errors, total)}%)  " +
          ", ".join(f"{m}: {n}" for m, n in by_model.items()))
    for (before, after), n in sorted(transitions.items(), key=lambda kv: -kv[1]):
        print(f"   {before} -> {after}: {n}")
    if unflagged:
        print("Label changed but override flag false (counted in RAS, not in the error count above):")
        for line in unflagged:
            print(f"   {line}")


def main():
    df = load_master_table()
    reference = load_reference_labels()
    runs = load_judge_runs()
    report_grounding(df)
    report_text_accuracy(df)
    report_label_agreement(df, reference)
    report_flip_rates(df)
    report_judge(runs)


if __name__ == "__main__":
    main()
