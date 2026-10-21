# Evaluating Reasoning, Grounding, and Stability in LLM-Based GDPR Compliance Assessment

**Maede Rahmanikhalili**, University of Bologna

Paper: arXiv link to be added

This repository contains the materials for the paper: the prompts, the raw outputs of GPT-5.2 and Grok 4.1, the
LLM-as-judge outputs with the author's corrections, the expert rubric, and the scripts and workbook used to compute
the reported figures. The materials originate from the author's Master's thesis.

## Summary

The study asks whether large language models can assess a real privacy policy, that of the health app provider
Ada Health GmbH, against the seven principles of GDPR Article 5 in a way that is legally sound, grounded in the
policy text and stable across prompt designs. GPT-5.2 and Grok 4.1 were each run under six conditions: one
zero-shot prompt (ZS) and three few-shot prompts (FS1–FS3), with ZS and FS3 repeated in each model's extended
reasoning mode (ZS-Ext, FS3-Ext). The outputs are evaluated on three axes: **reasoning**, by comparing each
justification with an expert rubric written before the runs (RAS) and by an LLM judge's assessment of
justification quality (JJS), both checked by the author; **grounding**, by verifying every cited policy passage
(Evidence Error Rate, EER); and **stability**, by comparing compliance labels with expert reference labels and
across conditions (flip rates).

## Repository structure

