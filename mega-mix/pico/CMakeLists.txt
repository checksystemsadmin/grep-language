cmake_minimum_required(VERSION 3.13)

# Supply PICO_SDK_PATH from the environment or with -DPICO_SDK_PATH=...
if(NOT DEFINED PICO_SDK_PATH AND DEFINED ENV{PICO_SDK_PATH})
  set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
endif()
if(NOT PICO_SDK_PATH)
  message(FATAL_ERROR "Set PICO_SDK_PATH to a separately installed Raspberry Pi Pico SDK checkout.")
endif()

include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)
project(grep_mega_mix_pico C CXX ASM)
pico_sdk_init()

add_executable(gmx_pico_probe src/main.c)
target_link_libraries(gmx_pico_probe pico_stdlib)
pico_enable_stdio_usb(gmx_pico_probe 1)
pico_enable_stdio_uart(gmx_pico_probe 0)
pico_add_extra_outputs(gmx_pico_probe)