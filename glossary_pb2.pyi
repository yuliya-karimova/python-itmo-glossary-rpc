from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TermRequest(_message.Message):
    __slots__ = ("term_name",)
    TERM_NAME_FIELD_NUMBER: _ClassVar[int]
    term_name: str
    def __init__(self, term_name: _Optional[str] = ...) -> None: ...

class RelationsRequest(_message.Message):
    __slots__ = ("term_name", "max_depth")
    TERM_NAME_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    term_name: str
    max_depth: int
    def __init__(self, term_name: _Optional[str] = ..., max_depth: _Optional[int] = ...) -> None: ...

class PathRequest(_message.Message):
    __slots__ = ("source_term", "target_term", "max_depth")
    SOURCE_TERM_FIELD_NUMBER: _ClassVar[int]
    TARGET_TERM_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    source_term: str
    target_term: str
    max_depth: int
    def __init__(self, source_term: _Optional[str] = ..., target_term: _Optional[str] = ..., max_depth: _Optional[int] = ...) -> None: ...

class Term(_message.Message):
    __slots__ = ("name", "definition")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_FIELD_NUMBER: _ClassVar[int]
    name: str
    definition: str
    def __init__(self, name: _Optional[str] = ..., definition: _Optional[str] = ...) -> None: ...

class Relation(_message.Message):
    __slots__ = ("source_term", "target_term", "relation_type")
    SOURCE_TERM_FIELD_NUMBER: _ClassVar[int]
    TARGET_TERM_FIELD_NUMBER: _ClassVar[int]
    RELATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    source_term: str
    target_term: str
    relation_type: str
    def __init__(self, source_term: _Optional[str] = ..., target_term: _Optional[str] = ..., relation_type: _Optional[str] = ...) -> None: ...

class TermResponse(_message.Message):
    __slots__ = ("term", "found")
    TERM_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    term: Term
    found: bool
    def __init__(self, term: _Optional[_Union[Term, _Mapping]] = ..., found: bool = ...) -> None: ...

class RelationsResponse(_message.Message):
    __slots__ = ("relations", "total_count")
    RELATIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    relations: _containers.RepeatedCompositeFieldContainer[Relation]
    total_count: int
    def __init__(self, relations: _Optional[_Iterable[_Union[Relation, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class PathResponse(_message.Message):
    __slots__ = ("path", "path_exists", "message")
    PATH_FIELD_NUMBER: _ClassVar[int]
    PATH_EXISTS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    path: _containers.RepeatedScalarFieldContainer[str]
    path_exists: bool
    message: str
    def __init__(self, path: _Optional[_Iterable[str]] = ..., path_exists: bool = ..., message: _Optional[str] = ...) -> None: ...

class AllTermsResponse(_message.Message):
    __slots__ = ("terms", "total_count")
    TERMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    terms: _containers.RepeatedCompositeFieldContainer[Term]
    total_count: int
    def __init__(self, terms: _Optional[_Iterable[_Union[Term, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...
