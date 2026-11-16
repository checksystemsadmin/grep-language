package pentagon

fun main() {
    val watchdog = ThermalWatchdog()
    val now = System.currentTimeMillis()
    check(watchdog.evaluate(BatterySnapshot(65, 30.0, "GOOD", false, now), now).state == "HEALTHY")
    check(watchdog.evaluate(BatterySnapshot(65, 43.0, "GOOD", false, now), now).state == "BATTERY_TEMPERATURE_WARNING")
    check(watchdog.evaluate(BatterySnapshot(65, 49.0, "GOOD", false, now), now).requestShutdown)
    check(watchdog.evaluate(BatterySnapshot(3, 30.0, "GOOD", false, now), now).requestShutdown)
    check(watchdog.evaluate(BatterySnapshot(65, 30.0, "GOOD", false, now - 60_000), now).state == "SENSOR_WARNING")
    check(watchdog.sensorFailure("test").state == "SENSOR_WARNING")
    check(watchdog.sensorFailure("test").state == "SENSOR_WARNING")
    check(watchdog.sensorFailure("test").requestShutdown)
    println("Pentagon Kotlin watchdog tests: PASS")
}
