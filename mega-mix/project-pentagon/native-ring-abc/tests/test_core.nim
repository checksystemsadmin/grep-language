import std/[unittest, json]
import ../src/pentagon

suite "Project Pentagon native core":
  test "accepts a well-formed telemetry envelope":
    let node = parseJson("""{"type":"TELEMETRY","battery_percent":55,"battery_temp_c":31.5,"charging":true,"battery_health":"GOOD","timestamp_ms":1000}""")
    check validateTelemetry(node).ok

  test "rejects unknown fields":
    let node = parseJson("""{"type":"TELEMETRY","battery_percent":55,"battery_temp_c":31.5,"charging":true,"battery_health":"GOOD","timestamp_ms":1000,"shell":"id"}""")
    check not validateTelemetry(node).ok

  test "rejects out of range battery percentage":
    let node = parseJson("""{"type":"TELEMETRY","battery_percent":101,"battery_temp_c":31.5,"charging":true,"battery_health":"GOOD","timestamp_ms":1000}""")
    check not validateTelemetry(node).ok

  test "rejects control characters in payload":
    let node = parseJson("""{"type":"TELEMETRY","battery_percent":55,"battery_temp_c":31.5,"charging":true,"battery_health":"GOOD","timestamp_ms":1000,"payload":"ok\u0001bad"}""")
    check not validateTelemetry(node).ok
