````markdown
# Money-kills- 💰

## Forex Trading Bot - EURUSD & XAUUSD

An advanced automated Forex trading bot designed for currency pairs and commodities. Features market analysis, technical indicators, and automatic order execution with risk management.

### 🎯 Features

#### Trading Symbols
- **EURUSD** - Euro/US Dollar
- **XAUUSD** - Gold/US Dollar

#### Risk Management
- **Lot Size**: 0.01 (Micro lot)
- **Stop Loss**: 5 points
- **Take Profit**: 1:3 Ratio (3x the SL distance)
- **Automatic Order Execution**: Based on market conditions
- **Position Monitoring**: Real-time tracking of active positions

#### Technical Indicators
- **SMA (Simple Moving Average)** - 20 and 50 period trends
- **RSI (Relative Strength Index)** - Overbought/Oversold detection
- **MACD** - Momentum and trend confirmation
- **Bollinger Bands** - Volatility and price extremes
- **Price Action** - Support/Resistance analysis

#### Automated Features
- **Market Analysis**: Continuous analysis every 5 minutes
- **Signal Generation**: Multi-indicator confirmation (requires 2+ signals)
- **Order Placement**: Automatic execution with SL/TP
- **Position Management**: Real-time monitoring and logging
- **Risk Assessment**: Account balance checks before trading

### 📋 Commands & Usage

#### Start Trading Bot
```bash
python forex_trading_bot.py
```

#### Run Backtest
```bash
python backtest.py
```

### ⚙️ Configuration

Edit `config.py` to customize:

```python
# Trading Symbols
SYMBOLS = ['EURUSD', 'XAUUSD']

# Risk Management
LOT_SIZE = 0.01      # Micro lot
SL_POINTS = 5        # Stop Loss in points
TP_RATIO = 3         # Take Profit ratio (1:3)

# Technical Analysis
TIMEFRAME = 5        # 5-minute candles

# Account Management
MIN_BALANCE = 100    # Minimum account balance
```

### 🔧 Installation

#### Prerequisites
- Python 3.8+
- MetaTrader 5 installed and running
- Active trading account

#### Setup Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/manusharbidhar-rgb/Money-kills-.git
   cd Money-kills-
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Bot**
   - Copy and edit `config.py` with your settings
   - Ensure MetaTrader 5 is running with your account

5. **Run Bot**
   ```bash
   python forex_trading_bot.py
   ```

### 📊 Trading Logic

#### Signal Generation
The bot analyzes the market using multiple indicators:

1. **SMA Crossover**
   - BUY: SMA20 > SMA50 (Uptrend)
   - SELL: SMA20 < SMA50 (Downtrend)

2. **RSI Analysis**
   - BUY Signal: RSI < 30 (Oversold)
   - SELL Signal: RSI > 70 (Overbought)

3. **MACD Analysis**
   - BUY: MACD Bullish Crossover
   - SELL: MACD Bearish Crossover

4. **Bollinger Bands**
   - BUY: Price below lower band
   - SELL: Price above upper band

#### Order Execution
- **Confidence Threshold**: Minimum 50% (2+ signals required)
- **Entry Price**: Market price at signal confirmation
- **Stop Loss**: Current price ± 5 points (based on direction)
- **Take Profit**: SL × 3 (1:3 Risk-Reward Ratio)

### 📈 Performance Metrics

The bot tracks:
- Win Rate
- Profit/Loss
- Sharpe Ratio
- Total Trades Executed
- Average Trade Duration

### 🔍 Logging

All trading activity is logged to `trading_bot.log`:
- Market analysis results
- Trading signals generated
- Order placements and executions
- Profit/Loss updates
- Error handling

### 📁 Project Structure

```
Money-kills-/
├── forex_trading_bot.py      # Main trading bot
├── backtest.py               # Backtesting module
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── trading_bot.log          # Trading logs (generated)
├── .gitignore               # Git ignore file
└── README.md                # This file
```

### 🎓 Indicator Settings

```python
# SMA
SMA_FAST = 20      # Fast moving average
SMA_SLOW = 50      # Slow moving average

# RSI
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# MACD
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands
BB_PERIOD = 20
BB_STD_DEV = 2     # Standard deviations
```

### ⚠️ Risk Disclaimer

- This bot trades with REAL money on LIVE accounts
- Past performance does not guarantee future results
- Forex trading involves substantial risk
- You can lose more than your initial investment
- Test extensively on a demo account first
- Adjust risk parameters for your risk tolerance

### 🚀 Future Enhancements

- [ ] Multiple timeframe analysis
- [ ] Advanced hedging strategies
- [ ] Sentiment analysis integration
- [ ] Machine learning models
- [ ] News impact detection
- [ ] Advanced risk management
- [ ] Performance analytics dashboard
- [ ] Email/SMS notifications
- [ ] Telegram bot integration
- [ ] Web interface

### 📞 Support & Contribution

For issues, suggestions, or improvements:
- Open an issue on [GitHub](https://github.com/manusharbidhar-rgb/Money-kills-/issues)
- Submit pull requests for enhancements

### 📜 License

This project is open source under the MIT License.

### ⚡ Quick Start

```bash
# 1. Setup
git clone https://github.com/manusharbidhar-rgb/Money-kills-.git
cd Money-kills-
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
# Edit config.py with your settings

# 3. Test
python backtest.py

# 4. Trade
python forex_trading_bot.py
```

---

**Trade Smart, Risk Smart! 🎯💵**

Built with ❤️ for profitable trading
````