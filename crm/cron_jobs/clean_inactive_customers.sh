#!/bin/bash

# Navigate to the project directory
PROJECT_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
cd "$PROJECT_DIR" || exit 1

# File for logging number of deleted customers
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Python command that deletes customers with no orders since a year ago
DELETED_COUNT=$(python manage.py shell -c "
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

cut_off = timezone.now() - timedelta(days=365)

qs = (
    Customer.objects
    .filter(orders__isnull=True, created_at__lt=cut_off)
    .distinct()
)

count = qs.count()
qs.delete()
print(count)
")

# Log the DELETED_COUNT to the log file
printf '%s - Deleted customers: %s\n' \
  "$(date '+%Y-%m-%d %H:%M:%S')" \
  "$DELETED_COUNT" >> "$LOG_FILE"
