# Lab 2 — Student Grade Evaluator & Archive Organizer

**African Leadership University** — Introduction to Python Programming and Databases
BSE Year 1, Trimester 2 — Individual Coding Lab

Author: hyguette-alu

---

## What this project does

This lab has two parts that work together:

1. **`grade-evaluator.py`** — a Python application that reads a CSV of course grades,
   validates the data, calculates the final grade and GPA, decides whether the student
   passed or failed, and identifies which assignment(s) are eligible for resubmission.
2. **`organizer.sh`** — a Bash script that archives the processed `grades.csv` with a
   timestamp, resets the workspace with a fresh empty `grades.csv`, and keeps a running
   log of every archiving operation in `organizer.log`.

No external libraries are used. The Python script relies only on the standard library
(`csv`, `sys`, `os`), and the shell script uses only standard Unix utilities.

---

## Repository files

| File | Purpose |
| --- | --- |
| `grades.csv` | Source data: one row per assignment (name, group, score, weight) |
| `grade-evaluator.py` | The Python grading application |
| `organizer.sh` | The Bash archiving/organizer script |
| `organizer.log` | Generated log of archive runs (created by `organizer.sh`) |
| `archive/` | Generated directory holding timestamped copies of `grades.csv` |
| `README.md` | This file |

---

## The data format

`grades.csv` uses four columns with a header row:

```csv
assignment,group,score,weight
Quiz,Formative,85,20
Group Exercise,Formative,40,20
Functions and Debugging Lab,Formative,45,20
Midterm Project - Simple Calculator,Summative,70,20
Final Project - Text-Based Game,Summative,60,20
```

- `assignment` — the name of the assignment (text)
- `group` — either `Formative` or `Summative`
- `score` — the percentage scored on that assignment, 0–100
- `weight` — how much of the final grade this assignment is worth

---

## Grading rules implemented

### 1. Grade validation
Every `score` must be a number between 0 and 100 inclusive. Any score outside that
range is reported with the assignment name and the offending value.

### 2. Weight validation
Three checks must all pass:

- the sum of **all** weights is exactly **100**
- the sum of **Formative** weights is exactly **60**
- the sum of **Summative** weights is exactly **40**

### 3. Weighted score and GPA
Each assignment contributes `score × weight ÷ 100` points.

```
Total Grade = sum of all weighted contributions
GPA         = (Total Grade / 100) × 5.0
```

The maximum achievable total is 100, so the GPA scale runs from 0.0 to 5.0.

### 4. Pass / Fail decision
The student **passes only if they score at or above 50% in both categories**,
measured inside each category:

```
Formative % = (formative points earned / 60) × 100
Summative % = (summative points earned / 40) × 100
```

Passing the overall total is not enough — a student who is strong in one category
and below 50% in the other **fails**.

### 5. Resubmission logic
Resubmission applies to **failed formative assignments** (score below 50%). Among
those, the one carrying the **highest weight** is eligible. If several failed
formative assignments share that same highest weight, **all of them** are listed.

---

## Error handling and validation

The program is written to explain what went wrong instead of crashing:

- missing CSV file — reports the filename it could not find
- empty file or a file with only a header — reports that there are no records
- missing or misspelled columns — names the required header
- blank rows — skipped and counted
- non-numeric `score` or `weight` — reports the row and the bad value
- unknown category in `group` — reports the allowed values
- scores outside 0–100 — each offender is listed
- weights that do not sum to 100 / 60 / 40 — reports the expected vs actual sums

Scores and weights are read as text from the CSV and explicitly converted with
`float()` before any arithmetic or comparison.

---

## How to run

### Python application

```bash
python3 grade-evaluator.py
```

The program asks for the filename to process; the expected input is shown in the
prompt:

```
Enter the name of the CSV file to process (e.g., grades.csv): grades.csv
```

### Shell organizer

```bash
chmod +x organizer.sh
./organizer.sh
```

What it does, in order:

1. creates the `archive/` directory if it does not already exist
2. generates a timestamp in `YYYYMMDD-HHMMSS` format
3. moves `grades.csv` into `archive/` renamed as `grades_<timestamp>.csv`
4. creates a new empty `grades.csv` in the current directory
5. appends a line to `organizer.log` recording the timestamp, the original
   filename, and the new archived filename

`organizer.log` is never overwritten — entries accumulate across every run.

---

## Testing

The results are cross-checked by hand against the sample `grades.csv` above:

| Category | Weighted points | Category max | Percentage |
| --- | --- | --- | --- |
| Formative | 34.0 | 60 | 56.67% |
| Summative | 26.0 | 40 | 65.00% |
| **Total** | **60.0** | **100** | — |

- Total Grade = 60.0
- GPA = (60.0 / 100) × 5.0 = **3.0**
- Both categories are at or above 50% → **PASSED**
- Failed formative assignments: *Group Exercise* (40, weight 20) and
  *Functions and Debugging Lab* (45, weight 20) — tied on the highest weight,
  so **both** are listed for resubmission

Edge cases are also tested with deliberately broken copies of the CSV: an empty
file, a score of 105, weights summing to 90, a 50/50 category split, and a
non-numeric score. Each produces a clear message and a clean exit instead of a
traceback.

---

## Build steps

The work is committed in stages so the history shows how the solution was built:

1. `README.md` — project plan and documentation
2. `grades.csv` — source data verified against the expected transcript
3. `grade-evaluator.py` — validation, GPA, pass/fail, resubmission logic
4. `organizer.sh` — archiving, workspace reset, logging
5. Testing pass — edge cases and final README updates
