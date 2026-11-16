#!/usr/bin/env bash
set -euo pipefail
BIN="${1:-build/android-arm64/pentagon-native}"
if [[ ! -f "$BIN" ]]; then echo "Binary not found: $BIN" >&2; exit 2; fi
command -v file >/dev/null 2>&1 || { echo "'file' is required for ELF inspection" >&2; exit 127; }
file "$BIN"
if command -v readelf >/dev/null 2>&1; then
  readelf -h "$BIN" | grep -E 'Class:|Machine:|OS/ABI:'
  readelf -d "$BIN" 2>/dev/null | grep NEEDED || true
else
  echo "readelf unavailable; dynamic dependency inspection incomplete"
fi
echo "Static inspection only. Runtime compatibility must be verified on Android 16 ARM64 Termux."
