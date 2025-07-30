from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class TaskState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_STATE_UNSPECIFIED: _ClassVar[TaskState]
    TASK_STATE_IN_MISSING_PRECONDITION: _ClassVar[TaskState]
    TASK_STATE_IN_WAITING: _ClassVar[TaskState]
    TASK_STATE_IN_PROGRESS: _ClassVar[TaskState]
    TASK_STATE_COMPLETED: _ClassVar[TaskState]
    TASK_STATE_ERROR: _ClassVar[TaskState]
TASK_STATE_UNSPECIFIED: TaskState
TASK_STATE_IN_MISSING_PRECONDITION: TaskState
TASK_STATE_IN_WAITING: TaskState
TASK_STATE_IN_PROGRESS: TaskState
TASK_STATE_COMPLETED: TaskState
TASK_STATE_ERROR: TaskState
