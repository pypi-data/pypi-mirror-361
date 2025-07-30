from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LidarPoint(_message.Message):
    __slots__ = ("x", "y", "z", "intensity", "timestamp_offset_ns")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    INTENSITY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_OFFSET_NS_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    intensity: float
    timestamp_offset_ns: int
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ..., intensity: _Optional[float] = ..., timestamp_offset_ns: _Optional[int] = ...) -> None: ...

class PointCloud(_message.Message):
    __slots__ = ("points",)
    POINTS_FIELD_NUMBER: _ClassVar[int]
    points: _containers.RepeatedCompositeFieldContainer[LidarPoint]
    def __init__(self, points: _Optional[_Iterable[_Union[LidarPoint, _Mapping]]] = ...) -> None: ...
