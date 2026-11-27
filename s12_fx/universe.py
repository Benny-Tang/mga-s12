"""S12 FX/Gold/Index universe — 8 instruments, verified XM specs."""

INSTRUMENTS = {
    "GOLD":      {"yf": ["GC=F"], "type": "metal", "base": "XAU", "quote": "USD",
                  "contract_units": 100.0, "unit": "oz"},
    "SILVER":    {"yf": ["SI=F"], "type": "metal", "base": "XAG", "quote": "USD",
                  "contract_units": 5000.0, "unit": "oz"},
    "USDJPY":    {"yf": ["USDJPY=X"], "type": "fx", "base": "USD", "quote": "JPY",
                  "contract_units": 100_000.0, "unit": "base"},
    "EURUSD":    {"yf": ["EURUSD=X"], "type": "fx", "base": "EUR", "quote": "USD",
                  "contract_units": 100_000.0, "unit": "base"},
    "AUDUSD":    {"yf": ["AUDUSD=X"], "type": "fx", "base": "AUD", "quote": "USD",
                  "contract_units": 100_000.0, "unit": "base"},
    "GBPUSD":    {"yf": ["GBPUSD=X"], "type": "fx", "base": "GBP", "quote": "USD",
                  "contract_units": 100_000.0, "unit": "base"},
    "US30Cash":  {"yf": ["^DJI"], "type": "index", "base": "USD", "quote": "USD",
                  "contract_units": 1.0, "unit": "point"},
    "US500Cash": {"yf": ["^GSPC"], "type": "index", "base": "USD", "quote": "USD",
                  "contract_units": 1.0, "unit": "point"},
}
