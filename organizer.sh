#!/usr/bin/env bash
#
# organizer.sh
# African Leadership University - Introduction to Python Programming and Databases
# Lab 2 - BSE Year 1, Trimester 2

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SOURCE_FILE="grades.csv"
ARCHIVE_DIR="archive"
LOG_FILE="organizer.log"

TIMESTAMP="$(date +"%Y%m%d-%H%M%S")"

LOG_TIME="$(date +"%Y-%m-%d %H:%M:%S")"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

abort() {
    echo "" >&2
    echo "ERROR: $1" >&2
    if [ -n "${2:-}" ]; then
        echo "HINT : $2" >&2
    fi
    exit 1
}

echo "=============================================================="
echo " Grade Data Organizer"
echo "=============================================================="
echo "Run time : $LOG_TIME"
echo "Working in: $(pwd)"
echo ""

# ---------------------------------------------------------------------------
# Step 1 - Make sure there is something to archive
# ---------------------------------------------------------------------------

if [ ! -e "$SOURCE_FILE" ]; then
    abort "'$SOURCE_FILE' was not found in $(pwd), so there is nothing to archive." \
          "Add the grade data to a file named '$SOURCE_FILE' and run this script again."
fi

if [ -d "$SOURCE_FILE" ]; then
    abort "'$SOURCE_FILE' is a directory, not a CSV file." \
          "Remove or rename that directory so '$SOURCE_FILE' can be a normal file."
fi

if [ ! -r "$SOURCE_FILE" ]; then
    abort "'$SOURCE_FILE' exists but cannot be read (permission denied)." \
          "Make it readable with: chmod +r $SOURCE_FILE"
fi

if [ -s "$SOURCE_FILE" ]; then
    TOTAL_LINES="$(wc -l < "$SOURCE_FILE" | tr -d ' ')"
    # A file whose last line has no trailing newline still holds that line.
    if [ -n "$(tail -c 1 "$SOURCE_FILE")" ]; then
        TOTAL_LINES="$((TOTAL_LINES + 1))"
    fi
    if [ "$TOTAL_LINES" -gt 0 ]; then
        DATA_ROWS="$((TOTAL_LINES - 1))"
    else
        DATA_ROWS=0
    fi
else
    echo "Note: '$SOURCE_FILE' is empty, but it will still be archived."
    DATA_ROWS=0
fi

echo "Found '$SOURCE_FILE' holding $DATA_ROWS assignment row(s)."

# ---------------------------------------------------------------------------
# Step 2 - Archive directory: create it only if it does not exist
# ---------------------------------------------------------------------------

if [ -d "$ARCHIVE_DIR" ]; then
    echo "Archive directory '$ARCHIVE_DIR/' already exists - reusing it."
else
    if [ -e "$ARCHIVE_DIR" ]; then
        abort "'$ARCHIVE_DIR' already exists but is a file, not a directory." \
              "Rename or remove that file so the archive directory can be created."
    fi
    mkdir "$ARCHIVE_DIR"
    echo "Archive directory '$ARCHIVE_DIR/' did not exist - created it."
fi

# ---------------------------------------------------------------------------
# Step 3 - Move grades.csv into the archive with the timestamp appended
# ---------------------------------------------------------------------------

ARCHIVED_NAME="grades_${TIMESTAMP}.csv"
ARCHIVED_PATH="${ARCHIVE_DIR}/${ARCHIVED_NAME}"

COPY_NUMBER=1
while [ -e "$ARCHIVED_PATH" ]; do
    COPY_NUMBER="$((COPY_NUMBER + 1))"
    ARCHIVED_NAME="grades_${TIMESTAMP}_${COPY_NUMBER}.csv"
    ARCHIVED_PATH="${ARCHIVE_DIR}/${ARCHIVED_NAME}"
done

if ! mv "$SOURCE_FILE" "$ARCHIVED_PATH"; then
    abort "Could not move '$SOURCE_FILE' to '$ARCHIVED_PATH'." \
          "Check that you have write permission in $(pwd) and in '$ARCHIVE_DIR/'."
fi

echo "Archived : $SOURCE_FILE  ->  $ARCHIVED_PATH"

# ---------------------------------------------------------------------------
# Step 4 - Workspace reset: a new empty grades.csv for the next batch
# ---------------------------------------------------------------------------

if ! touch "$SOURCE_FILE"; then
    abort "Archived the old file but could not create a new '$SOURCE_FILE'." \
          "Check that you have write permission in $(pwd)."
fi

echo "Workspace: created a new empty '$SOURCE_FILE'."

# ---------------------------------------------------------------------------
# Step 5 - Logging: append this run to organizer.log
# ---------------------------------------------------------------------------

if [ ! -e "$LOG_FILE" ]; then
    {
        echo "# organizer.log - archive history for grades.csv"
        echo "# Created on $LOG_TIME by organizer.sh"
        echo "# Format: [date time] timestamp=... | original=... | archived=... | rows=..."
    } >> "$LOG_FILE"
    echo "Log      : '$LOG_FILE' did not exist - created it."
fi

echo "[$LOG_TIME] timestamp=$TIMESTAMP | original=$SOURCE_FILE | archived=$ARCHIVED_PATH | rows=$DATA_ROWS" >> "$LOG_FILE"

ENTRY_COUNT="$(grep -c '^\[' "$LOG_FILE" || true)"
echo "Log      : appended this run to '$LOG_FILE' - $ENTRY_COUNT entries on record."

echo ""
echo "=============================================================="
echo " Done. The workspace is ready for the next batch of grades."
echo "=============================================================="
