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

  test "bounded queue rejects work after capacity":
    var q: BoundedQueue
    initQueue(q, 1)
    check enqueue(q, "first")
    check not enqueue(q, "second")
    let item = dequeue(q)
    check item.ok
    check item.value == "first"

  test "MRE test-buffer allocation respects configured limit":
    var reserve: MreReserve
    initMre(reserve, 1024)
    check not allocateTestBuffer(reserve, 1)
    check not allocateTestBuffer(reserve, 2048)
