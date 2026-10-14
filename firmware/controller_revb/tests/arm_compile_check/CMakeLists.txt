# Compile/link check of the application against the real ST HAL without STM32CubeIDE.
# Vendor code is NOT in this repository (same policy as firmware/controller/Drivers/README.md):
#   cmake -S tests/arm_compile_check -B build-arm -DCMAKE_TOOLCHAIN_FILE=../../../controller/cmake/arm-gcc.cmake \
#         -DARM_TOOLCHAIN_BIN=/path/to/arm/bin -DHAL_ROOT=... -DDEVICE_ROOT=... -DCMSIS_ROOT=...
# HAL_ROOT    = stm32g4xx-hal-driver (v1.2.5)
# DEVICE_ROOT = cmsis-device-g4 (v1.2.4)
# CMSIS_ROOT  = folder that contains CMSIS/Core/Include (CMSIS_5 5.9.0 or ST cmsis_core)
cmake_minimum_required(VERSION 3.20)
project(sc_revb_arm_check LANGUAGES C ASM)
set(CMAKE_C_STANDARD 11)
foreach(dep HAL_ROOT DEVICE_ROOT CMSIS_ROOT)
  if(NOT IS_DIRECTORY "${${dep}}")
    message(FATAL_ERROR "Set ${dep}. No automatic download.")
  endif()
endforeach()
set(APP ${CMAKE_CURRENT_SOURCE_DIR}/../..)
set(HAL_NAMES hal hal_adc hal_adc_ex hal_cortex hal_dac hal_dac_ex hal_dma hal_dma_ex hal_exti hal_fdcan hal_flash
    hal_flash_ex hal_gpio hal_iwdg hal_pwr hal_pwr_ex hal_rcc hal_rcc_ex hal_tim hal_tim_ex hal_uart hal_uart_ex)
set(HAL_SOURCES)
foreach(n IN LISTS HAL_NAMES)
  list(APPEND HAL_SOURCES "${HAL_ROOT}/Src/stm32g4xx_${n}.c")
endforeach()
set(COMMON_FLAGS -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -ffunction-sections -fdata-sections)
add_library(vendor STATIC ${HAL_SOURCES} "${DEVICE_ROOT}/Source/Templates/system_stm32g4xx.c")
target_include_directories(vendor PUBLIC ${CMAKE_CURRENT_SOURCE_DIR} "${HAL_ROOT}/Inc" "${DEVICE_ROOT}/Include"
                           "${CMSIS_ROOT}/CMSIS/Core/Include")
target_compile_definitions(vendor PUBLIC STM32G431xx USE_HAL_DRIVER)
target_compile_options(vendor PUBLIC ${COMMON_FLAGS})
target_compile_options(vendor PRIVATE -Os)
add_executable(sc_revb.elf
  ${APP}/Core/Src/sc_app.c ${APP}/Core/Src/sc_sensing.c ${APP}/Core/Src/sc_referee.c ${APP}/Core/Src/sc_canproto.c
  ${APP}/Core/Src/sc_power.c ${APP}/Core/Src/sc_supervisor.c
  cube_equiv.c "${DEVICE_ROOT}/Source/Templates/gcc/startup_stm32g431xx.s")
target_include_directories(sc_revb.elf PRIVATE ${APP}/Core/Inc)
target_compile_options(sc_revb.elf PRIVATE -Os -g3 -Wall -Wextra -Werror -Wshadow -Wdouble-promotion)
target_link_libraries(sc_revb.elf PRIVATE vendor m)
target_link_options(sc_revb.elf PRIVATE ${COMMON_FLAGS} --specs=nano.specs --specs=nosys.specs
  "-T${CMAKE_CURRENT_SOURCE_DIR}/STM32G431CB_FLASH.ld" -Wl,--gc-sections "-Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/sc_revb.map")
add_custom_command(TARGET sc_revb.elf POST_BUILD COMMAND "${CMAKE_SIZE}" $<TARGET_FILE:sc_revb.elf>)
