# Project Pentagon — GREP MEGA MIX Integration Architecture

Status: Phase 1 architecture baseline (design only; implementation status is tracked separately).

## Target and boundary

Project Pentagon is a self-contained subsystem under `mega-mix/project-pentagon/`. It does not replace GREP's Python package, GREP CLI, Vite frontend, Pico firmware target, or QEMU host-emulation workflow. It does not modify the repository root Python environment, GitBook files, marketing page, or global Termux configuration.

Primary deployment target: unprivileged Android 16 ARM64 Termux. The Codespaces environment is a development and review environment, not proof of Android ABI compatibility.

## Five rings

| Ring | Component | Responsibility | Boundary |
|---|---|---|---|
| A | Nim native core | bounded processing, deadlines, deterministic simulation | stdin/stdout protocol only |
| B | MRE reserve + queue | bounded queue and explicitly allocated test-buffer reserve | no claim of secure erase or cryptographic work |
| C | Data Diode | allowlisted telemetry schema, strict key/value validation, safe responses | rejects unknown fields and malformed records |
| D | Kotlin telemetry | Termux:API battery readings, freshness, consecutive failures, thresholds | battery temperature is not SoC temperature |
| E | Kotlin orchestrator | child process lifecycle, bounded IPC, readiness, watchdog, notifications | fixed executable and arguments; no shell command interpretation |

## Process topology

```text
Termux session / optional Termux:Boot
  └─ Pentagon JVM supervisor
       ├─ fixed native executable (Nim)
       │    stdin: one bounded JSON request per line
       │    stdout: READY / TELEMETRY / OK / ERROR / DIODE_BREACH / SHUTDOWN
       │    stderr: bounded diagnostic log stream
       ├─ Termux:API bridge (fixed termux-battery-status invocation)
       └─ local runtime workspace (pid/log/state; restrictive app-private directory)
```

The supervisor owns the native process. The native process never launches arbitrary commands. The browser dashboard is informational in this phase and is not an execution bridge.

## IPC contract

- UTF-8, one JSON object per line, maximum 4096 bytes.
- Each message has a `type` field from the fixed event allowlist.
- No multiline JSON, unknown event, unknown field, duplicate key, control character, or oversized line.
- Startup: native emits `READY`; supervisor applies a handshake deadline before sending requests.
- Requests are data only. They cannot name an executable, path, shell fragment, or process argument.
- Responses are bounded and parsed as data. `DIODE_BREACH` is a rejection event, not a process command.
- Shutdown: supervisor sends a bounded `SHUTDOWN` request, waits a finite grace interval, then terminates the child if needed.

## Resource and failure model

- Queue capacity, MRE allocation, line size, processing time, telemetry age, restart count, and watchdog interval are configuration-bounded.
- Queue full is explicit; it does not silently allocate unbounded memory.
- MRE consists of allocated test buffers only. It is not a secure allocator, cryptographic puzzle, swap substitute, or guaranteed emergency heap.
- Termux:API absence, timeout, malformed JSON, missing fields, stale values, and repeated failures are sensor faults. No nominal temperature is fabricated.
- Battery temperature is reported as the battery sensor value. SoC temperature remains unavailable unless a separate supported sensor source is implemented and verified.
- No sysfs writes, root operations, mount operations, physical USB switching, or destructive hardware tests.
- File overwrite is not represented as secure erasure. Cleanup is best-effort deletion of app-private transient files.

## Build strategy

1. Host/simulation build for fast deterministic tests.
2. Native Termux ARM64 build using the device's available C toolchain and Nim 2.x.
3. Optional Android NDK cross-build only when a matching NDK toolchain is explicitly configured.
4. Verify executable format and architecture with available `file`/ELF inspection tools, inspect dynamic dependencies, then execute on the actual Android ARM64 target.
5. Kotlin/JVM compiles independently of Android framework classes. Android SDK 36 / `android.jar` is intentionally not a dependency unless a future Android framework adapter is added.

## GREP MEGA MIX integration

The existing React dashboard has module navigation and static command recipes. It has no backend execution service. Pentagon will first expose documented status/configuration contracts; a later dashboard adapter may display supervisor health through a local read-only endpoint or generated status file. It must not turn browser input into shell commands.

## Phase map

- Phase 1: architecture and integration map — documented.
- Phase 2: Nim core, queue/MRE, diode, Makefile and Nimble package.
- Phase 3: Kotlin/JVM API bridge, watchdog and supervisor.
- Phase 4: native/Kotlin unit and fault-injection tests.
- Phase 5: real bounded IPC integration tests.
- Phase 6: read-only MEGA MIX dashboard status integration.
- Phase 7: reproducible ARM64 packaging and on-device verification.
- Phase 8: documentation and release checklist.

No phase is considered complete from source creation alone; execution evidence is required.
