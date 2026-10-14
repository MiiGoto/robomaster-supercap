# Host tests for the portable logic (no HAL).  cmake -S tests -B build && cmake --build build && ./build/test_sc
cmake_minimum_required(VERSION 3.16)
project(sc_revb_tests C)
set(CMAKE_C_STANDARD 11)
add_compile_options(-Wall -Wextra -Werror -Wno-unused-parameter)
set(SRC ${CMAKE_CURRENT_SOURCE_DIR}/../Core/Src)
add_executable(test_sc test_sc.c ${SRC}/sc_sensing.c ${SRC}/sc_referee.c ${SRC}/sc_canproto.c
               ${SRC}/sc_power.c ${SRC}/sc_supervisor.c)
target_include_directories(test_sc PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../Core/Inc)
target_link_libraries(test_sc m)
enable_testing()
add_test(NAME sc_logic COMMAND test_sc)
