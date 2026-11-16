# Project Pentagon Security and Operational Limitations

- Runs as an ordinary Termux application process; root is neither required nor requested.
- No protected sysfs writes, privileged mounts, USB role switching, or hardware mutation.
- IPC accepts bounded data messages only. It does not execute shell commands or accept executable paths from telemetry.
- The native process is started from one configured executable path by Kotlin ProcessBuilder.
- The Termux API adapter invokes fixed command names without a shell. Install and authorize Termux:API separately.
- Battery temperature is not SoC temperature. A missing/stale sensor is a fault; no nominal value is synthesized.
- MRE uses bounded allocated byte buffers for allocation/fallback tests. It does not guarantee emergency allocation under system-wide memory exhaustion and is not a cryptographic reserve.
- Deleting transient files is best effort. Overwriting a file is not proof of secure erasure on flash storage.
- Android background execution and Termux:Boot timing are controlled by Android power-management policies. A wake lock is optional and disabled by default.
- A watchdog-triggered process exit cannot guarantee device-level thermal safety. Android's system thermal protections remain authoritative.
- The JVM implementation intentionally avoids Android framework APIs. SDK 36 / android.jar is not needed for the standalone JVM runtime.
- The current prototype should be treated as experimental until on-device ARM64 build, ABI, Termux:API, notification, and lifecycle tests are completed.
