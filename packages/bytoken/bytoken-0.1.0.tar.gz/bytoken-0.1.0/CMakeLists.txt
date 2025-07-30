cmake_minimum_required(VERSION 3.14)
project(bytoken)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)

pybind11_add_module(bytoken
    bytoken/bytoken_binding.cpp
    bytoken/bytoken.cpp
)

target_include_directories(bytoken PRIVATE ${CMAKE_SOURCE_DIR}/bytoken)

install(TARGETS bytoken DESTINATION bytoken)

install(FILES bytoken/__init__.py DESTINATION bytoken)
