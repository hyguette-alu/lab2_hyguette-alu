"""
Student Grade Evaluator
African Leadership University - Introduction to Python Programming and Databases
Lab 2 - BSE Year 1, Trimester 2

Reads a CSV file of course grades, validates it, calculates the final grade and
GPA, decides whether the student passed, and lists the assignment(s) that are
eligible for resubmission.

Uses only the Python standard library (csv, sys, os) - no external libraries.
"""

import csv
import sys
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = ["assignment", "group", "score", "weight"]

# Accepted categories. The key is the lowercase form used for matching, the
# value is the tidy form used when printing.
VALID_GROUPS = {"formative": "Formative", "summative": "Summative"}

MIN_SCORE = 0.0
MAX_SCORE = 100.0

EXPECTED_TOTAL_WEIGHT = 100.0
EXPECTED_FORMATIVE_WEIGHT = 60.0
EXPECTED_SUMMATIVE_WEIGHT = 40.0

PASS_MARK = 50.0   # minimum percentage required in EACH category
GPA_SCALE = 5.0    # GPA = (total grade / 100) * 5.0

# Small tolerance so that float arithmetic such as 59.999999999 is still
# treated as 60 when comparing weight totals.
TOLERANCE = 0.000001


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def stop_with_error(message, hint=None):
    """Print a clear error message, optionally with a hint, and exit."""
    print("\n" + "=" * 62)
    print("ERROR: " + message)
    if hint:
        print("HINT : " + hint)
    print("=" * 62)
    sys.exit(1)


def clean(value):
    """Turn a raw CSV value into a trimmed string, treating None as empty."""
    if value is None:
        return ""
    return str(value).strip()


def is_close(value, target):
    """Compare two floats allowing for tiny rounding differences."""
    return abs(value - target) < TOLERANCE


# ---------------------------------------------------------------------------
# Step 1 - Loading the data
# ---------------------------------------------------------------------------

