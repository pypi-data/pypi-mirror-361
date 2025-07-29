from pathlib import Path
from typing import List, Dict, Any
from jinja2 import Environment, PackageLoader, select_autoescape
from .parser import ParsedMsg, Field, Constant, MsgParser  # 引入 MsgParser
from .mapper import map_ros_to_proto_type


class ProtoField:
    """Represents a field in the Protobuf message."""

    def __init__(self, name: str, proto_type: str, package: str = ""):
        self.name = name
        self.proto_type = proto_type
        self.package = package


class ProtoGenerator:
    """Generates .proto files from ROS message definitions."""

    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("r2pb", "templates"), autoescape=select_autoescape()
        )
        self.template = self.env.get_template("msg.proto.j2")

    def _collect_dependencies(self, fields: List[Field]) -> List[str]:
        """Collects required dependencies based on field types."""
        dependencies = set()
        for field in fields:
            if "/" in field.field_type:
                dependencies.add(field.field_type)
        return sorted(list(dependencies))

    def _convert_fields(self, fields: List[Field]) -> List[ProtoField]:
        """Converts ROS message fields to Protobuf fields."""
        proto_fields = []
        for field in fields:
            package = ""
            ros_type = field.field_type
            if "/" in ros_type:
                package, ros_type = ros_type.split("/", 1)

            proto_fields.append(
                ProtoField(
                    name=field.name,
                    proto_type=map_ros_to_proto_type(field.field_type),
                    package=package,
                )
            )
        return proto_fields

    def generate_proto(
        self, parsed_msg: ParsedMsg, package_name: str, msg_name: str
    ) -> (str, List[str]):
        """Generates a .proto file content for a given ROS message."""
        proto_fields = self._convert_fields(parsed_msg.fields)
        dependencies = self._collect_dependencies(parsed_msg.fields)

        # 从依赖项生成导入语句
        imports = sorted([f"{dep}.proto" for dep in dependencies])

        proto_content = self.template.render(
            package_name=package_name,
            msg_name=msg_name,
            fields=proto_fields,
            constants=parsed_msg.constants,
            imports=imports,
        )
        return proto_content, dependencies
