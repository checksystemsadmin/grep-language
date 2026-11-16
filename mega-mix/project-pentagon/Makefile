SHELL := /bin/sh
NIM ?= nim
NIMBLE ?= nimble
KOTLINC ?= kotlinc
JAVA ?= java
BUILD := build
NATIVE_SRC := native-ring-abc/src/pentagon.nim
NATIVE_BIN := $(BUILD)/pentagon-native
KOTLIN_SRC := $(wildcard android-ring-ed/src/main/kotlin/*.kt)

.PHONY: build-native build-arm64 test test-native test-kotlin package clean verify-tools

verify-tools:
	@command -v $(NIM) >/dev/null 2>&1 || { echo "Nim 2.x is required (NIM=$(NIM))" >&2; exit 127; }
	@$(NIM) --version | head -n 1

build-native: verify-tools
	@mkdir -p $(BUILD)
	$(NIM) c -d:release --out:$(NATIVE_BIN) $(NATIVE_SRC)

# Android ARM64 cross-build. Set ANDROID_NDK_HOME and NDK_HOST_TAG for the installed NDK.
# NDK_HOST_TAG examples: linux-x86_64, darwin-x86_64, windows-x86_64.
build-arm64: verify-tools
	@test -n "$(ANDROID_NDK_HOME)" || { echo "Set ANDROID_NDK_HOME to an installed Android NDK." >&2; exit 2; }
	@test -n "$(NDK_HOST_TAG)" || { echo "Set NDK_HOST_TAG for this build host." >&2; exit 2; }
	@CC="$(ANDROID_NDK_HOME)/toolchains/llvm/prebuilt/$(NDK_HOST_TAG)/bin/aarch64-linux-android24-clang"; \
	  test -x "$$CC" || { echo "Android ARM64 clang not found: $$CC" >&2; exit 2; }; \
	  mkdir -p $(BUILD)/android-arm64; \
	  $(NIM) c -d:release --os:linux --cpu:arm64 --cc:clang \
	    --clang.exe:"$$CC" --out:$(BUILD)/android-arm64/pentagon-native $(NATIVE_SRC)

test-native: verify-tools
	$(NIM) c -r --path:native-ring-abc/src native-ring-abc/tests/test_core.nim

test-kotlin:
	@command -v $(KOTLINC) >/dev/null 2>&1 || { echo "kotlinc is required" >&2; exit 127; }
	@mkdir -p $(BUILD)/kotlin
	$(KOTLINC) $(KOTLIN_SRC) $(KOTLIN_TEST_SRC) -jvm-target 17 -include-runtime -d $(BUILD)/kotlin/pentagon-tests.jar
	$(JAVA) -cp $(BUILD)/kotlin/pentagon-tests.jar pentagon.PentagonUnitTestsKt

test: test-native test-kotlin

package: build-native
	@mkdir -p dist/project-pentagon
	@for d in native-ring-abc android-ring-ed termux-boot tests scripts docs config; do if [ -d "$d" ]; then cp -R "$d" dist/project-pentagon/; fi; done
	@cp $(NATIVE_BIN) dist/project-pentagon/pentagon-native
	@cp Makefile pentagon.nimble dist/project-pentagon/
	@tar -C dist -czf dist/project-pentagon-0.1.0.tar.gz project-pentagon

clean:
	rm -rf $(BUILD) dist
