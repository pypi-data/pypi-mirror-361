# AiEDA

## 介绍
面向python编程的EDA平台，集成iEDA等开源EDA工具的各类接口作为AiEDA开发引擎

### 修改iEDA third_party/iEDA/CMakelist.txt 以下参数
```Shell
option(BUILD_STATIC_LIB "If ON, build static lib." OFF)
option(BUILD_PYTHON "If ON, build python interface." ON)
```
### 编译iEDA，并install
```Shell
cd third_party/iEDA
mkdir build
cd build
cmake ..
make -j32 ieda_py
```
