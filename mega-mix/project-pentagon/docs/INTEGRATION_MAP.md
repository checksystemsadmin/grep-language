# GREP MEGA MIX Integration Map

## Inspected target state

Inspected on branch `feat/mega-mix-standalone`:

- `mega-mix/package.json`: Vite 6, React 18, TypeScript 5.7 and lucide-react.
- `mega-mix/src/App.tsx`: client-side module navigation, static command recipes, copy-to-clipboard controls, and status labels. It explicitly says browser commands are not executed.
- `mega-mix/pico/CMakeLists.txt` and `pico/src/main.c`: physical Pico firmware starter using the official Pico SDK.
- `mega-mix/qemu/README.md` and `scripts/qemu-launch.sh`: optional host QEMU system-emulation documentation and launcher.
- Root `pyproject.toml`: GREP remains a Python >=3.9 package with the `greplang` entry point.
- Root `AGENTS.md`: preserve docs/index.html, docs/guide/, gitbook-docs.yaml; keep Python 3.9 compatibility; run GREP unit tests, validate, doctor, and diff checks before release.

## Existing capability versus Pentagon requirement

| Requirement | Existing target capability | Integration decision |
|---|---|---|
| GNU/search | GREP Python package and GNU-oriented UI recipes | Keep GREP as-is; Pentagon's diode is separate |
| Native ARM64 | No Pentagon native executable | Add Nim core under Pentagon |
| Nim 2.x | Not present in MEGA MIX | Add local Nimble package and Make targets |
| Kotlin/JVM | Not present in MEGA MIX | Add standalone JVM supervisor |
| Queues/MRE | Not present | Add bounded queue and test-buffer reserve |
| Data validation | GREP has its own parser/CLI validation | Add strict protocol-specific allowlist |
| Battery telemetry | No device telemetry service | Add optional Termux:API adapter |
| Process lifecycle | Browser UI does not execute processes | Kotlin supervisor owns only its configured native child |
| Pico | Physical firmware starter exists | Keep independent; no false QEMU Pico emulation claim |
| QEMU | Host VM launcher exists | Keep independent from Android Termux runtime |
| Dashboard | Static React dashboard | Add read-only Pentagon module/status integration only after backend contract is tested |

## Files to preserve

Do not modify or replace the root GREP package, root Python dependency configuration, root test suite, marketing site, GitBook guide, GitBook configuration, Pico starter, or QEMU launcher as part of Pentagon's initial implementation.

## Deployment distinction

Codespaces can host source review and web builds. It cannot certify Android 16 execution. ARM64 binary, Kotlin process behavior, Termux:API permissions, background lifecycle and thermal/battery telemetry must be verified on the actual Android 16 ARM64 Termux device.

## Explicit non-goals

- No root or privileged Android operations.
- No protected sysfs writes.
- No physical USB-OTG switching.
- No unbounded queues or memory allocation.
- No shell execution from IPC or browser input.
- No claims of secure memory wiping.
- No fabricated sensor values.
- No assertion that QEMU emulates RP2040/RP2350 peripherals.
