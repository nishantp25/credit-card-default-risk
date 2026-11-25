# Credit Card Default Risk | Project Notes

## Current checkpoint

**Stages 1–7 are complete. Resume at Stage 8: deploy the Streamlit app and verify the live demo.**

The latest local run of `python -m pytest -q` finished with **7 passed, 1 warning in 2.08 seconds** on macOS. The warning concerns the Excel reader. The frozen model, cutoff, and both browser reference scores are recorded below.

## Stage 1 | Environment and repository

- Created the repository from scratch, cloned it to `C:\Projects\credit-card-default-risk` on Windows, and opened it in VS Code.
- Set up a project-local `.venv` with Python 3.11.9 on Windows and later Python 3.11.18 on macOS.
- Pinned pandas, xlrd, scikit-learn, matplotlib, Streamlit, and pytest in `requirements.txt`.
- Used `sys.executable` to verify which Python interpreter VS Code was running. Used `pip check` to verify dependency compatibility and separate imports to confirm each package loaded.
- Used `.gitignore` to keep `.venv`, Python caches, the raw workbook, and individual test predictions out of Git.

## Stage 2 | Data inspection

- Loaded the original UCI workbook with `load_clients()` in `src/credit_risk/data.py`. Used `header=1` because the second Excel row contains the descriptive column names.
- Verified 30,000 rows, 25 columns, 30,000 distinct customer IDs, and zero missing cells.
- Counted 6,636 defaults and 23,364 non-defaults. The observed default rate was 22.12%.
- Preserved repayment codes `-2` and `0` separately. Both appear in the workbook, and the published codebook leaves their meanings unspecified.

## Stage 3 | Features and data splits

- Selected 19 financial inputs explicitly. Excluded customer ID, outcome, education, sex, marital status, and age from the model inputs.
- Added `months_with_recorded_delay` and `max_recorded_delay_code`, bringing the total to 21 features.
- Checked the distinction on a real row: one month showed a delay, and its delay code was 2. The customer's frequency was 1 and severity was 2.
- Used stratified splits with `random_state=42`: 18,000 training, 6,000 validation, and 6,000 test customers. Verified zero overlapping customer IDs for every pair.

## Stage 4 | Model and cutoff selection

- Compared three models on identical five-fold training splits. Mean AP was 0.5459 for logistic regression, 0.5568 for random forest, and 0.5554 for gradient boosting.
- Selected the forest using the highest mean AP rule. It led gradient boosting by 0.0014.
- Fit the selected forest on all training customers. On validation, a `0.50` cutoff produced 224 false alarms and 857 missed defaults, costing 4,509 units.
- Selected cutoff `0.14166170167472678` under the assumption that a missed default costs five units and a false alarm costs one. It produced 1,995 false alarms and 252 missed defaults, costing 3,255 units.
- The lower cutoff caught 605 additional defaults and produced 1,771 additional false alarms, saving 1,254 assumed cost units on validation.
- Saved the fitted pipeline and full-precision cutoff together in `artifacts/credit_default_model.pkl`. Reloading the bundle reproduced the validation counts and cost.

## Stage 5 | Held-out evaluation and group audit

- Scored the 6,000 held-out customers with the frozen forest and cutoff. It caught 1,043 defaults, missed 284, falsely flagged 2,017 non-defaulters, and correctly left 2,656 non-defaulters unflagged.
- Precision was 34.08%, recall was 78.60%, and 51.00% of customers were flagged. Test cost was 3,437 units.
- Test ROC-AUC was 0.7722, trapezoidal PR-AUC was 0.5516, and AP was 0.5520.
- In the highest-risk test group, mean predicted risk was 68.16% and observed default was 69.33%.
- September repayment status (`PAY_0`) had the largest validation permutation importance, with a mean AP drop of 0.1739. Both delay summaries were recalculated after each shuffle.
- Saved `reports/figures/calibration.png`, `reports/figures/permutation_importance.png`, and `reports/RESULTS.md`.

### Group audit findings

