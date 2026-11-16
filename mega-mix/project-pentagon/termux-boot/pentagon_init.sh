#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${PENTAGON_HOME:-$HOME/projects/grep-language/mega-mix/project-pentagon}"
RUNTIME="$ROOT/runtime"
JAVA_BIN="${JAVA:-java}"
JAR="$ROOT/dist/project-pentagon/pentagon.jar"
NATIVE="$ROOT/dist/project-pentagon/pentagon-native"
LOG="$RUNTIME/boot.log"
PIDFILE="$RUNTIME/pentagon.pid"

mkdir -p "$RUNTIME"
chmod 700 "$RUNTIME"
exec >>"$LOG" 2>&1

echo "[$(date -Iseconds)] Project Pentagon boot requested"

for tool in "$JAVA_BIN" termux-battery-status termux-notification; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing dependency: $tool"
    exit 1
  fi
done
if [[ ! -x "$NATIVE" || ! -f "$JAR" ]]; then
  echo "Pentagon distribution missing; expected executable and JAR under dist/project-pentagon"
  exit 1
fi
if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "Project Pentagon already running"
  exit 0
fi

export PENTAGON_RUNTIME_DIR="$RUNTIME"
cd "$ROOT"
"$JAVA_BIN" -jar "$JAR" --native "$NATIVE" &
PID=$!
echo "$PID" > "$PIDFILE"
cleanup() {
  if kill -0 "$PID" 2>/dev/null; then kill "$PID" 2>/dev/null || true; fi
  rm -f "$PIDFILE"
}
trap cleanup EXIT INT TERM

# Wake lock is opt-in; Android may still restrict background execution.
if [[ "${PENTAGON_WAKE_LOCK:-0}" == "1" ]] && command -v termux-wake-lock >/dev/null 2>&1; then
  termux-wake-lock || echo "Wake lock unavailable; continuing without it"
fi
wait "$PID"
STATUS=$?
echo "[$(date -Iseconds)] Project Pentagon exited: $STATUS"
exit "$STATUS"
