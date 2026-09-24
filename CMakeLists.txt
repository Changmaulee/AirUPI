cmake_minimum_required(VERSION 3.14)
project(ProjectBrahmand VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization flags
if(MSVC)
    add_compile_options(/O2 /W4 /utf-8)
else()
    add_compile_options(-O3 -Wall -Wextra -pedantic)
endif()

include_directories(cpp_core)

# Standalone CLI Executable
add_executable(brahmand cpp_core/main.cpp)

# WebAssembly Target (if using Emscripten)
if(EMSCRIPTEN)
    set_target_properties(brahmand PROPERTIES
        OUTPUT_NAME "brahmand"
        SUFFIX ".html"
        LINK_FLAGS "-s WASM=1 -s ALLOW_MEMORY_GROWTH=1 -s EXPORTED_RUNTIME_METHODS=['ccall','cwrap']"
    )
endif()
