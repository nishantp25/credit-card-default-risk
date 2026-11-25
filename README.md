# Credit Card Default Risk

Can six months of credit card history help predict next-month default? This project compares three classifiers, selects a review cutoff on validation data, and serves the selected model through a Streamlit app.

On 6,000 held-out customers, the random forest caught **1,043 of 1,327 defaults (78.60% recall)**. It flagged **3,060 customers (51.00%)**, and **34.08%** of flagged customers actually defaulted.

## Quick start

Clone the repository, open its root folder in a terminal, and use Python 3.11.

### 1. Create and activate a virtual environment

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

### 2. Install dependencies

```sh
python -m pip install -r requirements.txt
```

### 3. Launch the Streamlit app

```sh
python -m streamlit run app.py
```

Open the local URL printed in the terminal. The app starts with a real UCI customer example and the saved random forest. You can edit all 19 financial inputs: the credit limit, six repayment statuses, six bill amounts, and six payment amounts. Click **Calculate risk** to see the estimated default risk, review cutoff, and decision.

To check the demo against a known result, leave all amounts and the other five months at their original values:

| September repayment code | Estimated risk | Decision |
|---|---:|---|
| `-1` (original example) | 11.382644% | No flag |
| `2` (edited example) | 36.948080% | Flag for review |

The app and the Python scoring function share the same feature calculations. The decision uses the full-precision score and cutoff before the numbers are rounded for display.

### Run the command-line audit

```sh
python -m src.credit_risk
```

The first audit run needs internet access to download the original UCI workbook. It loads the saved model and cutoff, scores the held-out customers, and saves the individual predictions locally. Later runs reuse those files.

A successful audit reports **6,000 predictions, 0 unmatched customer IDs, 3,060 flags, 2,017 false alarms, and 284 missed defaults**. It prints group tables for recorded sex, marital status, and age band.

The command-line quick start was verified on a fresh macOS clone. The model and audit also ran on Windows. Fresh-clone checks on Windows and Linux are pending.

### Run the tests

```sh
python -m pytest -q
```

The first regression test loads the committed example and model bundle, then checks that `score_customer()` reproduces the verified score and decision. Additional tests are in progress.

## Data and features

The UCI *Default of Credit Card Clients* dataset contains 30,000 customer records from Taiwan, with repayment history from April through September 2005. A total of 6,636 customers (22.12%) defaulted the following month. [Dataset and codebook, I-Cheng Yeh, CC BY 4.0](https://doi.org/10.24432/C55S3H)

The model uses 19 financial inputs and two derived features:

- **Months with a recorded delay** counts how many of the six monthly statuses show a documented repayment delay.
- **Maximum recorded delay code** measures the severity of the largest documented delay.

The workbook contains repayment codes `-2` and `0` whose meanings are unspecified in the published codebook. The pipeline preserves them as distinct categories.

Customer ID, education, sex, marital status, age, and the outcome label are excluded from model inputs. The audit joins demographic fields to saved predictions by customer ID.

## Model selection

The stratified split produced 18,000 training, 6,000 validation, and 6,000 test customers. All three pairs of splits shared zero customer IDs. The models were compared on the same five training folds, using mean average precision (AP) as the selection metric.

| Model | Mean ROC-AUC | Mean PR-AUC (trapezoidal) | Mean AP |
|---|---:|---:|---:|
| Logistic regression | 0.7744 | 0.5453 | 0.5459 |
| Random forest | 0.7814 | 0.5563 | 0.5568 |
| Gradient boosting | 0.7787 | 0.5552 | 0.5554 |

The random forest led gradient boosting by 0.0014 mean AP. I fit the forest on all 18,000 training customers and chose its cutoff on validation using an assumed cost of **five units per missed default** and **one unit per false alarm**.

Lowering the cutoff from `0.50` to `0.14166170167472678` caught 605 additional defaults and produced 1,771 additional false alarms. Under the 5:1 assumption, validation cost fell from **4,509 to 3,255 units**. The fitted model and cutoff are stored together in `artifacts/credit_default_model.pkl`.

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

The audit reports flag, false-alarm, and missed-default rates with their denominators. For example, the model missed 6 of 23 defaults in the 60+ group. One additional miss would move that group's missed-default rate from 26.09% to 30.43%. [Full results and group tables](reports/RESULTS.md)

The data cover one historical cohort in Taiwan. The group comparisons describe that cohort, and the 5:1 cost ratio is an assumption. Different costs could favor a different review cutoff.

## Project status

The data pipeline, evaluation, group audit, and local Streamlit demo are complete. The first scoring regression test passes. Work continues on test coverage and deployment. [Project notes](NOTES.md)