import unittest
from unittest.mock import patch, MagicMock
from r2pb import cli


class TestCli(unittest.TestCase):

    @patch("r2pb.cli.Converter")
    @patch("r2pb.cli.argparse.ArgumentParser.parse_args")
    def test_main_flow(self, mock_parse_args, mock_converter_class):
        """Test the main CLI flow with mocked arguments and converter."""
        # Arrange: Mock the parsed arguments
        mock_args = MagicMock()
        mock_args.msg_type = "std_msgs/String"
        mock_args.output_dir = "/tmp/proto_test"
        mock_args.ros_distro = "noetic"
        mock_parse_args.return_value = mock_args

        # Arrange: Mock the Converter instance and its methods
        mock_converter_instance = MagicMock()
        mock_converter_class.return_value = mock_converter_instance

        # Act: Call the main function
        cli.main()

        # Assert: Check if Converter was initialized and called correctly
        mock_converter_class.assert_called_once_with(ros_distro="noetic")
        mock_converter_instance.convert.assert_called_once_with(
            "std_msgs/String", "/tmp/proto_test"
        )


if __name__ == "__main__":
    unittest.main()