def load_csv_data():
    """
    Prompts the user for a filename, checks if it exists,
    and extracts all fields into a list of dictionaries.
    """
    try:
        filename = input(
            "Enter the name of the CSV file to process (e.g., grades.csv): "
        ).strip()
    except EOFError:
        stop_with_error(
            "No input was received, so there is no file to process.",
            "Run the program in a terminal and type a filename when asked, "
            "for example: grades.csv",
        )
    except KeyboardInterrupt:
        print("\nCancelled by the user. No grades were processed.")
        sys.exit(1)

    if filename == "":
        stop_with_error(
            "No filename was entered.",
            "Type the name of the file, for example: grades.csv",
        )

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        print(f"HINT : Check the spelling. Files available here: "
              f"{', '.join(list_csv_files())}")
        sys.exit(1)

    if os.path.isdir(filename):
        stop_with_error(
            f"'{filename}' is a folder, not a CSV file.",
            "Pass the name of a .csv file, for example: grades.csv",
        )

    if os.path.getsize(filename) == 0:
        stop_with_error(
            f"The file '{filename}' is empty (0 bytes).",
            "The file needs a header row plus at least one assignment row, "
            "e.g. 'assignment,group,score,weight'.",
        )

    assignments = []
    skipped_blank_rows = 0

    try:
        with open(filename, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            # a) Make sure there is a header at all.
            if reader.fieldnames is None:
                stop_with_error(
                    f"The file '{filename}' has no header row.",
                    "The first line must be: assignment,group,score,weight",
                )

            # b) Normalise the header so that ' Score ' and 'score' both work.
            header = [clean(name).lower() for name in reader.fieldnames]
            reader.fieldnames = header

            # c) Make sure every column we need is present.
            missing = []
            for column in REQUIRED_COLUMNS:
                if column not in header:
                    missing.append(column)
            if missing:
                stop_with_error(
                    f"The file '{filename}' is missing the column(s): "
                    f"{', '.join(missing)}.",
                    "The header row must be: assignment,group,score,weight",
                )

            # d) Read the rows. Line numbers start at 2 because line 1 is the
            #    header - this makes error messages easy to act on.
            line_number = 1
            for row in reader:
                line_number += 1

                # Skip completely blank lines instead of crashing on them.
                if is_blank_row(row):
                    skipped_blank_rows += 1
                    continue

                assignments.append(build_record(row, line_number, filename))

    except UnicodeDecodeError:
        stop_with_error(
            f"The file '{filename}' is not readable as text.",
            "Make sure it is a plain CSV file, not a spreadsheet (.xlsx).",
        )
    except PermissionError:
        stop_with_error(
            f"Permission denied when opening '{filename}'.",
            "Check the file permissions, e.g. run: chmod +r " + filename,
        )
    except OSError as error:
        stop_with_error(f"An error occurred while reading the file: {error}")

    if skipped_blank_rows > 0:
        print(f"Note: skipped {skipped_blank_rows} blank row(s) in "
              f"'{filename}'.")

    if len(assignments) == 0:
        stop_with_error(
            f"No assignment records were found in '{filename}'.",
            "The file has a header but no data rows. Add at least one row, "
            "e.g. 'Quiz,Formative,85,20'.",
        )

    print(f"Loaded {len(assignments)} assignment record(s) from '{filename}'.")
    return assignments


def list_csv_files():
    """Return the CSV files in the current folder, to help a mistyped name."""
    found = []
    for name in os.listdir("."):
        if name.lower().endswith(".csv"):
            found.append(name)
    if len(found) == 0:
        return ["(no .csv files in this folder)"]
    return found


def is_blank_row(row):
    """True when every value in the row is empty or missing."""
    for value in row.values():
        # A row with extra columns stores them in a list under the key None.
        if isinstance(value, list):
            for extra in value:
                if clean(extra) != "":
                    return False
        elif clean(value) != "":
            return False
    return True


def build_record(row, line_number, filename):
    """
    Turn one raw CSV row into a validated dictionary with the correct data
    types. Any problem stops the program with a message naming the line.
    """
    assignment = clean(row.get("assignment"))
    group = clean(row.get("group"))
    raw_score = clean(row.get("score"))
    raw_weight = clean(row.get("weight"))

    where = f"line {line_number} of '{filename}'"

    # Every field must actually contain something.
    if assignment == "":
        stop_with_error(
            f"Missing assignment name on {where}.",
            "Every row needs all four values, e.g. 'Quiz,Formative,85,20'.",
        )
    if group == "":
        stop_with_error(
            f"Missing group for '{assignment}' on {where}.",
            "The group must be either Formative or Summative.",
        )
    if raw_score == "":
        stop_with_error(
            f"Missing score for '{assignment}' on {where}.",
            "The score must be a number from 0 to 100, e.g. 85.",
        )
    if raw_weight == "":
        stop_with_error(
            f"Missing weight for '{assignment}' on {where}.",
            "The weight must be a number, e.g. 20.",
        )

    # The group must be one we recognise.
    if group.lower() not in VALID_GROUPS:
        stop_with_error(
            f"Unknown group '{group}' for '{assignment}' on {where}.",
            "The group must be either Formative or Summative.",
        )

    # Convert the text from the CSV into numbers before any arithmetic.
    try:
        score = float(raw_score)
    except ValueError:
        stop_with_error(
            f"The score '{raw_score}' for '{assignment}' on {where} is not a "
            f"number.",
            "Scores are written as plain numbers from 0 to 100, e.g. 85 or "
            "72.5 (no '%' sign and no text).",
        )

    try:
        weight = float(raw_weight)
    except ValueError:
        stop_with_error(
            f"The weight '{raw_weight}' for '{assignment}' on {where} is not "
            f"a number.",
            "Weights are written as plain numbers, e.g. 20.",
        )

    return {
        "assignment": assignment,
        "group": VALID_GROUPS[group.lower()],
        "score": score,
        "weight": weight,
    }


# ---------------------------------------------------------------------------
# Step 2 - Validation
# ---------------------------------------------------------------------------

def validate_scores(data):
    """a) Check that every score is a percentage between 0 and 100."""
    print(f"\n[1/2] Checking that all scores are between "
          f"{int(MIN_SCORE)} and {int(MAX_SCORE)}...")

    offenders = []
    for record in data:
        if record["score"] < MIN_SCORE or record["score"] > MAX_SCORE:
            offenders.append(record)

    if offenders:
        print(f"      {len(offenders)} invalid score(s) found:")
        for record in offenders:
            print(f"        - {record['assignment']}: {record['score']:g} "
                  f"is outside {int(MIN_SCORE)}-{int(MAX_SCORE)}")
        stop_with_error(
            "One or more scores are not valid percentages.",
            "Fix the score(s) listed above so that each one is between "
            "0 and 100, then run the program again.",
        )

    print(f"      OK - all {len(data)} score(s) are valid percentages.")


def validate_weights(data):
    """
    b) Verify that the weights add up correctly:
       total = 100, Formative = 60, Summative = 40.
    Returns the three sums so they can be reused.
    """
    print("\n[2/2] Checking the assignment weights...")

    total_weight = 0.0
    formative_weight = 0.0
    summative_weight = 0.0

    for record in data:
        weight = record["weight"]

        # A negative weight would silently corrupt every later calculation.
        if weight < 0:
            stop_with_error(
                f"The weight for '{record['assignment']}' is negative "
                f"({weight:g}).",
                "Weights must be zero or greater, e.g. 20.",
            )

        total_weight += weight
        if record["group"] == "Formative":
            formative_weight += weight
        else:
            summative_weight += weight

    print(f"      Total weight     : {total_weight:g} "
          f"(expected {EXPECTED_TOTAL_WEIGHT:g})")
    print(f"      Formative weight : {formative_weight:g} "
          f"(expected {EXPECTED_FORMATIVE_WEIGHT:g})")
    print(f"      Summative weight : {summative_weight:g} "
          f"(expected {EXPECTED_SUMMATIVE_WEIGHT:g})")

    problems = []
    if not is_close(total_weight, EXPECTED_TOTAL_WEIGHT):
        problems.append(
            f"all weights must add up to exactly "
            f"{EXPECTED_TOTAL_WEIGHT:g} but they add up to {total_weight:g} "
            f"(off by {total_weight - EXPECTED_TOTAL_WEIGHT:+g})"
        )
    if not is_close(formative_weight, EXPECTED_FORMATIVE_WEIGHT):
        problems.append(
            f"Formative weights must add up to exactly "
            f"{EXPECTED_FORMATIVE_WEIGHT:g} but they add up to "
            f"{formative_weight:g} "
            f"(off by {formative_weight - EXPECTED_FORMATIVE_WEIGHT:+g})"
        )
    if not is_close(summative_weight, EXPECTED_SUMMATIVE_WEIGHT):
        problems.append(
            f"Summative weights must add up to exactly "
            f"{EXPECTED_SUMMATIVE_WEIGHT:g} but they add up to "
            f"{summative_weight:g} "
            f"(off by {summative_weight - EXPECTED_SUMMATIVE_WEIGHT:+g})"
        )

    if problems:
        print(f"      {len(problems)} weight problem(s) found:")
        for problem in problems:
            print(f"        - {problem}")
        stop_with_error(
            "The assignment weights are not valid.",
            "Adjust the 'weight' column in the CSV so that the Formative "
            "rows total 60, the Summative rows total 40, and all rows "
            "together total 100.",
        )

    print("      OK - the weights are correctly distributed 60/40.")
    return total_weight, formative_weight, summative_weight


# ---------------------------------------------------------------------------
# Step 3 - Calculations
# ---------------------------------------------------------------------------

def category_points(data, group):
    """
    Add up the weighted points earned in one category.
    An assignment scoring 85 with a weight of 20 contributes 17 points.
    """
    points = 0.0
    for record in data:
        if record["group"] == group:
            points += record["score"] * record["weight"] / 100.0
    return points


def percentage_of(points, category_max):
    """Convert points earned into a percentage of that category's maximum."""
    if category_max <= 0:
        return 0.0
    return points / category_max * 100.0


def find_resubmissions(data):
    """
    e) Resubmission is for the failed formative assignment carrying the
    highest weight. Ties are all returned, so every eligible assignment is
    shown to the student.
    """
    failed = []
    for record in data:
        if record["group"] == "Formative" and record["score"] < PASS_MARK:
            failed.append(record)

    if len(failed) == 0:
        return []

    # Find the highest weight among the failed formative assignments.
    highest_weight = failed[0]["weight"]
    for record in failed:
        if record["weight"] > highest_weight:
            highest_weight = record["weight"]

    # Collect every failed assignment sharing that highest weight.
    eligible = []
    for record in failed:
        if is_close(record["weight"], highest_weight):
            eligible.append(record)

    return eligible


# ---------------------------------------------------------------------------
# Step 4 - Reporting
# ---------------------------------------------------------------------------

def print_transcript(data):
    """Print each assignment with the points it contributed."""
    name_width = len("Assignment")
    for record in data:
        if len(record["assignment"]) > name_width:
            name_width = len(record["assignment"])

    print("\n" + "=" * 62)
    print("TRANSCRIPT")
    print("=" * 62)
    header = (f"{'Assignment':<{name_width}}  {'Group':<10}"
              f"{'Score':>7}{'Weight':>8}{'Earned':>9}")
    print(header)
    print("-" * len(header))

    for record in data:
        earned = record["score"] * record["weight"] / 100.0
        print(f"{record['assignment']:<{name_width}}  "
              f"{record['group']:<10}"
              f"{record['score']:>7.2f}"
              f"{record['weight']:>8.2f}"
              f"{earned:>9.2f}")


def evaluate_grades(data):
    """
    Validate the records, calculate the grade and GPA, decide pass or fail,
    and report any assignments eligible for resubmission.
    """
    print("\n--- Processing Grades ---")

    # a) and b) - nothing is calculated until the data is known to be sound.
    validate_scores(data)
    validate_weights(data)

    # c) Weighted scores per category and overall.
    formative_points = category_points(data, "Formative")
    summative_points = category_points(data, "Summative")
    total_grade = formative_points + summative_points

    formative_percentage = percentage_of(
        formative_points, EXPECTED_FORMATIVE_WEIGHT)
    summative_percentage = percentage_of(
        summative_points, EXPECTED_SUMMATIVE_WEIGHT)

    # GPA = (Total Grade / 100) * 5.0
    gpa = total_grade / 100.0 * GPA_SCALE

    print_transcript(data)

    print("\n" + "=" * 62)
    print("RESULTS")
    print("=" * 62)
    print(f"Formative : {formative_points:6.2f} / "
          f"{EXPECTED_FORMATIVE_WEIGHT:g}  "
          f"({formative_percentage:.2f}% of the category)")
    print(f"Summative : {summative_points:6.2f} / "
          f"{EXPECTED_SUMMATIVE_WEIGHT:g}  "
          f"({summative_percentage:.2f}% of the category)")
    print("-" * 62)
    print(f"Total Grade : {total_grade:.2f} / {EXPECTED_TOTAL_WEIGHT:g}")
    print(f"GPA         : {gpa:.2f} / {GPA_SCALE:.1f}   "
          f"[({total_grade:.2f} / 100) x {GPA_SCALE:.1f}]")

    # d) A student passes only when BOTH categories reach the pass mark.
    passed_formative = formative_percentage >= PASS_MARK
    passed_summative = summative_percentage >= PASS_MARK
    passed = passed_formative and passed_summative

    print("\nCategory check (at least "
          f"{PASS_MARK:g}% is required in each):")
    print(f"  Formative {formative_percentage:6.2f}%  ->  "
          f"{'PASS' if passed_formative else 'FAIL'}")
    print(f"  Summative {summative_percentage:6.2f}%  ->  "
          f"{'PASS' if passed_summative else 'FAIL'}")

    # f) The final decision.
    print("\n" + "=" * 62)
    if passed:
        print("FINAL STATUS: PASSED")
    else:
        print("FINAL STATUS: FAILED")
    print("=" * 62)

    if not passed:
        reasons = []
        if not passed_formative:
            reasons.append(f"Formative is below {PASS_MARK:g}% "
                           f"({formative_percentage:.2f}%)")
        if not passed_summative:
            reasons.append(f"Summative is below {PASS_MARK:g}% "
                           f"({summative_percentage:.2f}%)")
        print("Reason: " + "; ".join(reasons) + ".")

    # e) Resubmission options.
    print("\n--- Resubmission ---")
    eligible = find_resubmissions(data)

    if len(eligible) == 0:
        print("No formative assignment was failed, so there is nothing to "
              "resubmit.")
    else:
        if len(eligible) == 1:
            print("Eligible for resubmission (failed formative assignment "
                  "with the highest weight):")
        else:
            print(f"{len(eligible)} assignments tie on the highest weight, "
                  f"so all of them are eligible for resubmission:")
        for record in eligible:
            print(f"  - {record['assignment']} "
                  f"(score {record['score']:g}, weight "
                  f"{record['weight']:g})")

    print()


if __name__ == "__main__":
    # 1. Load the data
    course_data = load_csv_data()

    # 2. Process the features
    evaluate_grades(course_data)
