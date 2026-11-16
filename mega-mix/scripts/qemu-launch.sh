#!/usr/bin/env bash
set -euo pipefail

IMAGE="${1:-}"
QEMU_BIN="${QEMU_BIN:-qemu-system-x86_64}"

if [[ -z "$IMAGE" ]]; then
  echo "Usage: $0 <existing-qcow2-or-raw-disk-image>" >&2
  exit 2
fi
if [[ ! -f "$IMAGE" ]]; then
  echo "Disk image not found: $IMAGE" >&2
  exit 2
fi
if ! command -v "$QEMU_BIN" >/dev/null 2>&1; then
  echo "QEMU executable not found: $QEMU_BIN" >&2
  exit 127
fi

exec "$QEMU_BIN" \
  -machine q35 -accel tcg \
  -cpu max -smp 2 -m 2048 \
  -drive "file=$IMAGE,if=virtio,format=qcow2" \
  -nic user,model=virtio-net-pci \
  -display none -serial mon:stdio
