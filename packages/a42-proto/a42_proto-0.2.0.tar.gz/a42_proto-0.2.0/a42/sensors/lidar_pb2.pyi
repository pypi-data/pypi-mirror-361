from a42.common import calibration_pb2 as _calibration_pb2
from a42.label import object_pb2 as _object_pb2
from a42.data import pointcloud_pb2 as _pointcloud_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LaserName(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_NAME: _ClassVar[LaserName]
    WIM_HOR: _ClassVar[LaserName]
    ANPR_HOR: _ClassVar[LaserName]
    AMPEL_HOR: _ClassVar[LaserName]
    WIM_VER: _ClassVar[LaserName]
    ANPR_VER: _ClassVar[LaserName]
    AMPEL_VER: _ClassVar[LaserName]
    CLASS_QB2: _ClassVar[LaserName]
    CLASS_OS0: _ClassVar[LaserName]
    CLASS_AERIES_II: _ClassVar[LaserName]
UNKNOWN_NAME: LaserName
WIM_HOR: LaserName
ANPR_HOR: LaserName
AMPEL_HOR: LaserName
WIM_VER: LaserName
ANPR_VER: LaserName
AMPEL_VER: LaserName
CLASS_QB2: LaserName
CLASS_OS0: LaserName
CLASS_AERIES_II: LaserName

class LidarScan(_message.Message):
    __slots__ = ("laser_name", "scan_timestamp_ns", "pointcloud", "calibration", "object_list")
    LASER_NAME_FIELD_NUMBER: _ClassVar[int]
    SCAN_TIMESTAMP_NS_FIELD_NUMBER: _ClassVar[int]
    POINTCLOUD_FIELD_NUMBER: _ClassVar[int]
    CALIBRATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_LIST_FIELD_NUMBER: _ClassVar[int]
    laser_name: LaserName
    scan_timestamp_ns: int
    pointcloud: _pointcloud_pb2.PointCloud
    calibration: _calibration_pb2.SensorCalibration
    object_list: _object_pb2.ObjectList
    def __init__(self, laser_name: _Optional[_Union[LaserName, str]] = ..., scan_timestamp_ns: _Optional[int] = ..., pointcloud: _Optional[_Union[_pointcloud_pb2.PointCloud, _Mapping]] = ..., calibration: _Optional[_Union[_calibration_pb2.SensorCalibration, _Mapping]] = ..., object_list: _Optional[_Union[_object_pb2.ObjectList, _Mapping]] = ...) -> None: ...
