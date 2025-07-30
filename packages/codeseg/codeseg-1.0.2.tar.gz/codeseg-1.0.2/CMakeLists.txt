cmake_minimum_required(VERSION 3.22.1)
project(CoDeSEG)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

include_directories(${PROJECT_SOURCE_DIR}/lib)



add_executable(CoDeSEG 
       src/main.cpp
        src/lib/CoDeSEG.cpp
        src/lib/CoDeSEG.h
        src/lib/DynamicArray.cpp
        src/lib/DynamicArray.h
        src/lib/CxxOpts.h
        src/lib/Utility.h
        src/lib/Utility.cpp
        src/lib/ThreadPool.h
        src/lib/CDS_Dynamic.cpp
        src/lib/CDS_Dynamic.h
)

find_package(Threads REQUIRED)
target_link_libraries(CoDeSEG PRIVATE Threads::Threads)

install(TARGETS CoDeSEG
    RUNTIME DESTINATION bin
)