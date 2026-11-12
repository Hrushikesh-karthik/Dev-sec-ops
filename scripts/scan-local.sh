#!/usr/bin/env bash
set -euo pipefail
echo "1/3 Secret scan (requires gitleaks)"
gitleaks detect --source . --no-git --verbose || true
echo "2/3 SAST (requires semgrep)"
semgrep scan --config .semgrep.yml . || true
echo "3/3 Filesystem scan (requires trivy)"
trivy fs --scanners vuln,secret,misconfig .
echo "Local demo scans completed. Review findings; this script does not certify the app as secure."
