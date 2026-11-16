# QEMU Engine

QEMU is an optional host-side system emulator. It provides whole-machine emulation for supported machine types and CPU architectures; it is not a general Raspberry Pi Pico RP2040/RP2350 emulator.

## Host requirements

Install a QEMU build that provides the system binary you need (for example, `qemu-system-x86_64`) and `qemu-img`. Codespaces may not expose KVM or nested virtualization; TCG software emulation is the portable baseline where the host supports the target.

## Create a disposable disk

```sh
qemu-img create -f qcow2 build/guest.qcow2 16G
```

## Launch

```sh
bash scripts/qemu-launch.sh build/guest.qcow2
```

The launcher uses a user-mode NAT network and does not expose host directories or devices. Supply your own legally obtained guest installation media and install it into the disk image. VM execution is host-dependent and may be unavailable in browser-only development containers.