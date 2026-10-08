# External STM32 dependencies

No vendor code is copied into this public repository. Project-authored code is in `Core/`, `App/`, `config/`, `tests/` and `tools/`. No CubeMX-generated files are claimed.

Build-tested source dependencies (unmodified, kept in ignored local storage):

| Dependency | Pinned version / commit | License | CMake setting |
|---|---|---|---|
| [ST G4 HAL](https://github.com/STMicroelectronics/stm32g4xx-hal-driver/tree/v1.2.5) |v1.2.5 / d69997c6dcdc2d672afae31fee03713fb033c4a8|BSD-3-Clause in LICENSE.md|HAL_ROOT|
| [ST G4 CMSIS device](https://github.com/STMicroelectronics/cmsis-device-g4/tree/v1.2.4)|v1.2.4 / f4ee399953e3b5c437788526e93b10efa5fad4fa|Apache-2.0|DEVICE_ROOT|
| [Arm CMSIS core](https://github.com/ARM-software/CMSIS_5/tree/5.9.0)|5.9.0 / 2b7495b8535bdcb306dac29b9ded4cfb679d7e5c|Apache-2.0|CMSIS_ROOT|

An installed STM32CubeG4 package may supply the same directories, but its exact revision must be recorded and rebuilt/reviewed. `CMSIS_ROOT/CMSIS/Core/Include` is the standalone CMSIS layout; for a Cube package point to its corresponding root layout or adjust the include path explicitly. Dependencies are not fetched by CMake. Toolchain installation, board connection and flashing are never build actions.
