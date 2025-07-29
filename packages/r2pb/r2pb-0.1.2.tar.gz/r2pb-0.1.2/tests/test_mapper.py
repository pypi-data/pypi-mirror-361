import pytest
from r2pb.mapper import map_ros_to_proto_type


@pytest.mark.parametrize(
    "ros_type, proto_type",
    [
        ("string", "string"),
        ("int32", "int32"),
        ("uint64", "uint64"),
        ("float32", "float"),
        ("time", "google.protobuf.Timestamp"),
        ("std_msgs/Header", "Header"),
        ("geometry_msgs/Pose", "Pose"),
    ],
)
def test_map_ros_to_proto_type(ros_type, proto_type):
    """Tests mapping of various ROS types to Protobuf types."""
    assert map_ros_to_proto_type(ros_type) == proto_type
