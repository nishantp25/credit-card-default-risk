# Credit Card Default Risk

Can six months of credit card history help predict next-month default? This project compares three classifiers, selects a review cutoff on validation data, and serves the selected model through a Streamlit app.

On 6,000 held-out customers, the random forest caught **1,043 of 1,327 defaults (78.60% recall)**. It flagged **3,060 customers (51.00%)**, and **34.08%** of flagged customers actually defaulted.

## Quick start

Clone the repository and open its root folder in a terminal. Use Python 3.11.

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

Open the local URL printed in the terminal. The app starts with a real UCI customer example. You can edit the credit limit, six monthly repayment statuses, six bill amounts, and six payment amounts. Click **Calculate risk** to see the estimated default risk, review cutoff, and decision.

To verify the demo, leave the financial amounts and the other five months at their original values:

| September repayment code | Estimated risk | Decision |
|---|---:|---|
| `-1` (original example) | 11.382644% | No flag |
| `2` (edited example) | 36.948080% | Flag for review |

The app uses the same feature calculations as the Python scoring function. It applies the full-precision cutoff before rounding the score for display.

### Run the command-line audit

```sh
python -m src.credit_risk
```

The first audit run needs internet access to download the original UCI workbook. The program loads the saved forest and cutoff, scores the held-out customers, and saves the individual predictions locally. Later runs reuse the local files.

A successful audit reports **6,000 predictions, 0 unmatched IDs, 3,060 flags, 2,017 false alarms, and 284 missed defaults**. It prints separate tables for recorded sex, marital status, and age band.

The complete command-line quick start was verified on a fresh macOS clone. The model and audit also ran on Windows. Fresh-clone checks on Windows and Linux are pending.

### Run the tests

```sh
python -m pytest -q
```

All **seven tests passed** on macOS. They cover:

- The original example’s score and decision using the saved model.
- Exclusion of `SEX`, `MARRIAGE`, and `AGE` from engineered inputs and from the fitted pipeline’s recorded input columns.
- Repayment-delay frequency and severity for two verified cases.
- The review decision at the cutoff and immediately below it.
- Split sizes, customer-ID separation, and coverage of the original workbook.

The split test downloads the workbook if it is missing, so the first test run on a fresh clone needs internet access. The verified run produced one pandas warning about future removal of the `xlrd` reader.

## Data and features

The UCI *Default of Credit Card Clients* dataset contains 30,000 customer records from Taiwan, with repayment history from April through September 2005. A total of 6,636 customers (22.12%) defaulted the following month. [Dataset and codebook, I-Cheng Yeh, CC BY 4.0](https://doi.org/10.24432/C55S3H)

The model uses 19 financial inputs and two derived features:

- **Months with a recorded delay** counts how many of the six monthly statuses show a documented repayment delay.
- **Maximum recorded delay code** measures the severity of the largest documented delay.

The workbook contains repayment codes `-2` and `0` whose meanings are unspecified in the published codebook. The pipeline preserves them as distinct categories.

Customer ID, education, sex, marital status, age, and the outcome label are excluded from model inputs. The audit joins demographic fields to saved predictions by customer ID.

## Model selection

The stratified split produced 18,000 training, 6,000 validation, and 6,000 test customers. All three pairs of splits shared zero customer IDs. The models were compared on the same five training folds using mean average precision (AP) as the selection metric.

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

The data cover one historical cohort in Taiwan. The group comparisons describe that cohort. The 5:1 cost ratio is a project assumption, and different costs could favor a different review cutoff.

## Project status

The data pipeline, model evaluation, group audit, local Streamlit demo, and seven-test suite are complete. The next stage is deployment and verification of the live app against the two locally verified examples. [Project notes](NOTES.md)