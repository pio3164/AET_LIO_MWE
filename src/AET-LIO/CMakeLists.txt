cmake_minimum_required(VERSION 2.8.3)
project(aet_lio)

set(CMAKE_BUILD_TYPE "Release")

add_compile_options(-std=c++14)
set(CMAKE_CXX_FLAGS "-std=c++14 -O3 -pthread")

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  sensor_msgs
  geometry_msgs
  nav_msgs
  message_generation
  tf
  pcl_ros
  pcl_conversions
  eigen_conversions
)

find_package(PCL REQUIRED)
find_package(Eigen3 REQUIRED)

add_message_files(
  FILES
  Pose6D.msg
)

generate_messages(
  DEPENDENCIES
  std_msgs
  geometry_msgs
  nav_msgs
  sensor_msgs
)

catkin_package(
  INCLUDE_DIRS include
  CATKIN_DEPENDS
    roscpp
    rospy
    std_msgs
    sensor_msgs
    geometry_msgs
    nav_msgs
    message_runtime
    tf
    pcl_ros
    pcl_conversions
    eigen_conversions
)

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
  ${PCL_INCLUDE_DIRS}
  ${EIGEN3_INCLUDE_DIR}
)

link_directories(
  ${PCL_LIBRARY_DIRS}
)

add_definitions(${PCL_DEFINITIONS})

# ============================================================
# 关键：导入预编译核心库 libaet_lio_core.so
# ============================================================

add_library(aet_lio_core SHARED IMPORTED)

set_target_properties(aet_lio_core PROPERTIES
  IMPORTED_LOCATION ${PROJECT_SOURCE_DIR}/lib/libaet_lio_core.so
)

# ============================================================
# wrapper 节点
# ============================================================

add_executable(aet_lio_node
  src/aet_lio_node.cpp
)

add_dependencies(aet_lio_node
  ${${PROJECT_NAME}_EXPORTED_TARGETS}
  ${catkin_EXPORTED_TARGETS}
)

target_link_libraries(aet_lio_node
  aet_lio_core
  ${catkin_LIBRARIES}
  ${PCL_LIBRARIES}
)

# 让运行时能找到包内 lib/libaet_lio_core.so
set_target_properties(aet_lio_node PROPERTIES
  BUILD_RPATH ${PROJECT_SOURCE_DIR}/lib
  INSTALL_RPATH ${PROJECT_SOURCE_DIR}/lib
)
