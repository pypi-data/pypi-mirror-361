
# volg

A Python package for calculating option Greeks and implied volatility.

## Installation

```bash
pip install volg
```

## Features

- Calculate implied volatility (IV) using binary search method
- Compute option Greeks (Delta, Gamma, Vega, Theta, etc.)
- Calculate exposures (Delta exposure, Gamma exposure, etc.)
- Support for both call and put options

## Usage

```python
import volg

# Calculate implied volatility
iv = volg.greek.iv(spot_price, strike_price, interest_rate, days_to_expiry, option_price, flag='C')

# Calculate Greeks
greeks = volg.greek.greeks(spot_price, strike_price, interest_rate, days_to_expiry, option_price, flag='C')

# Process a dataframe with option data
df = volg.greek.compute_greeks_vectorized(df)
df = volg.greek.compute_exposure(df)
```

### Alternative import style:

```python
from volg import greek

# Calculate implied volatility
iv = greek.iv(spot_price, strike_price, interest_rate, days_to_expiry, option_price, flag='C')

# Calculate implied volatility using vectorized method on df columns
df['iv'] = greek.iv_vectorized(df['sfut_price'], df['strike_price'], 0, df['dte'], df['close_ce'], flag='C')

# Calculate Greeks
greeks = greek.greeks(spot_price, strike_price, interest_rate, days_to_expiry, option_price, flag='C')


#Option to calculate greeks in vectorized on dataframe
column_mapping = {
    "sfut_price": "future_price",
    "strike_price": "strike_price",
    "dte": "dte",
    "count": "count",
    "ce_ltp": "close_ce",
    "pe_ltp": "close_pe"
}

greek_df = greek.compute_greeks_vectorized(df, columns=column_mapping)

```

## License

MIT License
