# GREP MEGA MIX

Standalone developer studio combining a GNU-oriented workbench, Raspberry Pi Pico firmware workflow, QEMU virtual-machine profiles and a Vite/React interface.

## Modules

- **GNU Workbench:** documented search, diagnostics and project command recipes. It does not execute arbitrary shell commands from the browser.
- **Pico Lab:** CMake firmware starter for physical RP2040/RP2350 boards using the official Pico SDK.
- **QEMU Engine:** optional host-side QEMU system-emulation launcher for supported guest machines.
- **Vite Studio:** responsive React/TypeScript dashboard.

## Requirements

- Node.js 20.19+ or 22.12+ recommended for Vite 6.
- npm.
- Optional: CMake, ARM embedded GCC, Raspberry Pi Pico SDK and picotool for firmware builds.
- Optional: QEMU system binaries and qemu-img for virtual machines.

## Run the interface

```sh
cd mega-mix
npm install
npm run dev
```

Open the forwarded Vite port 5173 in Codespaces.

## Validate and build

```sh
npm run typecheck
npm run build
npm run preview
```

## Isolation and safety

MEGA MIX lives entirely under `mega-mix/`. It does not alter GREP's existing Python package, tests, GitBook configuration, marketing page, active Python environment, Termux installation or global shell configuration. Dependencies are local to this frontend package. QEMU and Pico SDK are optional external host tools; the project does not install them globally, auto-flash hardware, or run arbitrary browser-supplied commands.

QEMU support depends on the host's available emulator binary, machine model and virtualization permissions. Pico firmware is built for physical hardware; QEMU's general system emulation is not a substitute for RP2040/RP2350 peripheral simulation.
