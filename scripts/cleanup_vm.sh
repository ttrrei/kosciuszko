#!/usr/bin/env bash
set -euo pipefail

# Stop browser processes that may survive failed scraping runs on Ironbark.
pkill -f chromedriver || true
pkill -f chromium || true
pkill -f chrome || true

# Keep raw snapshot samples bounded on small OCI VM disks.
find data/samples/ -type f -mtime +7 -delete
