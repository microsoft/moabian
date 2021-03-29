board_runner_args(jlink "--device=STM32F415RG" "--speed=4000")

#include(${ZEPHYR_BASE}/boards/common/openocd.board.cmake)
include(${ZEPHYR_BASE}/boards/common/jlink.board.cmake)
