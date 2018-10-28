cmake_minimum_required(VERSION 3.8.2)

#Approach1
#include($ENV{ZEPHYR_BASE}/cmake/section_relocation.cmake NO_POLICY_SCOPE)
#zephyr_kernel_code_relocate(src/main.c SRAM2)
#zephyr_kernel_code_relocate(src/fn.c SRAM)

#Approach2
set_property(GLOBAL PROPERTY CODE_DATA_RELOCATION_STRINGS "SRAM2:src/fn.c")

include($ENV{ZEPHYR_BASE}/cmake/app/boilerplate.cmake NO_POLICY_SCOPE)
project(test_relocation)

include_directories(src)
target_sources(app PRIVATE src/main.c)
target_sources(app PRIVATE src/fn.c)
