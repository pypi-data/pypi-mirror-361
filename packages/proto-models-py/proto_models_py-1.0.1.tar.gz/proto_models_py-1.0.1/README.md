# Proto Models Python Package

Generated Python protobuf models for trading and financial data.

## Installation

```bash
pip install proto-models-py
```

## Usage

```python
from proto_models import quote_pb2, company_info_pb2

# Create a quote object
quote = quote_pb2.Quote()
quote.symbol = "AAPL"
quote.quote.price = 150.25

# Serialize to bytes
data = quote.SerializeToString()

# Deserialize from bytes
new_quote = quote_pb2.Quote()
new_quote.ParseFromString(data)
```

## Available Models

- `chart_pb2` - Chart data models
- `company_info_pb2` - Company information models
- `option_chain_pb2` - Options chain models
- `quote_pb2` - Quote data models
- `wheelstrategy_pb2` - Wheel strategy models
