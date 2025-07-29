from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContractType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CALL: _ClassVar[ContractType]
    PUT: _ClassVar[ContractType]
CALL: ContractType
PUT: ContractType

class OptionChain(_message.Message):
    __slots__ = ["symbol", "underlying", "calls", "puts", "interval", "isDelayed", "isIndex", "numberOfContracts", "volatility", "expirations", "strikes", "status"]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    UNDERLYING_FIELD_NUMBER: _ClassVar[int]
    CALLS_FIELD_NUMBER: _ClassVar[int]
    PUTS_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    ISDELAYED_FIELD_NUMBER: _ClassVar[int]
    ISINDEX_FIELD_NUMBER: _ClassVar[int]
    NUMBEROFCONTRACTS_FIELD_NUMBER: _ClassVar[int]
    VOLATILITY_FIELD_NUMBER: _ClassVar[int]
    EXPIRATIONS_FIELD_NUMBER: _ClassVar[int]
    STRIKES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    underlying: Underlying
    calls: _containers.RepeatedCompositeFieldContainer[Contract]
    puts: _containers.RepeatedCompositeFieldContainer[Contract]
    interval: float
    isDelayed: bool
    isIndex: bool
    numberOfContracts: float
    volatility: float
    expirations: _containers.RepeatedScalarFieldContainer[str]
    strikes: _containers.RepeatedScalarFieldContainer[float]
    status: str
    def __init__(self, symbol: _Optional[str] = ..., underlying: _Optional[_Union[Underlying, _Mapping]] = ..., calls: _Optional[_Iterable[_Union[Contract, _Mapping]]] = ..., puts: _Optional[_Iterable[_Union[Contract, _Mapping]]] = ..., interval: _Optional[float] = ..., isDelayed: bool = ..., isIndex: bool = ..., numberOfContracts: _Optional[float] = ..., volatility: _Optional[float] = ..., expirations: _Optional[_Iterable[str]] = ..., strikes: _Optional[_Iterable[float]] = ..., status: _Optional[str] = ...) -> None: ...

