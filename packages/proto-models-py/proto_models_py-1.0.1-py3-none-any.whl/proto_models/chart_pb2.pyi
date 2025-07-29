from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Yearly(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    BY_DAY: _ClassVar[Yearly]
    BY_WEEK: _ClassVar[Yearly]
    BY_MONTH: _ClassVar[Yearly]
BY_DAY: Yearly
BY_WEEK: Yearly
BY_MONTH: Yearly

class History(_message.Message):
    __slots__ = ["symbol", "candles"]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    CANDLES_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    candles: _containers.RepeatedCompositeFieldContainer[Candle]
    def __init__(self, symbol: _Optional[str] = ..., candles: _Optional[_Iterable[_Union[Candle, _Mapping]]] = ...) -> None: ...

class Candle(_message.Message):
    __slots__ = ["date_time", "open", "close", "high", "low", "volume"]
    DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    date_time: int
    open: float
    close: float
    high: float
    low: float
    volume: float
    def __init__(self, date_time: _Optional[int] = ..., open: _Optional[float] = ..., close: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., volume: _Optional[float] = ...) -> None: ...
