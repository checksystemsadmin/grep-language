# Package metadata for Project Pentagon native ring.
version       = "0.1.0"
author        = "Nolan G. Sands"
description   = "Bounded Nim native core for GREP MEGA MIX Project Pentagon"
license       = "Apache-2.0"
srcDir        = "src"
bin           = @["pentagon"]

requires "nim >= 2.0.0"

task test, "Run native unit and boundary tests":
  exec "nim c -r --path:src tests/test_core.nim"
