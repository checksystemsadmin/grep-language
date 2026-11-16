package pentagon

data class WatchdogConfig(
    val warningBatteryTempC: Double = 42.0,
    val criticalBatteryTempC: Double = 48.0,
    val criticalBatteryPercent: Int = 5,
    val staleAfterMs: Long = 15_000,
    val maxConsecutiveFailures: Int = 3,
) {
    init {
        require(warningBatteryTempC < criticalBatteryTempC)
        require(criticalBatteryTempC in 20.0..80.0)
        require(criticalBatteryPercent in 0..20)
        require(staleAfterMs in 1_000..300_000)
        require(maxConsecutiveFailures in 1..20)
    }
}

data class WatchdogResult(
    val state: String,
    val message: String,
    val requestShutdown: Boolean = false,
)

class ThermalWatchdog(private val config: WatchdogConfig = WatchdogConfig()) {
    private var failures = 0

    @Synchronized
    fun sensorFailure(reason: String): WatchdogResult {
        failures++
        return if (failures >= config.maxConsecutiveFailures) {
            WatchdogResult("SENSOR_FAULT", "Repeated telemetry failure: ${reason.take(100)}", true)
        } else {
            WatchdogResult("SENSOR_WARNING", "Telemetry failure $failures/${config.maxConsecutiveFailures}: ${reason.take(100)}")
        }
    }

    @Synchronized
    fun evaluate(snapshot: BatterySnapshot, nowMs: Long = System.currentTimeMillis()): WatchdogResult {
        if (nowMs - snapshot.capturedAtMs > config.staleAfterMs || snapshot.capturedAtMs > nowMs + 1000) {
            return sensorFailure("stale_or_future_telemetry")
        }
        failures = 0
        if (snapshot.temperatureC >= config.criticalBatteryTempC) {
            return WatchdogResult("CRITICAL_BATTERY_TEMPERATURE", "Battery temperature ${snapshot.temperatureC} C reached critical threshold", true)
        }
        if (snapshot.temperatureC >= config.warningBatteryTempC) {
            return WatchdogResult("BATTERY_TEMPERATURE_WARNING", "Battery temperature ${snapshot.temperatureC} C exceeded warning threshold")
        }
        if (snapshot.percentage <= config.criticalBatteryPercent) {
            return WatchdogResult("CRITICAL_BATTERY_LEVEL", "Battery at ${snapshot.percentage} percent", true)
        }
        return WatchdogResult("HEALTHY", "Battery telemetry current; SoC temperature not measured")
    }
}
