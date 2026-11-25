# Credit Card Default Risk

Can six months of repayment history help identify which credit card customers will default the following month? This project compares three classifiers, selects a risk cutoff using an explicit cost assumption, and evaluates the selected model on 6,000 held-out customers.

The random forest caught **1,043 of 1,327 defaults (78.60% recall)**. It flagged **3,060 of 6,000 customers (51.00%)**, and **34.08%** of flagged customers actually defaulted.

## Quick start

Clone the repository and open its root folder in a terminal. Use Python 3.11. The first run needs internet access to download the dataset.

### Create and activate a virtual environment

**Windows PowerShell**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS or Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Install and run

With the environment active, run:

```sh
python -m pip install -r requirements.txt
python -m src.credit_risk
```

On the first run, the program downloads the UCI workbook, loads the saved random forest and cutoff, generates test predictions, and runs the group audit. Later runs reuse the local workbook and predictions.

A successful run reports **6,000 test predictions, 0 unmatched IDs, 3,060 flags, 2,017 false alarms, and 284 missed defaults**. It prints separate audit tables for recorded sex, marital status, and age band.

The complete quick start was verified on a fresh macOS clone. The model and audit also ran on Windows. Fresh-clone checks on Windows and Linux are pending.

## Data and approach

The UCI *Default of Credit Card Clients* dataset contains 30,000 customer records from Taiwan, with repayment history from April through September 2005. In the workbook, 6,636 customers (22.12%) defaulted the following month. [Dataset and codebook, I-Cheng Yeh, CC BY 4.0](https://doi.org/10.24432/C55S3H)

- Selected 19 financial inputs covering credit limit, repayment status, bill amounts, and payment amounts. Added two features to distinguish delay frequency from severity: the number of months showing a documented delay and the highest recorded delay code.
- Preserved repayment codes `-2` and `0` as distinct categories because the published codebook leaves their meanings unspecified.
- Excluded customer ID, education, sex, marital status, age, and the outcome label from the model inputs. Demographic fields were joined to predictions by customer ID for the audit.
- Used stratified splits of 18,000 training, 6,000 validation, and 6,000 test customers. All three pairs of splits shared zero customer IDs.

## Model selection

All three models used the same five stratified training folds. The selection metric was mean average precision (AP).

| Model | Mean ROC-AUC | Mean PR-AUC (trapezoidal) | Mean AP |
|---|---:|---:|---:|
| Logistic regression | 0.7744 | 0.5453 | 0.5459 |
| Random forest | 0.7814 | 0.5563 | 0.5568 |
| Gradient boosting | 0.7787 | 0.5552 | 0.5554 |

The random forest led gradient boosting by 0.0014 mean AP. After fitting the forest on all 18,000 training customers, I chose its cutoff on validation using an assumed cost of **five units per missed default** and **one unit per false alarm**.

Lowering the cutoff from `0.50` to `0.14166170167472678` caught 605 additional defaults and produced 1,771 additional false alarms. Under the 5:1 assumption, validation cost fell from **4,509 to 3,255 units**. The fitted model and full-precision cutoff are saved together in `artifacts/credit_default_model.pkl`.

## Held-out results

| Measure | Result |
|---|---:|
| ROC-AUC | 0.7722 |
| PR-AUC (trapezoidal) | 0.5516 |
| Average precision | 0.5520 |
| Defaults caught / missed | 1,043 / 284 |
| Non-defaulters falsely flagged / correctly unflagged | 2,017 / 2,656 |
| Cost under the 5:1 assumption | 3,437 units |

In the highest-risk test group, mean predicted risk was 68.16% and the observed default rate was 69.33%. On validation, shuffling September repayment status produced the largest mean drop in AP (0.1739). [Calibration chart](reports/figures/calibration.png) · [Permutation importance chart](reports/figures/permutation_importance.png)

## Group audit and limitations

The audit reports flag rates, false-alarm rates, and missed-default rates by recorded sex, marital status, and age band. Each rate is accompanied by counts so readers can judge how much data supports it. For example, the 60+ group missed 6 of 23 actual defaults. One additional miss would move its missed-default rate from 26.09% to 30.43%. [Full results and group denominators](reports/RESULTS.md)

The data cover one historical cohort in Taiwan. The 5:1 cost ratio is a project assumption, and different costs could favor a different cutoff. The group comparisons describe outcomes in this test cohort.

## Project status

Data preparation, model comparison, cutoff selection, held-out evaluation, and the command-line audit are complete. The next stage is a Streamlit scoring demo, followed by the pytest suite and deployment. [Project notes](NOTES.md)