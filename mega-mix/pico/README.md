# Pico Lab

This is a real firmware target for Raspberry Pi Pico-family hardware, not a QEMU board-emulation claim.

## Supported SDK targets

- Pico / Pico W: RP2040, select the matching board.
- Pico 2 / Pico 2 W: RP2350, select the matching board.
- RP2350 RISC-V builds: select `PICO_PLATFORM=rp2350-riscv` where supported by the board configuration.

## Build

Install the official Raspberry Pi Pico SDK and ARM embedded toolchain in your own development environment. Keep them outside this repository or in an ignored project-local tool directory. Then:

```sh
export PICO_SDK_PATH="$HOME/dev/pico-sdk"
cmake -S pico -B build/pico -DPICO_BOARD=pico
cmake --build build/pico
```

For Pico 2, use `-DPICO_BOARD=pico2`. The UF2 output is generated in `build/pico/`. Flash only to a physically connected, correctly identified board. This project does not auto-flash devices.