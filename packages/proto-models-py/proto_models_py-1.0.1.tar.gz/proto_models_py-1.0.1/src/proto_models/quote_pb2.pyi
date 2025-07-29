from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Quote(_message.Message):
    __slots__ = ["symbol", "quote", "quotes"]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUOTE_FIELD_NUMBER: _ClassVar[int]
    QUOTES_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quote: QuoteData
    quotes: _containers.RepeatedCompositeFieldContainer[QuoteData]
    def __init__(self, symbol: _Optional[str] = ..., quote: _Optional[_Union[QuoteData, _Mapping]] = ..., quotes: _Optional[_Iterable[_Union[QuoteData, _Mapping]]] = ...) -> None: ...

class QuoteData(_message.Message):
    __slots__ = ["symbol", "price", "price_change", "price_change_percent", "bid", "ask", "volume", "day_high", "day_low", "year_high", "year_low"]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    PRICE_CHANGE_FIELD_NUMBER: _ClassVar[int]
    PRICE_CHANGE_PERCENT_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    ASK_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    DAY_HIGH_FIELD_NUMBER: _ClassVar[int]
    DAY_LOW_FIELD_NUMBER: _ClassVar[int]
    YEAR_HIGH_FIELD_NUMBER: _ClassVar[int]
    YEAR_LOW_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    price: float
    price_change: float
    price_change_percent: float
    bid: float
    ask: float
    volume: float
    day_high: float
    day_low: float
    year_high: float
    year_low: float
    def __init__(self, symbol: _Optional[str] = ..., price: _Optional[float] = ..., price_change: _Optional[float] = ..., price_change_percent: _Optional[float] = ..., bid: _Optional[float] = ..., ask: _Optional[float] = ..., volume: _Optional[float] = ..., day_high: _Optional[float] = ..., day_low: _Optional[float] = ..., year_high: _Optional[float] = ..., year_low: _Optional[float] = ...) -> None: ...
