from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MessageRequest(_message.Message):
    __slots__ = ("prompt", "uuid")
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    prompt: str
    uuid: str
    def __init__(self, prompt: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class MessageResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