| Path | Contents |
|---|---|
| [`main_outputs/`](main_outputs/README.md) | Raw JSON assessments from GPT-5.2 and Grok 4.1 (one file per run). These are the evidence for the paper and are kept exactly as produced. |
| [`gemini_judge_output/`](gemini_judge_output/README.md) | Gemini 3 Flash judge outputs (RAS labels and JJS scores) per run, including the author's corrections in each `human` block |
| [`prompts/`](prompts/README.md) | The prompts for each condition and the judge prompt |
| [`golden_standard_bullet_points.md`](golden_standard_bullet_points.md) | Expert rubric: five questions per principle, with the expert's scores and reasoning |
| [`data/rubric.csv`](data/rubric.csv) | The same rubric in machine-readable form, with reference labels |
| [`docs/evaluation_protocol.md`](docs/evaluation_protocol.md) | How RAS, JJS, EER, label agreement, flip rates and judge validation are defined and computed |
| [`scripts/`](scripts/) | Analysis scripts and their outputs (see [Reproducing the figures](#reproducing-the-figures)) |

## Terminology mapping

Some files predate the paper and use the thesis names. Column names inside data files are left unchanged.

**Metrics and error types**

| In the files | In the paper |
|---|---|
| `FGS`, "Factual Grounding Score", "False-Grounding Score" (e.g. Excel column `section_result FGS`) | **Evidence Error Rate (EER)** = erroneous citations / total citations. 0 = no errors; lower is better. Overall figures are pooled (total errors / total citations). |
| `legally misplaced` (Excel column `SECTION-NOTE`) | **unrelated (U)** |
| `unrelated` (Excel column `SECTION-NOTE`) | **unrelated (U)** |
| `not exist`, non-existent | **non-existent (NE)** |
| "Golden Standard" | expert rubric / reference labels |

**Conditions.** "Ext" means GPT-5.2's extended thinking mode and Grok's expert mode. "Zero-shot.3rd" and
"1st zero-shot" both refer to the final zero-shot prompt, called **ZS** in the paper.

| Paper | Prompt | Mode | Raw output (`main_outputs/<model>/…`) | Name in Excel / flip-rate CSV |
|---|---|---|---|---|
| ZS | [`3rd_version_zero_shot.md`](prompts/3rd_version_zero_shot.md) | standard | `zero_shot/3rd_output.json` | `zero_shot_gpt5.3rd.json`, `zero_shot_grok.3rd.json` / `Zero-Standard` |
| ZS-Ext | [`3rd_version_zero_shot.md`](prompts/3rd_version_zero_shot.md) | extended / expert | GPT: `zero_shot/3rd_output_extended_thinking.json`; Grok: `zero_shot/3rd_output_expert.json` | `Zero-shot.3rd.GPT5.EXTENDED.THINKING.JSON`, `zero-shot.3rd.grok.expert.json` / `Zero-Extended`, `Zero-Expert` |
| FS1 | [`1st_version_few_shot.md`](prompts/1st_version_few_shot.md) | standard | `few_shot/1st_output.json` | `1st few shot output.<GPT5\|Grok>.json` / `Few1` |
| FS2 | [`2nd_version_few_shot.md`](prompts/2nd_version_few_shot.md) | standard | `few_shot/2nd_output.json` | `2nd few shot output.<GPT5\|Grok>.json` / `Few2` |
| FS3 | [`3rd_version_few_shot.md`](prompts/3rd_version_few_shot.md) | standard | `few_shot/3rd_output.json` | `3rd few shot output.<GPT5\|Grok>.json` / `Few3-Standard` |
| FS3-Ext | [`3rd_version_few_shot.md`](prompts/3rd_version_few_shot.md) | extended / expert | GPT: `few_shot/3rd_output_extended_thinking.json`; Grok: `few_shot/3rd_output_expert.json` | `3rd few shot output.GPT5.EXTENDED THINKING.JSON`, `3rd few shot output.Grok.Expert.json` / `Few3-Extended`, `Few3-Expert` |

In the judge outputs, GPT-5.2's extended runs are named `3rd_output_thinking_extended.json`. In the Excel
workbook and the flip-rate CSV, `GPT-5` / `GPT5` refers to **GPT-5.2**.

## Study details

**Models and runs**

| | GPT-5.2 | Grok 4.1 |
|---|---|---|
| Access | ChatGPT Team | X Premium |
| Run dates | 5–6 February 2026 | 5 February 2026 |
| Ext mode | Extended thinking | Expert mode |

Both models were used through their consumer web interfaces, not the API, so sampling parameters could not be
controlled. Each condition was run once, in a fresh chat.

**Judge.** Gemini 3 Flash (thinking mode); judgements produced on 25–27 February 2026. All judgements were reviewed
by the author (see [`docs/evaluation_protocol.md`](docs/evaluation_protocol.md#6-judge-validation)).

**Document assessed.** Ada Health GmbH privacy policy, November 2025 version.

**Legal benchmark.**
- GDPR Article 5 and Recital 39
- Article 29 Working Party, Guidelines on Transparency under Regulation 2016/679 (WP260 rev.01)
- EDPB Guidelines 4/2019 on Article 25 Data Protection by Design and by Default (version 2.0)

**Prompt contents.**
- ZS and FS1 contain excerpts of Article 5; FS2 and FS3 contain only the principle names.
- All versions contain key interpretive points from Recital 39.
- FS1–FS3 use the same CLAUDETTE-based examples, covering lawfulness/fairness/transparency, purpose limitation,
  storage limitation and accuracy.
- FS3 adds WP260 rev.01 and EDPB Guidelines 4/2019.

## Measurement framework

Full definitions are in [`docs/evaluation_protocol.md`](docs/evaluation_protocol.md).

- **RAS** (rubric alignment): share of the five rubric questions per principle labelled `ENTAILS` by the judge,
  averaged over the seven principles.
- **JJS** (justification quality): mean of traceability, principle correctness, calibration and no overreach
  (each 1–5).
- **EER** (grounding): erroneous citations (non-existent or unrelated) / total citations.
- **Label agreement** with the expert reference labels, and **flip rates** between conditions (stability).

Reported RAS and JJS values are after human correction.

## Reproducing the figures

```bash
pip install -r requirements.txt
python scripts/compute_paper_metrics.py
```

[`scripts/compute_paper_metrics.py`](scripts/compute_paper_metrics.py) reads the workbook, the judge outputs and the
rubric, and prints EER (per run, per model, and for data minimisation), Article 5 text accuracy, label agreement,
pairwise flip rates, RAS, JJS and the judge-validation counts.

Other scripts:
- `scripts/analyze_gdpr_outputs.py` parses the raw outputs, checks the reproduced Article 5 text, and writes the
  automatic columns of `scripts/outputs/GDPR_thesis_analysis_results.xlsx`. The grounding columns
  (`section_result FGS`, `SECTION-NOTE`) of the `Master_Table` sheet were filled in by hand, and the workbook still
  uses the file names from before the outputs were renamed (see the mapping above).
- `scripts/compute_flip_rates.py` writes `scripts/outputs/flip_rate_analysis_v2.csv`.

## How to cite

The arXiv identifier will be added once available. Until then:

```bibtex
@misc{rahmanikhalili2026gdpr,
  title         = {Evaluating Reasoning, Grounding, and Stability in LLM-Based GDPR Compliance Assessment},
  author        = {Rahmanikhalili, Maede},
  year          = {2026},
  eprint        = {XXXX.XXXXX},
  archivePrefix = {arXiv},
  note          = {arXiv identifier to be added}
}
```

Citation metadata is also in [`CITATION.cff`](CITATION.cff).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
