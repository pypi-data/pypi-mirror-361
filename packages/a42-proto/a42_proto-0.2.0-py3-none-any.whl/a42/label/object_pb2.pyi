from a42.data import pointcloud_pb2 as _pointcloud_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Position(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class Dimensions(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class ObjectBBox(_message.Message):
    __slots__ = ("timestamp_ns", "position", "dimension", "pointcloud")
    TIMESTAMP_NS_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    DIMENSION_FIELD_NUMBER: _ClassVar[int]
    POINTCLOUD_FIELD_NUMBER: _ClassVar[int]
    timestamp_ns: int
    position: Position
    dimension: Dimensions
    pointcloud: _pointcloud_pb2.PointCloud
    def __init__(self, timestamp_ns: _Optional[int] = ..., position: _Optional[_Union[Position, _Mapping]] = ..., dimension: _Optional[_Union[Dimensions, _Mapping]] = ..., pointcloud: _Optional[_Union[_pointcloud_pb2.PointCloud, _Mapping]] = ...) -> None: ...

class ObjectList(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[ObjectBBox]
    def __init__(self, objects: _Optional[_Iterable[_Union[ObjectBBox, _Mapping]]] = ...) -> None: ...
