"""
Configuration file for Forex Trading Bot
"""

# Trading Symbols
SYMBOLS = ['EURUSD', 'XAUUSD']

# Risk Management
LOT_SIZE = 0.01  # Micro lot
SL_POINTS = 5    # Stop Loss in points
TP_RATIO = 3     # Take Profit to Stop Loss ratio (1:3)

# Technical Analysis
TIMEFRAME = 5    # 5-minute timeframe (use mt5.TIMEFRAME_M5 for actual connection)

# Account Management
MIN_BALANCE = 100  # Minimum balance to trade

# Trading Hours (24-hour format)
START_HOUR = 0
END_HOUR = 24

# Maximum orders per symbol
MAX_ORDERS_PER_SYMBOL = 1

# Order Management
DEVIATION = 20  # Deviation for order execution
MAGIC_NUMBER = 234000

# Indicator Settings
SMA_FAST = 20
SMA_SLOW = 50
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD_DEV = 2

# Logging
LOG_FILE = 'trading_bot.log'
LOG_LEVEL = 'INFO'

# Risk Parameters
RISK_PERCENTAGE = 1  # Risk 1% of account per trade
MAX_DAILY_LOSS = 5   # Maximum loss per day in percentage

print(f"Trading Bot Configuration Loaded")
print(f"Symbols: {SYMBOLS}")
print(f"Lot Size: {LOT_SIZE}")
print(f"Stop Loss: {SL_POINTS} points")
print(f"Take Profit Ratio: 1:{TP_RATIO}")