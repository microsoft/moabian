cmake_minimum_required(VERSION 3.13.1)

# Board-specific files should get merged into the build as well.
set(BOARD_ROOT ${CMAKE_CURRENT_LIST_DIR})
set(BOARD moab_hat)
set(DTS_ROOT ${CMAKE_CURRENT_LIST_DIR})

# Add a common dts overlay necessary to ensure mcuboot is linked into,
# and fits inside, the boot partition. (If the user specified a
# DTC_OVERLAY_FILE on the CMake command line, we need to append onto
# the list).
if(DTC_OVERLAY_FILE)
  set(DTC_OVERLAY_FILE
    "${DTC_OVERLAY_FILE} ${CMAKE_CURRENT_LIST_DIR}/dts.overlay"
    CACHE STRING "" FORCE
    )
else()
  set(DTC_OVERLAY_FILE ${CMAKE_CURRENT_LIST_DIR}/dts.overlay)
endif()

add_compile_options(-Wall)

include($ENV{ZEPHYR_BASE}/cmake/app/boilerplate.cmake NO_POLICY_SCOPE)

project(app VERSION 3.0.0.0)

set(SEMVER $ENV{SEMVER})
message("Moab SEMVER=${SEMVER}")

configure_file(app/app_version.h.in app_version.h)
target_include_directories(app PUBLIC "${PROJECT_BINARY_DIR}")

target_sources(app PRIVATE
	app/display.c
	app/font_din2014light_12.c
	app/font_din2014_18.c
	app/font_moabsym_30.c
	app/font_iecsymbol_30.c
	app/joystick.c
	app/main.c
	app/spi.c
	app/plate.c
	app/sh1106_spi.c
	app/shell.c
    app/state.c
)

