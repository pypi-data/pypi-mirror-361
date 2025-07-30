cmake_minimum_required(VERSION 3.14)
project(bytoken)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Python
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

# Fetch pybind11 directly
include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG        v2.11.1  # or latest stable tag
)
FetchContent_MakeAvailable(pybind11)

# Build the module
pybind11_add_module(bytoken
    bytoken/bytoken_binding.cpp
    bytoken/bytoken.cpp
)

# Headers
target_include_directories(bytoken PRIVATE ${CMAKE_SOURCE_DIR}/bytoken)

# Install binary + Python file
install(TARGETS bytoken DESTINATION .)
install(FILES bytoken/__init__.py DESTINATION .)
