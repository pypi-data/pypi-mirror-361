import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from r2pb.parser import parse_msg_content, ParsedMsg, Field, Constant, MsgParser

# --- Tests for the original parse_msg_content function ---


def test_parse_simple_msg():
    """Tests parsing of a simple .msg file content."""
    content = """
# This is a comment
string name
int32 age

# Constants
string FOO = bar
int32 BAZ = 123

"""
    expected = ParsedMsg(
        fields=[
            Field(field_type="string", name="name"),  # 修改这里：type -> field_type
            Field(field_type="int32", name="age"),  # 修改这里：type -> field_type
        ],
        constants=[
            Constant(
                const_type="string", name="FOO", value="bar"
            ),  # 注意：这里也要用 const_type
            Constant(
                const_type="int32", name="BAZ", value="123"
            ),  # 注意：这里也要用 const_type
        ],
    )
    assert parse_msg_content(content) == expected


def test_parse_complex_msg():
    """Tests parsing of a .msg file with complex types."""
    content = """
# A complex message
std_msgs/Header header
geometry_msgs/Pose pose
string child_frame_id
"""
    expected = ParsedMsg(
        fields=[
            Field(field_type="std_msgs/Header", name="header"),
            Field(field_type="geometry_msgs/Pose", name="pose"),
            Field(field_type="string", name="child_frame_id"),
        ],
        constants=[],
    )
    assert parse_msg_content(content) == expected


# --- Tests for the new MsgParser class ---


@pytest.fixture
def mock_fetcher(monkeypatch):
    """Mock the RosMsgFetcher to simulate online fetching."""
    mock_fetcher_instance = MagicMock()
    # Use patch to replace the class in the parser module
    with patch(
        "r2pb.parser.RosMsgFetcher", return_value=mock_fetcher_instance
    ) as mock_class:
        yield mock_fetcher_instance


@pytest.fixture
def local_packages(tmp_path):
    """Create a dummy local package structure."""
    local_path = tmp_path / "ros_ws"
    local_path.mkdir()

    # Create a package: my_msgs
    my_msgs_path = local_path / "my_msgs" / "msg"
    my_msgs_path.mkdir(parents=True)
    (my_msgs_path / "MyData.msg").write_text("string data")

    return local_path


def test_parser_find_local_file(local_packages):
    """Test finding a message file from a local path."""
    parser = MsgParser(local_package_paths=[local_packages])
    content = parser.find_msg_file_content("my_msgs", "MyData")
    assert content == "string data"


def test_parser_local_file_not_found(local_packages):
    """Test that FileNotFoundError is raised if a local file is not found."""
    parser = MsgParser(local_package_paths=[local_packages])
    with pytest.raises(FileNotFoundError):
        # This should fail because we don't mock the fetcher, so online lookup also fails
        parser.find_msg_file_content("my_msgs", "NonExistent")


def test_parser_fetch_online_when_not_local(mock_fetcher, tmp_path):
    """Test that the parser attempts to fetch online if not found locally."""
    # Simulate the fetcher returning a path to a 'downloaded' package
    online_pkg_path = tmp_path / "online_pkgs" / "std_msgs"
    (online_pkg_path / "msg").mkdir(parents=True)
    (online_pkg_path / "msg" / "String.msg").write_text("string data")
    mock_fetcher.find_and_fetch.return_value = online_pkg_path

    # Initialize parser with no local paths
    parser = MsgParser(local_package_paths=[])
    content = parser.find_msg_file_content("std_msgs", "String")

    # Verify that fetcher was called and content is correct
    mock_fetcher.find_and_fetch.assert_called_once_with("std_msgs")
    assert content == "string data"


def test_parser_fetch_online_fails(mock_fetcher):
    """Test that FileNotFoundError is raised when online fetch fails."""
    # Simulate a failure in the fetcher
    mock_fetcher.find_and_fetch.side_effect = KeyError("Package not found")

    parser = MsgParser()
    with pytest.raises(
        FileNotFoundError, match="not found in package 'non_existent_pkg'"
    ):
        parser.find_msg_file_content("non_existent_pkg", "SomeMsg")


def test_parser_parse_method(mock_fetcher, tmp_path):
    """Test the main 'parse' method which integrates finding and parsing."""
    # Setup a fetched file
    online_pkg_path = tmp_path / "online_pkgs" / "sensor_msgs"
    (online_pkg_path / "msg").mkdir(parents=True)
    (online_pkg_path / "msg" / "Imu.msg").write_text(
        "std_msgs/Header header\nint32 data"
    )
    mock_fetcher.find_and_fetch.return_value = online_pkg_path

    parser = MsgParser()
    parsed_result = parser.parse("sensor_msgs", "Imu")

    expected = ParsedMsg(
        fields=[
            Field(field_type="std_msgs/Header", name="header"),
            Field(field_type="int32", name="data"),
        ],
        constants=[],
    )
    assert parsed_result == expected


def test_parser_online_repo_exists_but_msg_is_missing(mock_fetcher, tmp_path):
    """测试当远程仓库成功获取，但里面没有所需的 .msg 文件时的情况。"""
    # 1. 模拟 fetcher 成功返回了一个包的路径
    online_pkg_path = tmp_path / "online_pkgs" / "std_msgs"
    online_pkg_path.mkdir(parents=True)
    # 2. **但是**，我们故意不在这个路径下创建 'String.msg' 文件

    mock_fetcher.find_and_fetch.return_value = online_pkg_path

    parser = MsgParser()

    # 3. 断言：即使仓库找到了，但因为最终找不到文件，仍然应该抛出 FileNotFoundError
    with pytest.raises(
        FileNotFoundError, match="'String.msg' not found in package 'std_msgs'"
    ):
        parser.find_msg_file_content("std_msgs", "String")

    # 验证 fetcher 确实被调用了
    mock_fetcher.find_and_fetch.assert_called_once_with("std_msgs")
