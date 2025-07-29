import pytest
from pathlib import Path
from unittest import mock

from r2pb.converter import Converter
from r2pb.parser import ParsedMsg, Field


def test_converter_basic(tmp_path: Path):
    """Test converting a single message with dependencies."""
    # 1. Setup: Mock parser and generator
    mock_parser = mock.Mock()
    mock_generator = mock.Mock()

    # Mock data for 'my_pkg/MyMessage'
    my_message_parsed = ParsedMsg(
        fields=[Field(name="header", field_type="std_msgs/Header")], constants=[]
    )
    my_message_proto = (
        'syntax = "proto3"; package my_pkg; import "std_msgs/Header.proto"; message MyMessage { std_msgs.Header header = 1; }',
        ["std_msgs/Header"],
    )

    # Mock data for 'std_msgs/Header' based on real definition
    header_parsed = ParsedMsg(
        fields=[
            Field(name="seq", field_type="uint32"),
            Field(name="stamp", field_type="time"),
            Field(name="frame_id", field_type="string"),
        ],
        constants=[],
    )
    header_proto = (
        'syntax = "proto3"; package std_msgs; import "google/protobuf/timestamp.proto"; message Header { uint32 seq = 1; google.protobuf.Timestamp stamp = 2; string frame_id = 3; }',
        [],
    )

    # Configure mocks
    mock_parser.parse.side_effect = lambda pkg, msg: (
        my_message_parsed
        if (pkg, msg) == ("my_pkg", "MyMessage")
        else header_parsed if (pkg, msg) == ("std_msgs", "Header") else None
    )

    mock_generator.generate_proto.side_effect = lambda parsed, **kwargs: (
        my_message_proto
        if parsed == my_message_parsed
        else header_proto if parsed == header_parsed else ("", [])
    )

    # 2. Execution: Run the converter
    output_dir = tmp_path / "proto_out"
    converter = Converter()
    converter._parser = mock_parser
    converter._generator = mock_generator

    converter.convert("my_pkg/MyMessage", output_dir)

    # 3. Verification
    # Check that parser and generator were called correctly
    assert mock_parser.parse.call_count == 2
    mock_parser.parse.assert_any_call("my_pkg", "MyMessage")
    mock_parser.parse.assert_any_call("std_msgs", "Header")

    assert mock_generator.generate_proto.call_count == 2

    # Check that files were written correctly
    my_message_file = output_dir / "my_pkg" / "MyMessage.proto"
    header_file = output_dir / "std_msgs" / "Header.proto"
    assert my_message_file.exists()
    assert header_file.exists()
    assert my_message_file.read_text() == my_message_proto[0]
    assert header_file.read_text() == header_proto[0]


def test_converter_failure(tmp_path: Path, capsys):
    """Test that the converter handles failures gracefully."""
    mock_parser = mock.Mock()
    mock_generator = mock.Mock()

    # 'bad_pkg/BadMessage' will fail to parse
    mock_parser.parse.side_effect = ValueError("File not found")

    output_dir = tmp_path / "proto_out"
    converter = Converter()
    converter._parser = mock_parser
    converter._generator = mock_generator

    # Run conversion, expecting it to fail
    with pytest.raises(ValueError, match="File not found"):
        converter.convert("bad_pkg/BadMessage", output_dir)

    # Check that an error message was printed and no files were created
    captured = capsys.readouterr()
    assert "Failed to convert bad_pkg/BadMessage" in captured.out
    assert not (output_dir / "bad_pkg").exists()
