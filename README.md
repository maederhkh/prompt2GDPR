# Assessing Privacy Policy Compliance with GDPR Article 5 Using Large Language Models: The Role of Prompt Design

This repository contains the appendices, experimental outputs, and analysis scripts for the master's thesis: **"Assessing Privacy Policy Compliance with GDPR Article 5 Using Large Language Models: The Role of Prompt Design"**.

## Abstract Overview

The research investigates the legal reliability and stability of Large Language Models (LLMs) like **GPT-5.2** and **Grok** when evaluating a real-world healthcare privacy policy (Ada Health GmbH). It specifically examines how advanced prompting strategies—ranging from structured zero-shot to complex few-shot prompts—and extended reasoning modes (e.g., GPT's Extended Thinking and Grok's Expert Mode) influence the model's ability to produce legally sound compliance judgments against the seven core principles of GDPR Article 5.

## Repository Structure

The project has been restructured to separate raw experimental results from their subsequent evaluations by automated judges.

### Primary Results and Data
- **[`main_outputs/`](main_outputs/README.md)**: Contains the direct assessments (raw JSON) from GPT-5.2 and Grok. These files include principle-by-principle justifications, verbatim policy clauses, and compliance ratings.
- **[`gemini_judge_output/`](gemini_judge_output/README.md)**: Contains the "LLM-as-judge" evaluation results. Gemini assessed the main model outputs for **Rubric Alignment (RAS)** and **Justification Quality (JJS)**.
- **[`prompts/`](prompts/)**: The exact prompt templates used in all experimental phases, from simple zero-shot instructions to few-shot prompts with contextual legal examples.

### Core Methodology & Research Assets
- **`thesis.pdf`**: The full master's thesis document providing the theoretical background, experimental setup, and detailed analysis of findings.
- **`golden_standard_bullet_points.md`**: A comprehensive evaluation rubric manually developed by a legal expert to score the accuracy and consistency of LLM justifications.
- **`compute_flip_rates.py`**: A script to calculate the "Flip Rate"—the frequency with which a model changes its compliance rating when prompt phrasing is modified.
- **`flip_rate_analysis_v2.csv`**: The tabulated results of the flip rate analysis used in the thesis.

## Measurement Framework

This study evaluates the models across three key dimensions:
1.  **Rubric Alignment Score (RAS)**: Compliance justifications are checked against five specific legal guardrails per GDPR principle.
2.  **Justification Quality Score (JJS)**: Evaluates reasoning on four pillars: traceability, principle correctness, calibration, and no overreach.
3.  **Prompt Stability (Flip Rates)**: Measures how sensitive the model is to prompting variations.

## Getting Started

Follow these steps to set up the environment and explore the analysis scripts:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/maederhkh/prompt2GDPR.git
    cd prompt2GDPR
    ```

2.  **Set Up the Environment**:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Analysis**:
    To recalculate flip rates:
    ```bash
    python compute_flip_rates.py
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
