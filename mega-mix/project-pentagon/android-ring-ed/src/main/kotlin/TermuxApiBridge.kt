package pentagon

import java.io.File
import java.util.concurrent.TimeUnit

data class BatterySnapshot(
    val percentage: Int,
    val temperatureC: Double,
    val health: String,
    val charging: Boolean,
    val capturedAtMs: Long,
)

class TermuxApiBridge(
    private val command: String = "termux-battery-status",
    private val timeoutMs: Long = 2500,
) {
    fun readBattery(nowMs: Long = System.currentTimeMillis()): Result<BatterySnapshot> = runCatching {
        // Fixed executable name; no shell, interpolated arguments, or user-provided command.
        val process = ProcessBuilder(command).redirectErrorStream(true).start()
        if (!process.waitFor(timeoutMs, TimeUnit.MILLISECONDS)) {
            process.destroy()
            if (!process.waitFor(250, TimeUnit.MILLISECONDS)) process.destroyForcibly()
            error("termux_api_timeout")
        }
        val output = process.inputStream.readNBytes(8193)
        require(output.size <= 8192) { "termux_api_output_too_large" }
        require(process.exitValue() == 0) { "termux_api_exit_${process.exitValue()}" }
        parseBatteryJson(output.toString(Charsets.UTF_8), nowMs)
    }

    private fun parseBatteryJson(raw: String, nowMs: Long): BatterySnapshot {
        require(raw.length <= 8192) { "battery_json_too_large" }
        // Strict flat-object parser for the fields emitted by Termux:API. Unknown fields
        // are rejected intentionally so the adapter contract changes visibly.
        val trimmed = raw.trim()
        require(trimmed.startsWith("{") && trimmed.endsWith("}")) { "battery_json_object_required" }
        val fields = linkedMapOf<String, String>()
        val pattern = Regex("\"([A-Za-z_]+)\"\\s*:\\s*(\"(?:\\\\.|[^\"\\\\])*\"|-?[0-9]+(?:\\.[0-9]+)?|true|false|null)")
        val matches = pattern.findAll(trimmed).toList()
        require(matches.isNotEmpty()) { "battery_json_empty" }
        for (match in matches) {
            val key = match.groupValues[1]
            require(key !in fields) { "battery_json_duplicate_key" }
            fields[key] = match.groupValues[2].trim('"')
        }
        val residue = pattern.replace(trimmed, "").replace(Regex("[{},\\s:,]"), "")
        require(residue.isEmpty()) { "battery_json_malformed" }
        val allowed = setOf("health", "percentage", "plugged", "status", "temperature", "current", "voltage", "technology")
        require(fields.keys.all { it in allowed }) { "battery_json_unknown_key" }
        val percentage = fields["percentage"]?.toIntOrNull() ?: error("battery_percentage_missing_or_invalid")
        require(percentage in 0..100) { "battery_percentage_out_of_range" }
        val temperature = fields["temperature"]?.toDoubleOrNull() ?: error("battery_temperature_missing_or_invalid")
        require(temperature.isFinite() && temperature in -30.0..100.0) { "battery_temperature_out_of_range" }
        val health = fields["health"] ?: error("battery_health_missing")
        require(health in setOf("UNKNOWN", "GOOD", "OVERHEAT", "DEAD", "OVER_VOLTAGE", "UNSPECIFIED_FAILURE", "COLD")) { "battery_health_invalid" }
        val plugged = fields["plugged"] ?: error("battery_plugged_missing")
        val charging = plugged !in setOf("UNPLUGGED", "NONE", "0")
        BatterySnapshot(percentage, temperature, health, charging, nowMs)
    }
}

class TermuxNotifier(
    private val command: String = "termux-notification",
    private val timeoutMs: Long = 2000,
) {
    fun notify(title: String, message: String): Boolean = runCatching {
        val safeTitle = title.take(80).filter { it >= ' ' && it != '\u007f' }
        val safeMessage = message.take(240).filter { it >= ' ' && it != '\u007f' }
        val process = ProcessBuilder(command, "--title", safeTitle, "--content", safeMessage)
            .redirectErrorStream(true).start()
        if (!process.waitFor(timeoutMs, TimeUnit.MILLISECONDS)) {
            process.destroyForcibly()
            false
        } else process.exitValue() == 0
    }.getOrDefault(false)
}
