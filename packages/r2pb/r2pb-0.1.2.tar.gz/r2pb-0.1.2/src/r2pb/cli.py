import argparse
import sys
import traceback
from .converter import Converter
from git import GitCommandError


def main():
    """Main function for the r2pb command-line interface."""
    parser = argparse.ArgumentParser(
        description="r2pb: ROS .msg to Protobuf .proto converter."
    )
    parser.add_argument(
        "msg_type",
        type=str,
        help="The ROS message type to convert (e.g., std_msgs/String).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default=".",
        help="The directory where the .proto files will be saved.",
    )
    parser.add_argument(
        "-d",
        "--ros-distro",
        type=str,
        default="noetic",
        help="The ROS distribution to use (e.g., noetic, melodic).",
    )

    args = parser.parse_args()

    print(f"Converting {args.msg_type} for ROS {args.ros_distro}...")
    print(f"Output directory: {args.output_dir}")

    try:
        converter = Converter(ros_distro=args.ros_distro)
        converter.convert(args.msg_type, args.output_dir)
        print("\nConversion finished successfully.")
    except GitCommandError as e:
        print(f"\nGit command failed: {e}", file=sys.stderr)
        print(
            "Please ensure that Git is installed and accessible in your system's PATH.",
            file=sys.stderr,
        )
        print("Conversion failed.", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print(f"\nAn unexpected error occurred during conversion:", file=sys.stderr)
        traceback.print_exc()
        print("Conversion failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
