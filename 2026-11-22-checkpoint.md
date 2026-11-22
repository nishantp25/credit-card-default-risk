# Credit Card Default Risk | November 22, 2026

## Where to resume

Stages 1–4 are complete. Stage 5 is in progress. The frozen random forest has already been evaluated on the held-out test set.

Next task: extend `src/credit_risk/audit.py` to calculate false-positive and false-negative rates by group using the saved test predictions.

## Data and setup

- Built the project from scratch on Windows using PowerShell, VS Code, Git, and Python 3.11.9.
- Recorded the six direct dependencies in `requirements.txt`. The project uses a local `.venv`.
- Loaded the UCI Default of Credit Card Clients workbook with pandas using `header=1`. The second Excel row contains the descriptive column names.
- Verified 30,000 rows, 25 columns, 30,000 unique customer IDs, and zero missing cells.
- Counted 6,636 next-month defaults, giving an observed default rate of 22.12%.
- The pinned Excel reader works. Pandas issued a deprecation warning for the `xlrd` engine.

## Features and data splits

- Selected 19 financial inputs: credit limit, six repayment statuses, six bill amounts, and six payment amounts.
- Excluded customer ID, the target, sex, marital status, age, and education from the model inputs.
- Preserved repayment codes `-2` and `0` separately because UCI’s published codebook leaves their meanings unspecified.
- Added `months_with_recorded_delay` and `max_recorded_delay_code`, bringing the total to 21 features.
- Verified the distinction on a real customer: one month showed a delay, and the largest recorded delay code was 2.
- Used stratified splits with `random_state=42`: 18,000 training customers, 6,000 validation customers, and 6,000 test customers. All three pairwise customer-ID overlap counts were zero.

## Model comparison

Compared all three models on the same five stratified training folds. The selection metric was mean average precision (AP).

| Model | Mean ROC-AUC | Mean PR-AUC (trapezoidal) | Mean AP |
|---|---:|---:|---:|
| Logistic regression | 0.7744 | 0.5453 | 0.5459 |
| Random forest | 0.7814 | 0.5563 | 0.5568 |
| Gradient boosting | 0.7787 | 0.5552 | 0.5554 |

Selected the random forest. Its mean AP exceeded gradient boosting by 0.0014.

## Cutoff selection

Fit the selected forest on the 18,000 training customers. Chose the cutoff on validation using an assumed cost of one unit per false alarm and five units per missed default.

| Validation cutoff | False alarms | Missed defaults | Cost units |
|---|---:|---:|---:|
| 0.50 | 224 | 857 | 4,509 |
| 0.14166170167472678 | 1,995 | 252 | 3,255 |

Lowering the cutoff caught 605 additional defaults and produced 1,771 additional false alarms. Under the 5:1 assumption, the cost fell by 1,254 units, or 27.8%.

Saved the fitted pipeline and full-precision cutoff in `artifacts/credit_default_model.pkl`. Reloading the bundle reproduced the validation counts and cost. Commit `1bdc5f3` contains the frozen bundle.

## Held-out test results

Evaluated the frozen model and cutoff on 6,000 test customers.

| Measure | Result |
|---|---:|
| Actual defaults | 1,327 |
| Defaults flagged | 1,043 |
| Missed defaults | 284 |
| False alarms | 2,017 |
| True negatives | 2,656 |
| Customers flagged | 3,060 of 6,000 (51.00%) |
| Precision | 34.08% |
| Recall | 78.60% |
| ROC-AUC | 0.7722 |
| PR-AUC (trapezoidal) | 0.5516 |
| Average precision | 0.5520 |
| Cost under the 5:1 assumption | 3,437 units |

The model caught about four in five defaults while flagging just over half of all test customers for review. Individual test predictions are stored locally in `artifacts/test_predictions.csv` and ignored by Git.

## Calibration and feature importance

- Calibration chart: `reports/figures/calibration.png`. In the highest-risk test group, average predicted risk was 68.16% and the observed default rate was 69.33%. The model underestimated risk in that group by 1.17 percentage points.
- Permutation importance chart: `reports/figures/permutation_importance.png`. Each raw input was shuffled five times on validation customers. The derived delay features were recalculated after each shuffle.

| Raw input | Mean decrease in validation AP |
|---|---:|
| PAY_0 | 0.1739 |
| PAY_2 | 0.0257 |
| PAY_3 | 0.0103 |
| LIMIT_BAL | 0.0085 |
| PAY_4 | 0.0076 |

September repayment status (`PAY_0`) produced the largest measured drop in AP when shuffled.

## Group audit checkpoint

Joined the saved test predictions to demographic fields by customer ID. All 6,000 predictions matched, with zero unmatched IDs. The group totals reproduced all 3,060 flags.

| Recorded sex | Customers | Flagged | Flag rate |
|---|---:|---:|---:|
| Male (1) | 2,402 | 1,252 | 52.12% |
| Female (2) | 3,598 | 1,808 | 50.25% |

The observed flag-rate difference was about 1.87 percentage points. To understand how the groups experienced errors, the next step is to calculate false-alarm and missed-default rates with their respective denominators.

## Next session

1. From the project root, run `.\.venv\Scripts\python.exe -m src.credit_risk.audit` to reproduce the current table.
2. Extend the audit to report false-positive rate (false alarms divided by actual non-defaults) and false-negative rate (missed defaults divided by actual defaults). Show counts and denominators by recorded sex, marital status, and age band. Document the age-band boundaries and identify groups with small denominators.
3. Write `reports/RESULTS.md` with the measured results, audit findings, and limitations of this historical Taiwan dataset.
4. Continue with the Streamlit demo, pytest suite, deployment, final README, resume bullets, and interview preparation.

New-chat prompt: Continue Stage 5 of my credit-card-default-risk project from this checkpoint. Start with group error rates in audit.py. Keep the fitted model and cutoff frozen. Explain each small piece and wait for my PowerShell output.