# Credit Card Default Risk | Project Notes

## Current stage

Stage 1 (environment setup) is complete. Resume at Stage 2 (data inspection).

## What I completed

- Cloned the GitHub repository into `C:\Projects\credit-card-default-risk` and opened it in VS Code.
- Created a project-local `.venv` with Python 3.11.9 and selected it as the VS Code interpreter.
- Installed six project dependencies, verified that all six imported successfully, and pinned their versions in `requirements.txt`.
- Ran `python -m pip check` inside the project environment and got `No broken requirements found.`

## Decisions and why

- I use PowerShell for commands and VS Code for editing files.
- I added `/.venv/` to `.gitignore` because each developer can create their own environment locally.
- I pinned the six packages the project uses directly. This records the versions I tested while allowing pip to resolve their dependencies.

## What I learned

- I verified which Python VS Code ran by printing `sys.executable`. It returned `C:\Projects\credit-card-default-risk\.venv\Scripts\python.exe`. The path identified my project environment even though both interpreters showed Python 3.11.9.
- In `git status --short --ignored`, `!! .venv/` confirmed that Git was ignoring my virtual environment.
- `pip check` verified that installed packages satisfied their declared dependency requirements. Importing each package separately confirmed that Python could load it.

## Open items

- Finish the Stage 1 interview questions.
- Start Stage 2 by downloading the original UCI workbook into `data/raw/` and adding that folder to `.gitignore`.
- Inspect the workbook headers, identify the next-month default column, and verify the row count before calculating the default rate.
## Stage 2: Data inspection

- Loaded the original UCI workbook with `load_clients()` in `src/credit_risk/data.py`. Used `header=1` because the second Excel row contains descriptive column names.
- Verified 30,000 rows, 25 columns, 30,000 distinct customer IDs, and zero missing cells.
- Counted 6,636 next-month defaults and 23,364 non-defaults. The observed default rate was 22.12%.
- Found repayment codes `-2` and `0` in the workbook. UCI's published codebook leaves their meanings unspecified. Preserve them as distinct values.
- Kept the original workbook local under `data/raw/` and verified the Git ignore rule.
- Open item: pandas warned that support for the xlrd engine will be removed in a future version. The loader works with the pinned environment.