from pathlib import Path
from collections import deque
from typing import List, Set

from .parser import MsgParser
from .generator import ProtoGenerator


class Converter:
    """The main class for converting ROS messages to Protobuf files."""

    def __init__(self, ros_distro: str = "noetic"):
        # self._parser = MsgParser(ros_distro=ros_distro)
        self._parser = MsgParser()
        self._generator = ProtoGenerator()
        self._processed_messages = set()

    def convert(self, top_level_msg_type: str, output_dir: str):
        """
        Converts a top-level ROS message and its dependencies to .proto.

        Args:
            top_level_msg_type: The top-level message to convert (e.g., 'std_msgs/String').
            output_dir: The directory where .proto files will be saved.
        """
        output_path = Path(output_dir)
        queue = deque([top_level_msg_type])

        while queue:
            msg_type = queue.popleft()
            if msg_type in self._processed_messages:
                continue

            print(f"Processing {msg_type}...")
            try:
                package_name, msg_name = msg_type.split("/")
                parsed_msg = self._parser.parse(package_name, msg_name)

                proto_content, dependencies = self._generator.generate_proto(
                    parsed_msg, package_name=package_name, msg_name=msg_name
                )

                self._write_proto_file(
                    output_path, package_name, msg_name, proto_content
                )

                for dep in dependencies:
                    if dep not in self._processed_messages:
                        queue.append(dep)

                self._processed_messages.add(msg_type)
                print(f"Successfully converted {msg_type}")

            except Exception as e:
                print(f"Failed to convert {msg_type}: {e}")
                # Re-raise the exception to halt the entire conversion process
                raise

    def _write_proto_file(
        self, output_dir: Path, package_name: str, msg_name: str, content: str
    ):
        """Writes the .proto content to the appropriate file."""
        package_dir = output_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)
        file_path = package_dir / f"{msg_name}.proto"
        file_path.write_text(content, encoding="utf-8")
        print(f"Wrote {file_path}")
