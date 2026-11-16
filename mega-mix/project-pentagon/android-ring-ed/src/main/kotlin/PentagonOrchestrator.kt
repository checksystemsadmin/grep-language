package pentagon

import java.io.BufferedWriter
import java.io.File
import java.io.InputStream
import java.io.OutputStreamWriter
import java.nio.charset.StandardCharsets
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

class PentagonOrchestrator(
    private val nativeExecutable: File,
    private val runtimeDir: File,
    private val api: TermuxApiBridge = TermuxApiBridge(),
    private val notifier: TermuxNotifier = TermuxNotifier(),
    private val watchdog: ThermalWatchdog = ThermalWatchdog(),
    private val handshakeTimeoutMs: Long = 3000,
    private val ipcTimeoutMs: Long = 2500,
) : AutoCloseable {
    private var process: Process? = null
    private var writer: BufferedWriter? = null
    private val io = Executors.newCachedThreadPool()

    fun start(): Result<Unit> = runCatching {
        require(nativeExecutable.isFile && nativeExecutable.canExecute()) { "native_binary_missing_or_not_executable" }
        require(runtimeDir.mkdirs() || runtimeDir.isDirectory) { "runtime_directory_unavailable" }
        val child = ProcessBuilder(nativeExecutable.absolutePath)
            .directory(runtimeDir)
            .redirectError(ProcessBuilder.Redirect.appendTo(File(runtimeDir, "native.stderr.log")))
            .start()
        process = child
        writer = BufferedWriter(OutputStreamWriter(child.outputStream, StandardCharsets.UTF_8))
        val ready = readBoundedLine(child.inputStream, 4096, handshakeTimeoutMs)
        require(ready.contains("\"type\":\"READY\"")) { "native_readiness_handshake_failed" }
    }

    fun sampleBattery(): WatchdogResult {
        val snapshotResult = api.readBattery()
        if (snapshotResult.isFailure) {
            val fault = watchdog.sensorFailure(snapshotResult.exceptionOrNull()?.message ?: "termux_api_failure")
            notifier.notify("Project Pentagon: ${fault.state}", fault.message)
            if (fault.requestShutdown) shutdownNative()
            return fault
        }
        val snapshot = snapshotResult.getOrThrow()
        val result = watchdog.evaluate(snapshot)
        if (result.state != "HEALTHY") notifier.notify("Project Pentagon: ${result.state}", result.message)
        if (!result.requestShutdown) {
            val request = """{"type":"TELEMETRY","battery_percent":${snapshot.percentage},"battery_temp_c":${snapshot.temperatureC},"charging":${snapshot.charging},"battery_health":"${snapshot.health}","timestamp_ms":${snapshot.capturedAtMs}}"""
            val response = exchange(request)
            if (!response.contains("\"type\":\"OK\"")) {
                notifier.notify("Project Pentagon: IPC fault", "Native telemetry exchange rejected or timed out")
            }
        } else {
            shutdownNative()
        }
        return result
    }

    private fun exchange(line: String): String {
        require(line.length <= 4096) { "ipc_request_too_large" }
        val child = process ?: error("native_process_not_started")
        require(child.isAlive) { "native_process_not_alive" }
        writer?.apply { write(line); newLine(); flush() } ?: error("native_stdin_unavailable")
        return readBoundedLine(child.inputStream, 4096, ipcTimeoutMs)
    }

    private fun readBoundedLine(stream: InputStream, maxBytes: Int, timeoutMs: Long): String {
        val future = io.submit<String> {
            val out = StringBuilder()
            while (true) {
                val value = stream.read()
                if (value < 0) error("ipc_eof")
                if (value == 10) break
                if (value == 13) continue
                require(value >= 32) { "ipc_control_character" }
                require(out.length < maxBytes) { "ipc_line_too_large" }
                out.append(value.toChar())
            }
            out.toString()
        }
        return try { future.get(timeoutMs, TimeUnit.MILLISECONDS) }
        catch (e: Exception) { future.cancel(true); throw IllegalStateException("ipc_timeout_or_read_error", e) }
    }

    fun shutdownNative() {
        val child = process ?: return
        runCatching {
            writer?.apply { write("""{"type":"SHUTDOWN"}"""); newLine(); flush() }
            child.waitFor(1500, TimeUnit.MILLISECONDS)
        }
        if (child.isAlive) child.destroy()
        if (child.isAlive && !child.waitFor(500, TimeUnit.MILLISECONDS)) child.destroyForcibly()
        process = null
    }

    override fun close() {
        shutdownNative()
        io.shutdownNow()
    }
}
