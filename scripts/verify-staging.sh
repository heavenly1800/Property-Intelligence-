#!/usr/bin/env sh
set -eu

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 FRONTEND_URL BACKEND_URL [enabled|disabled|skip]" >&2
  exit 2
fi

frontend=${1%/}
backend=${2%/}
docs=${3:-skip}
failures=0

check() {
  name=$1
  url=$2
  expected=$3
  status=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 20 "$url" || printf '000')
  if [ "$status" = "$expected" ]; then
    printf 'PASS: %s returned HTTP %s\n' "$name" "$status"
  else
    printf 'FAIL: %s returned HTTP %s; expected %s\n' "$name" "$status" "$expected" >&2
    failures=$((failures + 1))
  fi
}

check "Frontend" "$frontend" 200
check "Liveness" "$backend/health/live" 200
check "Readiness" "$backend/health/ready" 200
check "Version" "$backend/health/version" 200
check "Unauthenticated protected API" "$backend/properties" 401
[ "$docs" != "enabled" ] || check "API docs" "$backend/docs" 200
[ "$docs" != "disabled" ] || check "API docs" "$backend/docs" 404

[ "$failures" -eq 0 ] || exit 1
echo "Staging endpoint verification passed."
