# Lab 2 — Student Grade Evaluator & Data Organizer

African Leadership University — Introduction to Python Programming and Databases
BSE Year 1, Trimester 2 · Individual Coding Lab

Repository: `lab2_hyguette-alu`

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

> **Note:** `organizer.sh` is deliberately *not* run inside this repository before
> submission, because step 4 replaces `grades.csv` with an empty file and the lab
> requires the populated `grades.csv` to be present. `archive/` and `organizer.log`
> are therefore generated artifacts that appear the first time you run the script.

---

## The grading rules implemented

| Rule | Implementation |
| --- | --- |
| Grade validation | Every score must be between 0 and 100 |
| Weight validation | All weights total exactly 100; Formative total exactly 60; Summative total exactly 40 |
| GPA | `GPA = (Total Grade / 100) × 5.0`, on a 5.0 scale |
| Pass/Fail | PASSED only when the student reaches **≥ 50% in both** categories (not on the overall average) |
| Resubmission | The *failed* (< 50%) formative assignment with the **highest weight**; all assignments tied on that weight are listed |

---

## Testing — cross-check against the expected transcript

Running the program on the committed `grades.csv` produces:

| Assignment | Group | Score | Weight | Earned |
| --- | --- | --- | --- | --- |
| Quiz | Formative | 85 | 20 | 17.00 |
| Group Exercise | Formative | 40 | 20 | 8.00 |
| Functions and Debugging Lab | Formative | 45 | 20 | 9.00 |
| Midterm Project - Simple Calculator | Summative | 70 | 20 | 14.00 |
| Final Project - Text-Based Game | Summative | 60 | 20 | 12.00 |

- Formative: **34.00 / 60 → 56.67%** → PASS
- Summative: **26.00 / 40 → 65.00%** → PASS
- Total Grade: **60.00 / 100**
- GPA: **(60.00 / 100) × 5.0 = 3.00**
- Final status: **PASSED**
- Eligible for resubmission (tie on the highest weight, 20): **Group Exercise** (40) and
  **Functions and Debugging Lab** (45)

These figures match the transcript structure provided with the assignment.

### Edge cases verified

Each of the following was tested and produces a clear, named error instead of a crash:

| Scenario | Result |
| --- | --- |
| File does not exist | Error naming the file, plus a list of the `.csv` files in the folder |
| Empty file (0 bytes) | Error explaining a header plus one data row is needed |
| Header present but no data rows | Error asking for at least one assignment row |
| Missing or misnamed columns | Error naming exactly which column(s) are absent |
| Blank rows inside the file | Skipped, counted, and reported as a note |
| Non-numeric score or weight (`abc`, `80%`) | Error naming the value, the assignment and the line number |
| Empty field in a row | Error naming the field, the assignment and the line number |
| Score outside 0–100 | Every offending score listed before the program stops |
| Weights not 100 / 60 / 40 | Each wrong total listed with how far off it is |
| Unknown group (e.g. `Peer`) | Error stating the group must be Formative or Summative |
| Mixed-case / padded headers and groups | Accepted (`SCORE`, ` Group `, `formative` all work) |
| CSV saved from Excel (byte-order mark) | Accepted — the BOM is stripped on read |
| `grades.csv` missing when archiving | `organizer.sh` stops with an error and changes nothing |
| `archive/` already exists | Reused rather than recreated |
| Two runs in the same second | A counter is appended so no archive is overwritten |

---

## Build steps

The work is committed in stages so the history shows how the solution was built:

1. `README.md` — project plan and documentation
2. `grades.csv` — source data verified against the expected transcript
3. `grade-evaluator.py` — validation, GPA, pass/fail, resubmission logic
4. `organizer.sh` — archiving, workspace reset, logging
5. Testing pass — edge cases verified and documented above
