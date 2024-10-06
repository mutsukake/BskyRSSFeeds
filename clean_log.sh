# Delete old logs and keep the latest 10 logs

# Read inside the logs directory and sort the files by date
LOG_DIR=$(dirname "$(realpath "$0")")/logs

CUTOFF_DATE=$(date -v-7d +%s)

# Delete logs older than 10 days
find "$LOG_DIR" -type f -name "*.log" -mtime +7 -exec rm {} \;