class Underlying(_message.Message):
    __slots__ = ["ask", "askSize", "bid", "bidSize", "change", "close", "delayed", "description", "exchangeName", "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "highPrice", "last", "lowPrice", "mark", "markChange", "markPercentChange", "openPrice", "percentChange", "quoteTime", "totalVolume", "tradeTime", "volatility"]
    ASK_FIELD_NUMBER: _ClassVar[int]
    ASKSIZE_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    BIDSIZE_FIELD_NUMBER: _ClassVar[int]
    CHANGE_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    DELAYED_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXCHANGENAME_FIELD_NUMBER: _ClassVar[int]
    FIFTYTWOWEEKHIGH_FIELD_NUMBER: _ClassVar[int]
    FIFTYTWOWEEKLOW_FIELD_NUMBER: _ClassVar[int]
    HIGHPRICE_FIELD_NUMBER: _ClassVar[int]
    LAST_FIELD_NUMBER: _ClassVar[int]
    LOWPRICE_FIELD_NUMBER: _ClassVar[int]
    MARK_FIELD_NUMBER: _ClassVar[int]
    MARKCHANGE_FIELD_NUMBER: _ClassVar[int]
    MARKPERCENTCHANGE_FIELD_NUMBER: _ClassVar[int]
    OPENPRICE_FIELD_NUMBER: _ClassVar[int]
    PERCENTCHANGE_FIELD_NUMBER: _ClassVar[int]
    QUOTETIME_FIELD_NUMBER: _ClassVar[int]
    TOTALVOLUME_FIELD_NUMBER: _ClassVar[int]
    TRADETIME_FIELD_NUMBER: _ClassVar[int]
    VOLATILITY_FIELD_NUMBER: _ClassVar[int]
    ask: float
    askSize: float
    bid: float
    bidSize: float
    change: float
    close: float
    delayed: bool
    description: str
    exchangeName: str
    fiftyTwoWeekHigh: float
    fiftyTwoWeekLow: float
    highPrice: float
    last: float
    lowPrice: float
    mark: float
    markChange: float
    markPercentChange: float
    openPrice: float
    percentChange: float
    quoteTime: float
    totalVolume: float
    tradeTime: float
    volatility: float
    def __init__(self, ask: _Optional[float] = ..., askSize: _Optional[float] = ..., bid: _Optional[float] = ..., bidSize: _Optional[float] = ..., change: _Optional[float] = ..., close: _Optional[float] = ..., delayed: bool = ..., description: _Optional[str] = ..., exchangeName: _Optional[str] = ..., fiftyTwoWeekHigh: _Optional[float] = ..., fiftyTwoWeekLow: _Optional[float] = ..., highPrice: _Optional[float] = ..., last: _Optional[float] = ..., lowPrice: _Optional[float] = ..., mark: _Optional[float] = ..., markChange: _Optional[float] = ..., markPercentChange: _Optional[float] = ..., openPrice: _Optional[float] = ..., percentChange: _Optional[float] = ..., quoteTime: _Optional[float] = ..., totalVolume: _Optional[float] = ..., tradeTime: _Optional[float] = ..., volatility: _Optional[float] = ...) -> None: ...

class Contract(_message.Message):
    __slots__ = ["putCall", "strike", "currency", "lastPrice", "change", "percentChange", "openInterest", "bid", "ask", "contractSize", "expiration", "lastTradeDate", "impliedVolatility", "inTheMoney", "volume", "delta", "gamma", "theta", "vega", "rho", "timeValue", "dte"]
    PUTCALL_FIELD_NUMBER: _ClassVar[int]
    STRIKE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    LASTPRICE_FIELD_NUMBER: _ClassVar[int]
    CHANGE_FIELD_NUMBER: _ClassVar[int]
    PERCENTCHANGE_FIELD_NUMBER: _ClassVar[int]
    OPENINTEREST_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    ASK_FIELD_NUMBER: _ClassVar[int]
    CONTRACTSIZE_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    LASTTRADEDATE_FIELD_NUMBER: _ClassVar[int]
    IMPLIEDVOLATILITY_FIELD_NUMBER: _ClassVar[int]
    INTHEMONEY_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FIELD_NUMBER: _ClassVar[int]
    THETA_FIELD_NUMBER: _ClassVar[int]
    VEGA_FIELD_NUMBER: _ClassVar[int]
    RHO_FIELD_NUMBER: _ClassVar[int]
    TIMEVALUE_FIELD_NUMBER: _ClassVar[int]
    DTE_FIELD_NUMBER: _ClassVar[int]
    putCall: ContractType
    strike: float
    currency: str
    lastPrice: float
    change: float
    percentChange: float
    openInterest: float
    bid: float
    ask: float
    contractSize: str
    expiration: _timestamp_pb2.Timestamp
    lastTradeDate: float
    impliedVolatility: float
    inTheMoney: bool
    volume: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    timeValue: float
    dte: float
    def __init__(self, putCall: _Optional[_Union[ContractType, str]] = ..., strike: _Optional[float] = ..., currency: _Optional[str] = ..., lastPrice: _Optional[float] = ..., change: _Optional[float] = ..., percentChange: _Optional[float] = ..., openInterest: _Optional[float] = ..., bid: _Optional[float] = ..., ask: _Optional[float] = ..., contractSize: _Optional[str] = ..., expiration: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., lastTradeDate: _Optional[float] = ..., impliedVolatility: _Optional[float] = ..., inTheMoney: bool = ..., volume: _Optional[float] = ..., delta: _Optional[float] = ..., gamma: _Optional[float] = ..., theta: _Optional[float] = ..., vega: _Optional[float] = ..., rho: _Optional[float] = ..., timeValue: _Optional[float] = ..., dte: _Optional[float] = ...) -> None: ...

class OptionChainRequest(_message.Message):
    __slots__ = ["symbol"]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class OptionChainResponse(_message.Message):
    __slots__ = ["optionChain"]
    OPTIONCHAIN_FIELD_NUMBER: _ClassVar[int]
    optionChain: OptionChain
    def __init__(self, optionChain: _Optional[_Union[OptionChain, _Mapping]] = ...) -> None: ...
