# r2pb

[![Python package](https://github.com/tz-bb/r2pb/actions/workflows/python-package.yml/badge.svg)](https://github.com/tz-bb/r2pb/actions/workflows/python-package.yml)
[![PyPI version](https://img.shields.io/pypi/v/r2pb.svg)](https://pypi.org/project/r2pb/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/r2pb.svg)](https://pypi.org/project/r2pb/)
[![PyPI - License](https://img.shields.io/pypi/l/r2pb.svg)](https://github.com/tz-bb/r2pb/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# r2pb - ROS .msg to Protobuf .proto Converter

`r2pb` 是一个功能强大且易于使用的命令行工具和 Python 库，用于将 ROS (Robot Operating System) 的 `.msg` 文件转换为 Google 的 Protobuf (`.proto`) 文件。它支持从本地文件系统或远程 Git 仓库（如 GitHub）自动获取 ROS 包。

## 特性

- **CLI 和库两种使用方式**: 提供 `r2pb` 命令行工具用于快速转换，也提供 Python API (`r2pb.Converter`) 用于在代码中集成。
- **自动获取依赖**: 能够自动从 GitHub 等远程 Git 仓库克隆 ROS 包及其依赖项。
- **本地缓存**: 将获取的包缓存在本地 (`~/.cache/r2pb`)，加快后续转换速度。
- **灵活的输出控制**: 用户可以指定输出目录来存放生成的 `.proto` 文件。
- **跨平台**: 可在 Windows, macOS 和 Linux 上运行。

## 安装

通过 pip 从 PyPI 安装：

```bash
pip install r2pb
```
或者，如果你想从源码安装并进行开发：

```
git clone https://github.com/tz-bb/r2pb.git
cd r2pb
pip install -e .
```
或

```
pip install git+https://github.com/tz-bb/r2pb.git
```

## 使用方法
### 命令行接口 (CLI)
CLI 是使用 r2pb 的最简单方式。基本语法如下：

```
r2pb <package_name/message_name> [options]
```
示例：

1. 转换单个消息
   
   将 std_msgs 包中的 String 消息转换为 .proto 文件，并保存到 generated_protos 目录：
   
   ```
   r2pb std_msgs/String -o generated_protos
   ```
   执行后， generated_protos/std_msgs/ 目录下会生成 String.proto 文件。
2.  **[TODO]** 转换整个包
   
   未来版本将支持转换一个包中的所有消息。
选项:

- -o, --output-dir <directory> : 指定存放生成文件的输出目录。默认为当前目录下的 generated_protos 。
- --ros-distro <distro> : **[TODO]**指定 ROS 发行版（如 noetic , humble ），用于查找正确的包版本。默认为 noetic 。
### Python API
你也可以在 Python 代码中使用 r2pb 的 Converter 类来实现更复杂的逻辑。

示例：

```
from r2pb import Converter

# 初始化转换器
converter = Converter()

# 定义输出目录
output_dir = "my_protos"

# 转换 std_msgs/String
# convert 方法在成功时返回 True，失败时会抛出异常
try:
    success = converter.convert(["std_msgs/String"], output_dir)
    if success:
        print(f"Successfully converted messages and saved to {output_dir}")
except Exception as e:
    print(f"An error occurred: {e}")

```
## 工作原理
1. 解析输入 : r2pb 首先解析你提供的消息名称，如 std_msgs/String 。
2. 查找包 : 它会在本地缓存中查找 std_msgs 包。如果找不到，它会使用 rosdistro 数据库来定位包的远程 Git 仓库。
3. 获取包 : r2pb 会克隆仓库到本地缓存目录 ( ~/.cache/r2pb )。
4. 解析消息文件 : 它会读取 .msg 文件的内容，分析其字段和类型。
5. 类型映射 : r2pb 会将 ROS 的内置类型（如 string , int32 , Header ）映射到对应的 Protobuf 类型（如 string , int32 , Timestamp ）。
6. 生成 .proto 文件 : 最后，它使用模板生成 .proto 文件，包含正确的 syntax , package 定义和消息结构。
## 贡献
欢迎任何形式的贡献！如果你发现了 bug、有功能建议或想改进代码，请随时提交 Pull Request 或创建 Issue。

## 许可证
本项目基于 GNU AGPLv3 发布。