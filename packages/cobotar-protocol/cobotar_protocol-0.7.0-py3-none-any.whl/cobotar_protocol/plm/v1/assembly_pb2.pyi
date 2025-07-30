from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskStateRequest(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_STATE_REQUEST_UNSPECIFIED: _ClassVar[TaskStateRequest]
    TASK_STATE_REQUEST_IN_PROGRESS: _ClassVar[TaskStateRequest]
    TASK_STATE_REQUEST_COMPLETED: _ClassVar[TaskStateRequest]
    TASK_STATE_REQUEST_UNDO: _ClassVar[TaskStateRequest]
    TASK_STATE_REQUEST_ERROR: _ClassVar[TaskStateRequest]
TASK_STATE_REQUEST_UNSPECIFIED: TaskStateRequest
TASK_STATE_REQUEST_IN_PROGRESS: TaskStateRequest
TASK_STATE_REQUEST_COMPLETED: TaskStateRequest
TASK_STATE_REQUEST_UNDO: TaskStateRequest
TASK_STATE_REQUEST_ERROR: TaskStateRequest

class LoadProcessMessage(_message.Message):
    __slots__ = ("request_id", "process_id", "location_id")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PROCESS_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    process_id: str
    location_id: str
    def __init__(self, request_id: _Optional[str] = ..., process_id: _Optional[str] = ..., location_id: _Optional[str] = ...) -> None: ...

class ReassignTaskMessage(_message.Message):
    __slots__ = ("request_id", "task_id", "assignee")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEE_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    task_id: str
    assignee: str
    def __init__(self, request_id: _Optional[str] = ..., task_id: _Optional[str] = ..., assignee: _Optional[str] = ...) -> None: ...

class UpdateTaskStateMessage(_message.Message):
    __slots__ = ("request_id", "task_id", "state")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    task_id: str
    state: TaskStateRequest
    def __init__(self, request_id: _Optional[str] = ..., task_id: _Optional[str] = ..., state: _Optional[_Union[TaskStateRequest, str]] = ...) -> None: ...
