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

---

## Build steps

The work is committed in stages so the history shows how the solution was built:

1. `README.md` — project plan and documentation
2. `grades.csv` — source data verified against the expected transcript
3. `grade-evaluator.py` — validation, GPA, pass/fail, resubmission logic
4. `organizer.sh` — archiving, workspace reset, logging
5. Testing pass — edge cases and final README updates
