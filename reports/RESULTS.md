# Credit Card Default Risk | Results

The frozen random forest caught 1,043 of 1,327 defaults on the held-out test set. It flagged 3,060 of 6,000 customers for review, giving 78.60% recall and 34.08% precision.

## Model selection

The dataset contained 30,000 customers and 6,636 next-month defaults. We used 18,000 customers for training, 6,000 for cutoff selection, and 6,000 for final testing. The splits shared zero customer IDs.

All three models used the same five stratified training folds. Mean average precision (AP) was the model-selection metric.

| Model | Mean ROC-AUC | Mean PR-AUC (trapezoidal) | Mean AP |
|---|---:|---:|---:|
| Logistic regression | 0.7744 | 0.5453 | 0.5459 |
| Random forest | 0.7814 | 0.5563 | 0.5568 |
| Gradient boosting | 0.7787 | 0.5552 | 0.5554 |

The random forest ranked first by mean AP, ahead of gradient boosting by 0.0014.

## Cutoff selection on validation

The cost assumption assigned one unit to a false alarm and five to a missed default. We fit the forest on all training customers and selected the cutoff using validation scores.

| Cutoff | False alarms | Missed defaults | Cost units |
|---|---:|---:|---:|
| 0.50 | 224 | 857 | 4,509 |
| 0.14166170167472678 | 1,995 | 252 | 3,255 |

Lowering the cutoff caught 605 additional defaults and produced 1,771 additional false alarms. Under the 5:1 assumption, validation cost fell by 1,254 units (27.8%). The fitted model and full-precision cutoff were frozen before test evaluation.

## Held-out test results

| Actual outcome | Flagged | Unflagged | Total |
|---|---:|---:|---:|
| Default | 1,043 | 284 | 1,327 |
| No default | 2,017 | 2,656 | 4,673 |
| Total | 3,060 | 2,940 | 6,000 |

Test ROC-AUC was 0.7722, trapezoidal PR-AUC was 0.5516, and AP was 0.5520. The observed default rate was 22.12%. At the selected cutoff, 51.00% of customers were flagged. Test cost was 3,437 units under the same assumption.

## Calibration and feature importance

In the highest-risk test group, the mean predicted risk was 68.16% and the observed default rate was 69.33%. The model underestimated risk in that group by 1.17 percentage points. [Calibration chart](figures/calibration.png)

On validation, shuffling September repayment status (`PAY_0`) produced the largest mean AP drop across five shuffles (0.1739), followed by August repayment status (`PAY_2`, 0.0257). Both derived delay features were recalculated after each shuffle. These drops measure how the fitted model used those inputs. [Permutation importance chart](figures/permutation_importance.png)

## Group audit

All 6,000 test predictions matched demographic records by customer ID. The model excluded sex, marital status, and age from its inputs. Each section below groups the same 6,000 predictions. The false-alarm denominator is the number of actual non-defaulters. The missed-default denominator is the number of actual defaulters.

| Group | Customers | Flag rate | False alarms / non-defaulters | Misses / defaulters |
|---|---:|---:|---:|---:|
| Sex: male | 2,402 | 52.12% | 808/1,841 (43.89%) | 117/561 (20.86%) |
| Sex: female | 3,598 | 50.25% | 1,209/2,832 (42.69%) | 167/766 (21.80%) |
| Marital status: undocumented code 0 | 7 | 57.14% | 4/7 (57.14%) | Undefined (0 defaulters) |
| Marital status: married | 2,767 | 50.63% | 881/2,099 (41.97%) | 148/668 (22.16%) |
| Marital status: single | 3,158 | 51.20% | 1,104/2,511 (43.97%) | 134/647 (20.71%) |
| Marital status: other | 68 | 55.88% | 28/56 (50.00%) | 2/12 (16.67%) |
| Age: under 30 | 1,912 | 54.24% | 691/1,485 (46.53%) | 81/427 (18.97%) |
| Age: 30–39 | 2,198 | 47.95% | 702/1,745 (40.23%) | 101/453 (22.30%) |
| Age: 40–49 | 1,341 | 50.11% | 435/1,029 (42.27%) | 75/312 (24.04%) |
| Age: 50–59 | 473 | 53.49% | 162/361 (44.88%) | 21/112 (18.75%) |
| Age: 60+ | 76 | 57.89% | 27/53 (50.94%) | 6/23 (26.09%) |

## Limitations

The results describe one historical Taiwan cohort. The 5:1 cost ratio is an assumption, and a different cost ratio could favor a different cutoff. Group rates are descriptive. Several estimates have small denominators, including 12 defaults in the “other” marital-status group and 23 in the 60+ age band.