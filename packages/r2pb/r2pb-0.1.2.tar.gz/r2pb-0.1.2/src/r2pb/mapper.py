# A mapping from ROS built-in types to Protobuf types
ROS_TO_PROTO_TYPE_MAP = {
    "bool": "bool",
    "byte": "int32",  # Protobuf doesn't have a byte type, int32 is a common choice
    "char": "string",  # Protobuf doesn't have a char type, string is a common choice
    "float32": "float",
    "float64": "double",
    "int8": "int32",
    "uint8": "uint32",
    "int16": "int32",
    "uint16": "uint32",
    "int32": "int32",
    "uint32": "uint32",
    "int64": "int64",
    "uint64": "uint64",
    "string": "string",
    # Special ROS types
    "time": "google.protobuf.Timestamp",
    "duration": "google.protobuf.Duration",
}


def map_ros_to_proto_type(ros_type: str) -> str:
    """Maps a ROS type to its corresponding Protobuf type."""
    if ros_type in ROS_TO_PROTO_TYPE_MAP:
        return ROS_TO_PROTO_TYPE_MAP[ros_type]
    # For complex types (e.g., other messages), we assume they will be
    # converted to a message of the same name in the same package.
    # We will handle package path resolution later.
    return ros_type.split("/")[-1]
