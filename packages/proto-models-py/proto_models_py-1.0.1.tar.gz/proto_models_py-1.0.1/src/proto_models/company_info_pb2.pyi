from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CompanyInfo(_message.Message):
    __slots__ = ["name", "address", "city", "state", "country", "zip", "website", "logo", "description", "symbol", "exchange", "industry", "ceo", "sector", "employees", "keyStats"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    ZIP_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_FIELD_NUMBER: _ClassVar[int]
    LOGO_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    CEO_FIELD_NUMBER: _ClassVar[int]
    SECTOR_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEES_FIELD_NUMBER: _ClassVar[int]
    KEYSTATS_FIELD_NUMBER: _ClassVar[int]
    name: str
    address: str
    city: str
    state: str
    country: str
    zip: str
    website: str
    logo: str
    description: str
    symbol: str
    exchange: str
    industry: str
    ceo: str
    sector: str
    employees: int
    keyStats: KeyStats
    def __init__(self, name: _Optional[str] = ..., address: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., country: _Optional[str] = ..., zip: _Optional[str] = ..., website: _Optional[str] = ..., logo: _Optional[str] = ..., description: _Optional[str] = ..., symbol: _Optional[str] = ..., exchange: _Optional[str] = ..., industry: _Optional[str] = ..., ceo: _Optional[str] = ..., sector: _Optional[str] = ..., employees: _Optional[int] = ..., keyStats: _Optional[_Union[KeyStats, _Mapping]] = ...) -> None: ...

class KeyStats(_message.Message):
    __slots__ = ["marketCap", "sharesOutstanding", "beta", "week52Change", "sharesShort", "sharesShortPriorMonth", "dividendAmount", "earningsDates", "eps", "peRatio", "forwardPE", "revenue", "pegRatio", "roe", "ebitda", "netIncome", "profitMargin", "debtToEquity", "freeCashFlow", "grossMargin"]
    MARKETCAP_FIELD_NUMBER: _ClassVar[int]
    SHARESOUTSTANDING_FIELD_NUMBER: _ClassVar[int]
    BETA_FIELD_NUMBER: _ClassVar[int]
    WEEK52CHANGE_FIELD_NUMBER: _ClassVar[int]
    SHARESSHORT_FIELD_NUMBER: _ClassVar[int]
    SHARESSHORTPRIORMONTH_FIELD_NUMBER: _ClassVar[int]
    DIVIDENDAMOUNT_FIELD_NUMBER: _ClassVar[int]
    EARNINGSDATES_FIELD_NUMBER: _ClassVar[int]
    EPS_FIELD_NUMBER: _ClassVar[int]
    PERATIO_FIELD_NUMBER: _ClassVar[int]
    FORWARDPE_FIELD_NUMBER: _ClassVar[int]
    REVENUE_FIELD_NUMBER: _ClassVar[int]
    PEGRATIO_FIELD_NUMBER: _ClassVar[int]
    ROE_FIELD_NUMBER: _ClassVar[int]
    EBITDA_FIELD_NUMBER: _ClassVar[int]
    NETINCOME_FIELD_NUMBER: _ClassVar[int]
    PROFITMARGIN_FIELD_NUMBER: _ClassVar[int]
    DEBTTOEQUITY_FIELD_NUMBER: _ClassVar[int]
    FREECASHFLOW_FIELD_NUMBER: _ClassVar[int]
    GROSSMARGIN_FIELD_NUMBER: _ClassVar[int]
    marketCap: float
    sharesOutstanding: float
    beta: float
    week52Change: float
    sharesShort: float
    sharesShortPriorMonth: float
    dividendAmount: float
    earningsDates: _containers.RepeatedScalarFieldContainer[str]
    eps: float
    peRatio: float
    forwardPE: float
    revenue: float
    pegRatio: float
    roe: float
    ebitda: float
    netIncome: float
    profitMargin: float
    debtToEquity: float
    freeCashFlow: float
    grossMargin: float
    def __init__(self, marketCap: _Optional[float] = ..., sharesOutstanding: _Optional[float] = ..., beta: _Optional[float] = ..., week52Change: _Optional[float] = ..., sharesShort: _Optional[float] = ..., sharesShortPriorMonth: _Optional[float] = ..., dividendAmount: _Optional[float] = ..., earningsDates: _Optional[_Iterable[str]] = ..., eps: _Optional[float] = ..., peRatio: _Optional[float] = ..., forwardPE: _Optional[float] = ..., revenue: _Optional[float] = ..., pegRatio: _Optional[float] = ..., roe: _Optional[float] = ..., ebitda: _Optional[float] = ..., netIncome: _Optional[float] = ..., profitMargin: _Optional[float] = ..., debtToEquity: _Optional[float] = ..., freeCashFlow: _Optional[float] = ..., grossMargin: _Optional[float] = ...) -> None: ...

class CompanyInfoRequest(_message.Message):
    __slots__ = ["symbol"]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class CompanyInfoResponse(_message.Message):
    __slots__ = ["companyInfo"]
    COMPANYINFO_FIELD_NUMBER: _ClassVar[int]
    companyInfo: CompanyInfo
    def __init__(self, companyInfo: _Optional[_Union[CompanyInfo, _Mapping]] = ...) -> None: ...
