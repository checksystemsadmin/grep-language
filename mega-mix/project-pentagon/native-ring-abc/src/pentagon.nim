import std/[json, strutils, deques, locks, math]

const
  MaxLineBytes* = 4096
  MaxQueueItems* = 64
  MaxPayloadBytes* = 1024 * 1024
  DefaultMreBytes* = 64 * 1024

type
  BoundedQueue = object
    guard: Lock
    items: Deque[string]
    capacity: int
  MreReserve = object
    guard: Lock
    buffers: seq[seq[byte]]
    allocatedBytes: int
    limitBytes: int

var workQueue: BoundedQueue
var mre: MreReserve

proc initQueue(q: var BoundedQueue, capacity: int) =
  initLock(q.guard)
  q.items = initDeque[string]()
  q.capacity = max(1, min(capacity, MaxQueueItems))

proc enqueue(q: var BoundedQueue, value: string): bool =
  acquire(q.guard)
  result = q.items.len < q.capacity
  if result: q.items.addLast(value)
  release(q.guard)

proc dequeue(q: var BoundedQueue): tuple[ok: bool, value: string] =
  acquire(q.guard)
  if q.items.len > 0:
    result.ok = true
    result.value = q.items.popFirst()
  release(q.guard)

proc initMre(r: var MreReserve, bytes: int) =
  initLock(r.guard)
  r.limitBytes = max(0, min(bytes, MaxPayloadBytes))
  r.allocatedBytes = 0
  r.buffers = @[]

proc allocateTestBuffer(r: var MreReserve, bytes: int): bool =
  if bytes <= 0 or bytes > MaxPayloadBytes: return false
  acquire(r.guard)
  result = bytes <= r.limitBytes - r.allocatedBytes
  if result:
    # Explicit test allocation only. This is not secure memory and is not a cryptographic reserve.
    r.buffers.add(newSeq[byte](bytes))
    r.allocatedBytes += bytes
  release(r.guard)

proc isAllowedKey(key: string): bool =
  key in ["type", "battery_percent", "battery_temp_c", "charging", "battery_health", "timestamp_ms", "payload"]

proc validateTelemetry*(node: JsonNode): tuple[ok: bool, reason: string] =
  if node.kind != JObject: return (false, "object_required")
  for key, value in node:
    if not isAllowedKey(key): return (false, "unknown_key:" & key)
    if key == "type" and (value.kind != JString or value.getStr() != "TELEMETRY"):
      return (false, "invalid_type")
  for key in ["battery_percent", "battery_temp_c", "charging", "battery_health", "timestamp_ms"]:
    if not node.hasKey(key): return (false, "missing_key:" & key)
  if node["battery_percent"].kind != JInt: return (false, "battery_percent_type")
  let pct = node["battery_percent"].getInt()
  if pct < 0 or pct > 100: return (false, "battery_percent_range")
  if node["battery_temp_c"].kind notin {JInt, JFloat}: return (false, "battery_temp_type")
  let temp = if node["battery_temp_c"].kind == JInt: node["battery_temp_c"].getInt().float else: node["battery_temp_c"].getFloat()
  if classify(temp) in {fcNan, fcInf, fcNegInf} or temp < -30.0 or temp > 100.0:
    return (false, "battery_temp_range")
  if node["charging"].kind != JBool: return (false, "charging_type")
  if node["battery_health"].kind != JString: return (false, "battery_health_type")
  let health = node["battery_health"].getStr()
  if health notin ["UNKNOWN", "GOOD", "OVERHEAT", "DEAD", "OVER_VOLTAGE", "UNSPECIFIED_FAILURE", "COLD"]:
    return (false, "battery_health_value")
  if node["timestamp_ms"].kind != JInt: return (false, "timestamp_type")
  if node.hasKey("payload"):
    if node["payload"].kind != JString or node["payload"].getStr().len > 512:
      return (false, "payload_invalid")
    for ch in node["payload"].getStr():
      if ord(ch) < 32 or ord(ch) == 127: return (false, "payload_control_character")
  return (true, "")

proc safeResponse(kind: string, detail = ""): string =
  var node = newJObject()
  node["type"] = %kind
  if detail.len > 0:
    var clean = ""
    for ch in detail:
      if ch >= ' ' and ch != '\\' and ch != '"' and clean.len < 120: clean.add(ch)
    node["detail"] = %clean
  $node

proc readBoundedLine(input: File, limit: int): tuple[ok: bool, line: string, tooLong: bool] =
  var value = newStringOfCap(limit)
  while not input.endOfFile:
    let ch = input.readChar()
    if ch == '\n': return (true, value, false)
    if ch == '\r': continue
    if value.len >= limit:
      while not input.endOfFile:
        if input.readChar() == '\n': break
      return (false, "", true)
    if ord(ch) < 32 and ch != '\t': return (false, "", false)
    value.add(ch)
  if value.len > 0: return (true, value, false)
  return (false, "", false)

proc handleLine(line: string): string =
  var request: JsonNode
  try:
    request = parseJson(line)
  except CatchableError:
    return safeResponse("ERROR", "malformed_json")
  if request.kind != JObject or not request.hasKey("type") or request["type"].kind != JString:
    return safeResponse("DIODE_BREACH", "invalid_envelope")
  let event = request["type"].getStr()
  case event
  of "TELEMETRY":
    let checked = validateTelemetry(request)
    if not checked.ok: return safeResponse("DIODE_BREACH", checked.reason)
    if not enqueue(workQueue, line):
      discard allocateTestBuffer(mre, DefaultMreBytes)
      return safeResponse("ERROR", "queue_full_mre_fallback")
    let item = dequeue(workQueue)
    if item.ok: return safeResponse("OK", "telemetry_accepted")
    return safeResponse("ERROR", "queue_state_error")
  of "SHUTDOWN":
    return safeResponse("SHUTDOWN", "accepted")
  else:
    return safeResponse("DIODE_BREACH", "event_not_allowed")

when isMainModule:
  initQueue(workQueue, MaxQueueItems)
  initMre(mre, DefaultMreBytes)
  stdout.writeLine(safeResponse("READY", "pentagon-native-v0.1.0"))
  stdout.flushFile()
  while true:
    let incoming = readBoundedLine(stdin, MaxLineBytes)
    if incoming.tooLong:
      stdout.writeLine(safeResponse("DIODE_BREACH", "line_too_long"))
      stdout.flushFile()
      continue
    if not incoming.ok: break
    let response = handleLine(incoming.line)
    stdout.writeLine(response)
    stdout.flushFile()
    if response.contains("\"type\":\"SHUTDOWN\""): break
  stdout.writeLine(safeResponse("SHUTDOWN", "native_exit"))
  stdout.flushFile()
