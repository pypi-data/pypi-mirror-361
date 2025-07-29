# r2pb 开发计划与技术路线图

## 1. 项目目标 (Project Goal)

创建一个健壮、可独立部署的 Python 库，名为 `r2pb` (ROS to Protobuf)。其核心功能是**自动将 ROS 1 和 ROS 2 的消息定义文件 (`.msg`) 转换为 Protobuf 的消息定义文件 (`.proto`)**。该库旨在解耦 `tSim` 与 ROS 消息的具体实现，并能服务于 `tStudio` 及其他任何需要进行类似转换的生态系统项目。

## 2. 核心功能划分 (Feature Breakdown)

- **消息发现 (Message Discovery)**: 
  - **本地搜索**: 能够根据给定的 ROS 包名或工作区路径，自动搜索并定位所有的 `.msg` 文件。
  - **(新) 在线获取与缓存 (Online Fetch & Cache)**: 当本地无法找到指定的 ROS 消息包时，从预设的远程代码仓库（如 GitHub 的 `ros/common_msgs`）按需下载，并缓存到本地用户目录 (`~/.cache/r2pb`) 中，避免重复下载。
- **消息解析 (Message Parsing)**: 精确解析 `.msg` 文件的内容，包括字段名、数据类型、数组类型、常量和注释。
- **类型映射 (Type Mapping)**: 维护一个可配置的 ROS 类型到 Protobuf 类型的映射表 (例如 `string` -> `string`, `float64` -> `double`, `Header` -> `google.protobuf.Timestamp` 等)。
- **依赖处理 (Dependency Handling)**: 自动解析 `.msg` 文件之间的依赖关系，并在生成的 `.proto` 文件中添加正确的 `import` 语句。
- **代码生成 (Code Generation)**: 基于解析和映射的结果，使用模板引擎生成格式规范、可读性强的 `.proto` 文件。
- **双重接口 (Dual Interface)**:
  - **命令行接口 (CLI)**: 提供一个简单的命令行工具，方便用户快速转换整个包或单个文件。
  - **Python API**: 提供一个简洁的 Python 函数接口，方便 `tSim` 等项目进行程序化调用。

## 3. 技术栈 (Technology Stack)

- **开发语言**: Python 3.8+
- **HTTP 请求**: `requests` 或 `httpx` (用于在线获取功能)
- **代码生成**: `Jinja2` (模板引擎)
- **命令行接口**: `Typer` 或 `Click`
- **代码风格**: `Black` (格式化), `Ruff` (Linter)
- **测试框架**: `pytest`
- **打包与分发**: `pyproject.toml` (使用 `hatch` 或 `setuptools`), 发布到 PyPI
- **持续集成**: GitHub Actions (自动化测试与发布)

## 4. 架构设计 (Architecture)

- `r2pb/`
  - `parser.py`: 负责查找和解析 `.msg` 文件。
  - `fetcher.py`: **(新)** 实现从远程仓库下载和缓存 `.msg` 文件的逻辑。
  - `mapper.py`: 定义 ROS 类型到 Protobuf 类型的映射规则。
  - `generator.py`: 接收解析后的数据结构，利用 `Jinja2` 模板生成最终的 `.proto` 文件字符串。
  - `cli.py`: 实现命令行接口。
  - `api.py`: 暴露公共的 Python API。
  - `templates/`: 存放 `.proto` 文件的 `Jinja2` 模板。

## 5. 分阶段开发路线图 (Phased Roadmap)

**阶段一: 核心转换引擎 (ROS 1)**
- **目标**: 实现针对单个 ROS 1 `.msg` 文件的基本转换功能。
- **任务**:
  1.  初始化项目结构，配置 `pyproject.toml` 和 `pytest`。
  2.  实现 `parser.py`，能够解析单个 `.msg` 文件（不处理依赖）。
  3.  在 `mapper.py` 中定义基础类型映射规则。
  4.  创建基础的 `.proto.j2` 模板。
  5.  实现 `generator.py`，将解析结果渲染为 `.proto` 文件内容。
  6.  为核心模块编写单元测试。

**阶段二: 包级转换与在线获取**
- **目标**: 支持转换整个 ROS 1 包，并集成在线获取功能。
- **任务**:
  1.  扩展 `parser.py` 以支持递归搜索 ROS 包。
  2.  **(新)** 实现 `fetcher.py`，能够从 GitHub 下载并缓存标准的 ROS 消息包。
  3.  在 `parser.py` 中集成 `fetcher`，实现“本地找不到则在线查找”的逻辑。
  4.  在 `generator.py` 中实现依赖处理逻辑，自动添加 `import` 语句。
  5.  编写集成测试，覆盖在线获取和包转换的场景。

**阶段三: CLI、API 与 ROS 2 支持**
- **目标**: 提供完整的用户接口并扩展对 ROS 2 的支持。
- **任务**:
  1.  使用 `Typer` 开发 `cli.py`，提供 `r2pb convert <package_name>` 命令。
  2.  在 `api.py` 中正式定义并实现 `convert_package()` 等公共函数。
  3.  研究并实现对 ROS 2 `.msg` 文件的解析和获取。
  4.  在 CLI 中增加 `--ros-version` 标志来区分 ROS 1 和 ROS 2。
  5.  编写详细的 `README.md`。

**阶段四: 打包、发布与文档**
- **目标**: 将 `r2pb` 打包成一个高质量的 Python 库并公开发布。
- **任务**:
  1.  配置 GitHub Actions，实现自动化测试 (CI)。
  2.  配置 `pyproject.toml` 以便打包和发布到 PyPI。
  3.  创建并发布 `r2pb` 的第一个正式版本。