- All 6,000 predictions matched demographic records by ID. Each grouping reconciled to 3,060 flags, 2,017 false alarms, and 284 missed defaults.
- Male customers had a 43.89% false-alarm rate and a 20.86% missed-default rate. Female customers had a 42.69% false-alarm rate and a 21.80% missed-default rate.
- Marital-status code `0` had seven customers and zero defaults, so its missed-default rate was undefined. The “other” group missed two of 12 defaults.
- The age bands were under 30, 30–39, 40–49, 50–59, and 60+. The 60+ group had 27 false alarms among 53 non-defaulters and six misses among 23 defaulters.
- What I learned: flag rate uses all customers in a group. False-alarm rate uses actual non-defaulters. Missed-default rate uses actual defaulters. The denominator explains why a single case can noticeably change a small group's rate.

### Reproducibility

- Added `src/credit_risk/__main__.py` so the command-line audit can download the workbook, generate missing test predictions from the committed model, and run the group summaries.
- Verified the complete quick start on a fresh macOS clone. It reproduced the Windows test confusion matrix and cost.
- Fresh-clone verification on Windows and Linux remains open.

## Stage 6 | Streamlit scoring demo

- Created `src/credit_risk/scoring.py`. `score_customer()` accepts one customer row, calls the shared `build_features()` function, obtains the default-class score, and applies the frozen cutoff.
- Saved a real held-out customer's 19 approved financial inputs in `examples/customer.json`. Used the ID to look up the original test prediction during verification.
- Built `app.py` with editable fields for the credit limit, six repayment statuses, six bill amounts, and six payment amounts.
- Used `st.cache_resource` to reuse the fitted model bundle. The form submits all fields together when the user selects **Calculate risk**.
- Verified the following browser outcomes with the other 18 inputs held constant:

| September code | Estimated risk | Decision |
|---|---:|---|
| `-1` (original example) | 11.382644% | No flag |
| `2` (edited example) | 36.948080% | Flag for review |

- Restoring September to `-1` after adding the bill and payment fields reproduced 11.382644% and No flag.
- Commit `06d5f7b` saved the app, scoring function, and example customer.

## Stage 7 | Automated tests

Ran the full suite from the repository root:

```sh
python -m pytest -q
```

**Observed result on macOS: `7 passed, 1 warning in 2.08s`.**

| Test file | Cases | What the tests check |
|---|---:|---|
| `tests/test_scoring.py` | 2 | The saved model reproduces the original example's score and decision. Equality at the cutoff produces a flag, and a score immediately below the cutoff stays unflagged. |
| `tests/test_model_inputs.py` | 2 | Adding empty `SEX`, `MARRIAGE`, and `AGE` audit fields leaves the example's engineered features unchanged. The saved pipeline's fitted input names exclude all three fields. |
| `tests/test_features.py` | 2 | The original example gives delay frequency 0 and severity 0. Changing September to code 2 gives frequency 1 and severity 2. |
| `tests/test_splits.py` | 1 | The real workbook splits into 18,000 / 6,000 / 6,000 rows. The three ID sets are pairwise disjoint and together cover the original customers. |

### What I learned from testing

- Checking feature-building code and inspecting the saved pipeline cover two places where an excluded attribute could enter the workflow.
- The cutoff comparison uses `>=` at full precision. Two values can look identical on screen and still produce different decisions.
- Correct split sizes alone cannot prove customer isolation. Checking ID overlap detects leakage, and checking the union detects missing customers.
- The split test emitted `Pandas4Warning` at `src/credit_risk/data.py` when pandas read the `.xls` workbook. The pinned reader successfully loaded the data. During a future dependency update, evaluate the suggested `calamine` engine and rerun the suite.

## Stage 8 | Next session

1. Commit the completed Stage 7 tests and updated documentation, then confirm the deployment branch contains `app.py`, `examples/customer.json`, `requirements.txt`, and `artifacts/credit_default_model.pkl`.
2. Deploy the Streamlit app using `app.py` as the entry point and Python 3.11.
3. Check the original example in the live browser: 11.382644% risk and No flag.
4. Change only September from `-1` to `2`: 36.948080% risk and Flag for review.
5. Add the verified deployment link to `README.md` and record the live checks here.
6. Prepare three resume bullets using measured project results, ten interview questions with short answers, and a five-question mock interview conducted one question at a time.

## Resume in a new chat

Continue my credit-card-default-risk portfolio project at Stage 8. The local Streamlit app works and all seven tests passed. Start by checking the Git state, then walk me through deployment one small step at a time. Give me complete README.md and NOTES.md files whenever either needs an update. I handle all GitHub pushes myself.

[November 22 checkpoint](2026-11-22-checkpoint.md) · [Full measured results](reports/RESULTS.md)