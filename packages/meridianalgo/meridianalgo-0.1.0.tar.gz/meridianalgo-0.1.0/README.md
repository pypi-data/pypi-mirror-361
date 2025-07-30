# MeridianAlgo

A comprehensive Python library for algorithmic trading and financial analysis. MeridianAlgo provides tools for backtesting trading strategies, calculating technical indicators, and managing trading operations.

## Features

- **Trading Engine**: Live trading operations and position management
- **Backtest Engine**: Historical strategy testing with performance metrics
- **Technical Indicators**: Comprehensive collection of technical analysis indicators
- **Utility Functions**: Risk management and performance calculation tools

## Installation

### From PyPI (when published)
```bash
pip install meridianalgo
```

### From Source
```bash
git clone https://github.com/yourusername/meridianalgo.git
cd meridianalgo
pip install -e .
```

## Quick Start

### Basic Usage

```python
import pandas as pd
from meridianalgo import TradingEngine, BacktestEngine, Indicators, TradeUtils

# Initialize trading engine
engine = TradingEngine(paper_trading=True)
engine.connect()

# Get account information
account_info = engine.get_account_info()
print(f"Account Balance: {account_info['balance']}")

# Place a trade
order = engine.place_order(
    symbol="BTC/USD",
    side="buy",
    quantity=0.1,
    order_type="market"
)
print(f"Order placed: {order}")
```

### Backtesting a Strategy

```python
# Load historical data
data = pd.read_csv('historical_data.csv')
data['timestamp'] = pd.to_datetime(data['timestamp'])

# Initialize backtest engine
backtest = BacktestEngine(initial_capital=10000)

# Load data
backtest.load_data(data)

# Define a simple moving average crossover strategy
def ma_crossover_strategy(row, positions, capital, fast_period=10, slow_period=20):
    """Simple moving average crossover strategy"""
    if len(backtest.data) < slow_period:
        return None
    
    # Calculate moving averages
    fast_ma = backtest.data['close'].rolling(fast_period).mean().iloc[-1]
    slow_ma = backtest.data['close'].rolling(slow_period).mean().iloc[-1]
    
    current_price = row['close']
    
    # Buy signal: fast MA crosses above slow MA
    if fast_ma > slow_ma and 'BTC/USD' not in positions:
        quantity = capital * 0.1 / current_price  # Use 10% of capital
        return {
            'symbol': 'BTC/USD',
            'action': 'buy',
            'quantity': quantity
        }
    
    # Sell signal: fast MA crosses below slow MA
    elif fast_ma < slow_ma and 'BTC/USD' in positions:
        return {
            'symbol': 'BTC/USD',
            'action': 'sell',
            'quantity': positions['BTC/USD']['quantity']
        }
    
    return None

# Run backtest
results = backtest.run_backtest(ma_crossover_strategy)
print(f"Total Return: {results['total_return']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
```

### Using Technical Indicators

```python
# Calculate RSI
rsi = Indicators.rsi(data['close'], period=14)

# Calculate MACD
macd_line, signal_line, histogram = Indicators.macd(data['close'])

# Calculate Bollinger Bands
upper_band, middle_band, lower_band = Indicators.bollinger_bands(data['close'])

# Calculate Stochastic Oscillator
k_percent, d_percent = Indicators.stochastic(
    data['high'], 
    data['low'], 
    data['close']
)
```

### Risk Management

```python
# Calculate position size based on risk
position_size = TradeUtils.calculate_position_size(
    capital=10000,
    risk_percent=2,  # Risk 2% of capital
    entry_price=50000,
    stop_loss=48000
)

# Calculate risk-reward ratio
rr_ratio = TradeUtils.calculate_risk_reward_ratio(
    entry_price=50000,
    target_price=55000,
    stop_loss=48000
)

# Calculate P&L
pnl = TradeUtils.calculate_pnl(
    entry_price=50000,
    exit_price=52000,
    quantity=0.1,
    side="long"
)
```

## Documentation

For detailed documentation, visit [https://meridianalgo.readthedocs.io/](https://meridianalgo.readthedocs.io/)

## API Reference

### TradingEngine

Main class for live trading operations.

```python
engine = TradingEngine(api_key="your_api_key", paper_trading=True)
```

**Methods:**
- `connect()`: Connect to trading platform
- `get_account_info()`: Get account information
- `place_order()`: Place a trading order
- `get_positions()`: Get current positions
- `get_trade_history()`: Get trade history
- `calculate_pnl()`: Calculate profit/loss

### BacktestEngine

Class for backtesting trading strategies.

```python
backtest = BacktestEngine(initial_capital=10000)
```

**Methods:**
- `load_data()`: Load historical data
- `run_backtest()`: Run backtest with strategy
- `get_equity_curve()`: Get equity curve data
- `get_trades()`: Get trade data

### Indicators

Static methods for technical analysis indicators.

**Available Indicators:**
- `sma()`: Simple Moving Average
- `ema()`: Exponential Moving Average
- `rsi()`: Relative Strength Index
- `macd()`: MACD
- `bollinger_bands()`: Bollinger Bands
- `stochastic()`: Stochastic Oscillator
- `atr()`: Average True Range
- `williams_r()`: Williams %R
- `cci()`: Commodity Channel Index

### TradeUtils

Utility functions for trading operations.

**Available Functions:**
- `calculate_position_size()`: Calculate position size based on risk
- `calculate_risk_reward_ratio()`: Calculate risk-reward ratio
- `calculate_pnl()`: Calculate profit/loss
- `calculate_sharpe_ratio()`: Calculate Sharpe ratio
- `calculate_max_drawdown()`: Calculate maximum drawdown
- `calculate_win_rate()`: Calculate win rate
- `format_currency()`: Format currency amounts
- `validate_trade_params()`: Validate trade parameters

## Examples

See the `examples/` directory for more detailed examples:

- `simple_strategy.py`: Basic moving average strategy
- `rsi_strategy.py`: RSI-based trading strategy
- `risk_management.py`: Risk management examples
- `performance_analysis.py`: Performance analysis examples

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=meridianalgo tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This library is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.

## Support

- Documentation: [https://meridianalgo.readthedocs.io/](https://meridianalgo.readthedocs.io/)
- Issues: [https://github.com/yourusername/meridianalgo/issues](https://github.com/yourusername/meridianalgo/issues)
- Email: your.email@example.com

## Changelog

### Version 0.1.0
- Initial release
- Basic trading engine functionality
- Backtesting engine with performance metrics
- Technical indicators collection
- Utility functions for risk management 