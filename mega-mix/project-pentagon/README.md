# Project Pentagon

Five-ring native computing and Android 16 Termux integration subsystem for GREP MEGA MIX.

**Current status:** Phase 1 architecture documented. Native and Kotlin implementation phases have not yet been built or tested.

See [Architecture](docs/ARCHITECTURE.md) and [Integration Map](docs/INTEGRATION_MAP.md).

Target runtime: unprivileged Android 16 ARM64 Termux. Codespaces is used for source development and review only.

The subsystem is isolated under this directory. It does not change GREP's Python package, existing MEGA MIX Pico/QEMU toolchains, global Termux configuration, or other projects.
