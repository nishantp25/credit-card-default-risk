# Credit Card Default Risk | Project Notes

## Current checkpoint

**Resume at Stage 6: build the Streamlit scoring demo.**

Stages 1–4 are complete. Stage 5 evaluation and all three group audits have been run. The full results belong in `reports/RESULTS.md`. Keep the fitted forest and its cutoff frozen when building the app.

## Stage 1 | Environment and repository

- Created the repository from scratch and cloned it to `C:\Projects\credit-card-default-risk` on Windows.
- Set up a project-local `.venv` with Python 3.11.9. Verified the VS Code interpreter by printing `sys.executable`.
- Pinned pandas, xlrd, scikit-learn, matplotlib, Streamlit, and pytest in `requirements.txt`. Verified their imports and ran `python -m pip check`.
- Used `.gitignore` to keep `.venv`, Python caches, the raw workbook, and customer-level test predictions out of Git.
- Learned that `pip check` verifies declared dependency compatibility. Importing each package separately verifies that the interpreter can load it.

## Stage 2 | Data inspection

- Loaded the original UCI workbook with `load_clients()` in `src/credit_risk/data.py`. Used `header=1` because the second Excel row contains the descriptive column names.
- Verified 30,000 rows, 25 columns, 30,000 distinct customer IDs, and zero missing cells.
- Counted 6,636 defaults and 23,364 non-defaults. The observed default rate was 22.12%.
- Preserved repayment codes `-2` and `0` separately. Both occur in the workbook, and UCI's published codebook leaves their meanings unspecified.
- The pinned `xlrd` reader works. Pandas emitted a deprecation warning worth revisiting during a future dependency update.

## Stage 3 | Features and data splits

- Used an explicit list of 19 financial inputs. Customer ID, target, sex, marital status, age, and education are excluded from model inputs.
- Added `months_with_recorded_delay` and `max_recorded_delay_code`, bringing the total to 21 features.
- Checked the difference on a real row: one monthly observation showed a delay, and its delay code was 2. The customer's frequency was 1 and severity was 2.
- Used stratified splits with `random_state=42`: 18,000 training, 6,000 validation, and 6,000 test customers. Verified zero overlapping IDs for all three pairs.

## Stage 4 | Model and cutoff selection

- Compared three models on identical five-fold stratified training splits. Mean AP was 0.5459 for logistic regression, 0.5568 for random forest, and 0.5554 for gradient boosting.
- Selected the forest using the highest mean AP rule. It led gradient boosting by 0.0014.
- Fit the selected forest on all 18,000 training customers. On validation, the 0.50 cutoff produced 224 false alarms and 857 missed defaults, costing 4,509 units.
- Chose cutoff `0.14166170167472678` under the assumption that a missed default costs five times a false alarm. It produced 1,995 false alarms and 252 missed defaults, costing 3,255 units.
- The lower cutoff caught 605 additional defaults at the cost of 1,771 additional false alarms. That saved 1,254 assumed cost units on validation.
- Saved the fitted pipeline and cutoff in `artifacts/credit_default_model.pkl`. Reloading the bundle reproduced the validation counts and cost.

## Stage 5 | Held-out evaluation and reporting

- Applied the frozen forest and cutoff to 6,000 held-out customers. It caught 1,043 defaults, missed 284, falsely flagged 2,017 non-defaulters, and correctly left 2,656 non-defaulters unflagged.
- Test precision was 34.08%, recall was 78.60%, and the model flagged 51.00% of customers. Test cost was 3,437 units under the 5:1 assumption.
- Test ROC-AUC was 0.7722, trapezoidal PR-AUC was 0.5516, and average precision was 0.5520.
- In the highest-risk test group, the observed default rate was 69.33% against a mean predicted risk of 68.16%. Saved the chart to `reports/figures/calibration.png`.
- September repayment status (`PAY_0`) had the largest validation permutation importance, with a mean AP drop of 0.1739. Recomputed both derived delay features after each shuffle. Saved the chart to `reports/figures/permutation_importance.png`.

### Group audit

- Joined the saved test predictions to the demographic fields by customer ID. All 6,000 predictions matched. Each audit grouping reconciled to 3,060 flags, 2,017 false alarms, and 284 missed defaults.
- **Recorded sex:** Male customers had a 43.89% false-alarm rate and a 20.86% missed-default rate. Female customers had a 42.69% false-alarm rate and a 21.80% missed-default rate.
- **Marital status:** Undocumented code `0` had seven customers and zero defaults, so its missed-default rate was undefined. The “other” group missed two of 12 defaults.
- **Age:** Used under 30, 30–39, 40–49, 50–59, and 60+. The 60+ group had 27 false alarms among 53 non-defaulters and six misses among 23 defaulters.
- **Lesson:** Flag rate uses all customers in a group. False-alarm rate uses actual non-defaulters. Missed-default rate uses actual defaulters. Showing the denominator makes small-group percentages easier to interpret.

## Reproducing the project on another computer

- Added `src/credit_risk/__main__.py` so a fresh clone can download the workbook, generate predictions from the committed model, and run the audit.
- With Python 3.11 active, run `python -m pip install -r requirements.txt`, followed by `python -m src.credit_risk`.
- Verified the complete quick start from a fresh macOS clone with Python 3.11.18. It reproduced the Windows confusion-matrix counts and cost.
- Fresh-clone checks on Windows and Linux remain open. [Earlier project checkpoint](2026-11-22-checkpoint.md)

## Next session | Stage 6

1. Start with one real customer example from the public dataset. Use only the approved financial fields in the demo.
2. Load the existing model bundle and use `build_features()` to score that example in Python. Record the score and flag as a reference for checking the app.
3. Build the Streamlit form in small pieces. Show the score, cutoff, and flag decision, then verify that the app and Python give the same result for the same inputs.
4. After the app works, continue with pytest, including a test that fails if a protected attribute reaches the model. Then deploy, finalize the README, and prepare the resume bullets and interview questions.

New-chat prompt: Continue my credit-card-default-risk portfolio project at Stage 6. Start with one real example and the saved model. Explain each small piece before and after the code, then wait for my terminal output.