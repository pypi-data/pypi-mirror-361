from common.v1 import agent_pb2 as _agent_pb2
from common.v1 import property_pb2 as _property_pb2
from tracker.v1 import tracker_pb2 as _tracker_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigurationMessage(_message.Message):
    __slots__ = ("instance_id", "id", "name", "description", "agents", "trackers", "properties")
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    TRACKERS_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    instance_id: str
    id: str
    name: str
    description: str
    agents: _containers.RepeatedCompositeFieldContainer[_agent_pb2.Agent]
    trackers: _containers.RepeatedCompositeFieldContainer[_tracker_pb2.Tracker]
    properties: _containers.RepeatedCompositeFieldContainer[_property_pb2.Property]
    def __init__(self, instance_id: _Optional[str] = ..., id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., agents: _Optional[_Iterable[_Union[_agent_pb2.Agent, _Mapping]]] = ..., trackers: _Optional[_Iterable[_Union[_tracker_pb2.Tracker, _Mapping]]] = ..., properties: _Optional[_Iterable[_Union[_property_pb2.Property, _Mapping]]] = ...) -> None: ...

class LoadConfigurationMessage(_message.Message):
    __slots__ = ("id", "instance_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    instance_id: str
    def __init__(self, id: _Optional[str] = ..., instance_id: _Optional[str] = ...) -> None: ...

class AddConfigurationMessage(_message.Message):
    __slots__ = ("name", "description", "template_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    template_id: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., template_id: _Optional[str] = ...) -> None: ...
