# Credit Card Default Risk | Project Notes

## Current checkpoint

**Stage 6 is complete. Stage 7 is in progress.**

The Streamlit app accepts all 19 financial inputs. I verified the original example and an edited September repayment status in the browser. The first pytest regression test passed. Next: add a test that fails if a protected attribute reaches the model.

## Stage 1 | Environment and repository

- Created the repository from scratch, cloned it to `C:\Projects\credit-card-default-risk` on Windows, and opened it in VS Code.
- Set up a project-local `.venv` with Python 3.11.9 on Windows and later Python 3.11.18 on macOS.
- Pinned pandas, xlrd, scikit-learn, matplotlib, Streamlit, and pytest in `requirements.txt`.
- Used `sys.executable` to verify which Python interpreter VS Code was running. Used `pip check` for dependency compatibility and separate import checks to confirm the packages loaded.
- Added Git ignore rules for `.venv`, Python caches, the raw workbook, and individual test predictions.

## Stage 2 | Data inspection

- Loaded the original UCI workbook with `load_clients()` in `src/credit_risk/data.py`. Used `header=1` because the second Excel row contains the descriptive column names.
- Verified 30,000 rows, 25 columns, 30,000 distinct customer IDs, and zero missing cells.
- Counted 6,636 defaults and 23,364 non-defaults. The observed default rate was 22.12%.
- Preserved repayment codes `-2` and `0` separately. Both appear in the workbook, and the UCI codebook leaves their meanings unspecified.
- The pinned `xlrd` reader works. During the Windows run, pandas emitted a deprecation warning to revisit during a future dependency update.

## Stage 3 | Features and data splits

- Selected 19 financial inputs explicitly. Customer ID, outcome, education, sex, marital status, and age are excluded from model inputs.
- Added `months_with_recorded_delay` and `max_recorded_delay_code`, bringing the total to 21 features.
- Checked the distinction on a real row: one month showed a delay, and its delay code was 2. The customer's frequency was 1 and severity was 2.
- Created stratified splits with `random_state=42`: 18,000 training, 6,000 validation, and 6,000 test customers. Verified zero overlapping customer IDs for every pair.

## Stage 4 | Model and cutoff selection

- Compared all three models on the same five training folds. Mean AP was 0.5459 for logistic regression, 0.5568 for random forest, and 0.5554 for gradient boosting.
- Selected the forest using the highest mean AP rule. Its lead over boosting was 0.0014.
- Fit the selected forest on all training customers. On validation, the `0.50` cutoff produced 224 false alarms and 857 missed defaults, costing 4,509 units.
- Selected cutoff `0.14166170167472678` using an assumed cost of five units per missed default and one per false alarm. It produced 1,995 false alarms and 252 missed defaults, costing 3,255 units.
- The lower cutoff caught 605 additional defaults and produced 1,771 additional false alarms, saving 1,254 assumed cost units.
- Saved the fitted pipeline and cutoff together in `artifacts/credit_default_model.pkl`. Reloading the bundle reproduced the validation counts and cost.

## Stage 5 | Held-out evaluation and group audit

- Scored the 6,000 held-out customers using the frozen forest and cutoff. It caught 1,043 defaults, missed 284, falsely flagged 2,017 non-defaulters, and correctly left 2,656 non-defaulters unflagged.
- Precision was 34.08%, recall was 78.60%, and 51.00% of customers were flagged. Test cost was 3,437 units.
- Test ROC-AUC was 0.7722, trapezoidal PR-AUC was 0.5516, and AP was 0.5520.
- In the highest-risk test group, mean predicted risk was 68.16% and observed default was 69.33%.
- September repayment status (`PAY_0`) had the largest validation permutation importance, with a mean AP drop of 0.1739. Both delay summaries were recalculated after each shuffle.
- Saved `reports/figures/calibration.png`, `reports/figures/permutation_importance.png`, and `reports/RESULTS.md`.

### What the audit showed

- All 6,000 test predictions matched demographic records by ID. Each grouping reconciled to 3,060 flags, 2,017 false alarms, and 284 missed defaults.
- Male customers had a 43.89% false-alarm rate and a 20.86% missed-default rate. Female customers had a 42.69% false-alarm rate and a 21.80% missed-default rate.
- Marital-status code `0` had seven customers and zero defaults, so its missed-default rate was undefined. The “other” group missed two of 12 defaults.
- The age bands were under 30, 30–39, 40–49, 50–59, and 60+. The 60+ group had 27 false alarms among 53 non-defaulters and six misses among 23 defaulters.
- What I learned: flag rate uses every customer in the group. False-alarm rate uses actual non-defaulters. Missed-default rate uses actual defaulters. The denominator explains why one case can noticeably change a small group's rate.

### Reproducibility

- Added `src/credit_risk/__main__.py` to download the workbook, generate missing test predictions from the committed model, and run the audit.
- Verified the complete quick start on a fresh macOS clone. It reproduced the Windows test confusion matrix and cost.
- Fresh-clone verification on Windows and Linux remains open.

## Stage 6 | Streamlit scoring demo

- Created `src/credit_risk/scoring.py`. `score_customer()` accepts one customer row, calls the shared `build_features()` function, obtains the default-class score, and applies the frozen cutoff.
- Saved the 19 financial fields from a real held-out example in `examples/customer.json`. Used the customer ID to look up its original test prediction during verification. The example file contains only the approved inputs.
- Verified that direct Python scoring reproduced the example's saved test score and decision.
- Built `app.py` with editable fields for six monthly repayment statuses, the credit limit, six bills, and six payments. The form submits the fields together when the user selects **Calculate risk**.
- Used `st.cache_resource` to reuse the loaded model bundle. Applied the cutoff at full precision and formatted the result afterward.
- Verified both browser cases with the other 18 inputs held constant:

| September code | Estimated risk | Decision |
|---|---:|---|
| `-1` (original example) | 11.382644% | No flag |
| `2` (edited example) | 36.948080% | Flag for review |

- Changed September back to `-1` after adding the bill and payment fields. The browser returned to 11.382644% and No flag.
- Commit `06d5f7b` saved `app.py`, `examples/customer.json`, and `src/credit_risk/scoring.py`.

## Stage 7 | Tests in progress

Added `tests/test_scoring.py`. The first regression test loads the real example and saved model, checks the original probability against `0.11382644` with a small rounding tolerance, and checks that the customer is unflagged.

Verified command:

```sh
python -m pytest -q tests/test_scoring.py
```

Observed result on macOS: **1 passed in 1.83s**.

### Next steps

1. Add a regression test covering `SEX`, `MARRIAGE`, and `AGE`. Check the feature-building path and the input columns recorded by the fitted pipeline.
2. Add focused tests for delay-feature calculations, split isolation, and the cutoff boundary.
3. Run the complete suite with `python -m pytest -q` and record the actual result.
4. Deploy the Streamlit app, verify the live example, and update the README with the deployment link.
5. Prepare three resume bullets using verified measurements, ten interview questions with short answers, and a five-question mock interview.

## Resume in a new chat

Continue Stage 7 of my credit-card-default-risk project. The Streamlit demo is complete and the original-example scoring test passes. Start with the protected-attribute regression test. Explain each small piece, give me the exact command to run, and wait for my output.

[November 22 checkpoint](2026-11-22-checkpoint.md) · [Full measured results](reports/RESULTS.md)