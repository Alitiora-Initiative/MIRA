cmake_minimum_required(VERSION 3.15)
project(MIRA_HFE_Engine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Threads REQUIRED)

# Source files
set(SOURCES
    src/main.cpp
    src/execution.cpp
    src/market_data.cpp
    src/risk_gateway.cpp
)

# Create executable
add_executable(hfe_engine ${SOURCES})

# Link threads
target_link_libraries(hfe_engine Threads::Threads)

# Compiler flags
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(hfe_engine PRIVATE -Wall -Wextra -O3 -march=native)
elseif(MSVC)
    target_compile_options(hfe_engine PRIVATE /W4 /O2)
endif()
