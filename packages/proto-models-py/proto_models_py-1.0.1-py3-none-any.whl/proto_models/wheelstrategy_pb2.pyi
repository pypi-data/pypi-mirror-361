from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OptionRecommendation(_message.Message):
    __slots__ = ["option_symbol", "option_type", "strike_price", "expiration_date", "premium", "delta", "open_interest", "status", "score"]
    OPTION_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    OPTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRIKE_PRICE_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    PREMIUM_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    YIELD_FIELD_NUMBER: _ClassVar[int]
    option_symbol: str
    option_type: str
    strike_price: float
    expiration_date: _timestamp_pb2.Timestamp
    premium: float
    delta: float
    open_interest: float
    status: str
    score: float
    def __init__(self, option_symbol: _Optional[str] = ..., option_type: _Optional[str] = ..., strike_price: _Optional[float] = ..., expiration_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., premium: _Optional[float] = ..., delta: _Optional[float] = ..., open_interest: _Optional[float] = ..., status: _Optional[str] = ..., score: _Optional[float] = ..., **kwargs) -> None: ...

class ScoredOption(_message.Message):
    __slots__ = ["option_symbol", "strike_price", "expiration_date", "premium", "delta", "open_interest", "score"]
    OPTION_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    STRIKE_PRICE_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    PREMIUM_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    YIELD_FIELD_NUMBER: _ClassVar[int]
    option_symbol: str
    strike_price: float
    expiration_date: _timestamp_pb2.Timestamp
    premium: float
    delta: float
    open_interest: float
    score: float
    def __init__(self, option_symbol: _Optional[str] = ..., strike_price: _Optional[float] = ..., expiration_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., premium: _Optional[float] = ..., delta: _Optional[float] = ..., open_interest: _Optional[float] = ..., score: _Optional[float] = ..., **kwargs) -> None: ...

class StrategyRecommendation(_message.Message):
    __slots__ = ["symbol", "rsi", "note", "call_recommendation", "put_recommendation", "all_scored_calls", "all_scored_puts", "stock_price"]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    RSI_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    CALL_RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    PUT_RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    ALL_SCORED_CALLS_FIELD_NUMBER: _ClassVar[int]
    ALL_SCORED_PUTS_FIELD_NUMBER: _ClassVar[int]
    STOCK_PRICE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    rsi: float
    note: str
    call_recommendation: OptionRecommendation
    put_recommendation: OptionRecommendation
    all_scored_calls: _containers.RepeatedCompositeFieldContainer[ScoredOption]
    all_scored_puts: _containers.RepeatedCompositeFieldContainer[ScoredOption]
    stock_price: float
    def __init__(self, symbol: _Optional[str] = ..., rsi: _Optional[float] = ..., note: _Optional[str] = ..., call_recommendation: _Optional[_Union[OptionRecommendation, _Mapping]] = ..., put_recommendation: _Optional[_Union[OptionRecommendation, _Mapping]] = ..., all_scored_calls: _Optional[_Iterable[_Union[ScoredOption, _Mapping]]] = ..., all_scored_puts: _Optional[_Iterable[_Union[ScoredOption, _Mapping]]] = ..., stock_price: _Optional[float] = ...) -> None: ...

class StrategyRecommendations(_message.Message):
    __slots__ = ["recommendations", "note"]
    RECOMMENDATIONS_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    recommendations: _containers.RepeatedCompositeFieldContainer[StrategyRecommendation]
    note: str
    def __init__(self, recommendations: _Optional[_Iterable[_Union[StrategyRecommendation, _Mapping]]] = ..., note: _Optional[str] = ...) -> None: ...
