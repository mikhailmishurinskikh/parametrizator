cmake_minimum_required(VERSION 3.16)

project(BatteryParametrizator VERSION 0.1 LANGUAGES CXX)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_C_COMPILER "C:/Qt/Tools/mingw1310_64/bin/gcc.exe")
set(CMAKE_CXX_COMPILER "C:/Qt/Tools/mingw1310_64/bin/g++.exe")

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Core)


file(GLOB FORMS "ui/*.ui")

set(PROJECT_SOURCES
        main.cpp
        mainWindow.cpp
        mainWindow.hpp
        testsPage.cpp
        testsPage.hpp
        testsModel.cpp
        testsModel.hpp
        testsParamsDialogs.cpp
        testsParamsDialogs.hpp
        batteriesPage.cpp
        batteriesPage.hpp
        batteriesManager.cpp
        batteriesManager.hpp
        batteriesModel.cpp
        batteriesModel.hpp
        batteriesParamsDialogs.cpp
        batteriesParamsDialogs.hpp
        battery.cpp
        battery.hpp
        test.cpp
        test.hpp
        constants.hpp
        bpd.hpp
        bpd.cpp
        canvas.hpp
        canvas.cpp
        ${FORMS}
)


qt_add_executable(${PROJECT_NAME}
    MANUAL_FINALIZATION
    ${PROJECT_SOURCES}
)

target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/libs/JKQtPlotter/include/
    ${CMAKE_CURRENT_SOURCE_DIR}
)

list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_SOURCE_DIR}/libs/JKQtPlotter/lib/cmake")
find_package(JKQTPlotter6 REQUIRED)

target_link_libraries(${PROJECT_NAME} PRIVATE
    Qt${QT_VERSION_MAJOR}::Widgets
    JKQTPlotter6::JKQTPlotter6
)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)


if(QT_VERSION_MAJOR EQUAL 6)
    qt_finalize_executable(${PROJECT_NAME})
endif()