# Build and Deploy Project Pentagon

## Tool requirements

- Nim 2.x and Nimble.
- Kotlin compiler (`kotlinc`) and Java 17 runtime.
- Android NDK only for cross-compilation from a non-Android host.
- Termux:API app and `termux-api` package for battery/notification integration on device.

## Native simulation / host build

```sh
cd mega-mix/project-pentagon
make build-native
make test-native
```

## Android ARM64 cross-build

Set `ANDROID_NDK_HOME` and `NDK_HOST_TAG` for the installed NDK host package, then run:

```sh
make build-arm64 ANDROID_NDK_HOME="$ANDROID_NDK_HOME" NDK_HOST_TAG=linux-x86_64
scripts/check-android-arm64.sh build/android-arm64/pentagon-native
```

This is a candidate Android ARM64 build, not verified until run on the target Android 16 Termux device. The NDK Clang path and Nim Clang backend must match the installed Nim release.

## Kotlin/JVM

```sh
make build-kotlin
java -jar build/kotlin/pentagon.jar --native "$PWD/build/pentagon-native"
```

The Kotlin layer is JVM-only and does not link Android framework APIs.

## Tests and packaging

```sh
make test
make package
```

The archive is created at `dist/project-pentagon-0.1.0.tar.gz`. The package target requires the Nim and Kotlin toolchains.

## Termux deployment

Extract the archive into an app-private project directory. Ensure the native executable has execute permission. Install Termux:API and the companion Android Termux:API app, grant notification permission where required, then invoke the boot script manually for the first run. Termux:Boot is optional and subject to Android background restrictions.
