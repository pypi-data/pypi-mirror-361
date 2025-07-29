import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, NamedTuple, Optional, Union

from .fetcher import RosMsgFetcher


class Field(NamedTuple):
    field_type: str
    name: str


class Constant(NamedTuple):
    const_type: str
    name: str
    value: Any


class ParsedMsg(NamedTuple):
    fields: List[Field]
    constants: List[Constant]


def parse_msg_content(content: str) -> ParsedMsg:
    """Parses the content of a .msg file into a structured format."""
    fields = []
    constants = []

    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        # Ignore comments and empty lines
        if not line or line.startswith("#"):
            continue

        # Split comments from the definition
        if "#" in line:
            line = line.split("#", 1)[0].strip()

        # Check for constants
        if "=" in line:
            parts = [p.strip() for p in line.split("=", 1)]
            const_def, const_val = parts
            const_type, const_name = const_def.split()
            constants.append(Constant(const_type, const_name, const_val))
        # Check for fields
        else:
            parts = line.split()
            if len(parts) >= 2:
                field_type, field_name = parts[:2]
                fields.append(Field(field_type, field_name))

    return ParsedMsg(fields=fields, constants=constants)


class MsgParser:
    """ROS 消息文件解析器，支持本地搜索和在线获取。"""

    def __init__(self, local_package_paths: Optional[List[Union[str, Path]]] = None):
        self.local_package_paths = (
            [Path(p) for p in local_package_paths] if local_package_paths else []
        )
        self.fetcher = RosMsgFetcher()

    def find_msg_file_content(self, package_name: str, msg_name: str) -> str:
        """查找指定的消息文件内容，优先在本地搜索，找不到则尝试在线获取。

        Args:
            package_name: ROS 包名，如 'std_msgs'。
            msg_name: 消息名称，如 'String' (不带 .msg 后缀)。

        Returns:
            消息文件的文本内容。

        Raises:
            FileNotFoundError: 当消息文件无法在本地和在线仓库中找到时。
        """
        # 1. 先在本地包路径中查找
        content = self._find_local_msg_content(package_name, msg_name)
        if content is not None:
            return content

        # 2. 本地找不到，尝试在线获取
        try:
            package_path = self.fetcher.find_and_fetch(package_name)
            msg_file_path = self._find_msg_in_package(package_path, msg_name)
            if msg_file_path:
                return msg_file_path.read_text(encoding="utf-8")
        except (KeyError, FileNotFoundError):
            # 捕获 fetcher 找不到包或文件找不到的异常，统一处理
            pass

        raise FileNotFoundError(
            f"Message '{msg_name}.msg' not found in package '{package_name}' "
            f"(searched in {self.local_package_paths} and online)"
        )

    def _find_local_msg_content(
        self, package_name: str, msg_name: str
    ) -> Optional[str]:
        """在配置的本地路径中查找消息文件并返回其内容。"""
        for base_path in self.local_package_paths:
            # 假设的目录结构: base_path / package_name / msg / msg_name.msg
            msg_file = base_path / package_name / "msg" / f"{msg_name}.msg"
            if msg_file.is_file():
                return msg_file.read_text(encoding="utf-8")
        return None

    def _find_msg_in_package(self, package_path: Path, msg_name: str) -> Optional[Path]:
        """在给定的包路径下查找 .msg 文件。"""
        # ROS 标准结构是在包目录下的 'msg' 子目录中
        msg_file = package_path / "msg" / f"{msg_name}.msg"
        if msg_file.is_file():
            return msg_file

        # 有些包可能直接把 .msg 文件放在根目录
        msg_file_root = package_path / f"{msg_name}.msg"
        if msg_file_root.is_file():
            return msg_file_root

        return None

    def parse(self, package_name: str, msg_name: str) -> ParsedMsg:
        """查找并解析一个消息文件。

        这是推荐使用的主方法，它封装了查找和解析的整个过程。
        """
        content = self.find_msg_file_content(package_name, msg_name)
        return parse_msg_content(content)
