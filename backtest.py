"""
Backtesting module for Forex Trading Bot
Test trading strategy on historical data
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from config import SYMBOLS, LOT_SIZE, SL_POINTS, TP_RATIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BacktestEngine:
    def __init__(self, symbols, start_date, end_date, timeframe=5):
        """Initialize backtest engine."""
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        self.results = {}
        
    def initialize(self):
        """Initialize MetaTrader 5."""
        if not mt5.initialize():
            logger.error("Failed to initialize MT5")
            return False
        return True
    
    def get_historical_data(self, symbol):
        """Get historical data for backtesting."""
        try:
            rates = mt5.copy_rates_range(symbol, self.timeframe, self.start_date, self.end_date)
            if rates is None:
                logger.error(f"Failed to get historical data for {symbol}")
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            return None
    
    def run_backtest(self):
        """Run backtest on all symbols."""
        if not self.initialize():
            return
        
        try:
            for symbol in self.symbols:
                logger.info(f"Backtesting {symbol}...")
                df = self.get_historical_data(symbol)
                
                if df is None or len(df) < 100:
                    logger.warning(f"Insufficient data for {symbol}")
                    continue
                
                # Calculate indicators
                df['sma_20'] = df['close'].rolling(window=20).mean()
                df['sma_50'] = df['close'].rolling(window=50).mean()
                
                # Generate signals
                df['signal'] = 0
                df.loc[df['sma_20'] > df['sma_50'], 'signal'] = 1  # BUY
                df.loc[df['sma_20'] < df['sma_50'], 'signal'] = -1  # SELL
                
                # Calculate returns
                df['returns'] = df['close'].pct_change()
                df['strategy_returns'] = df['signal'].shift(1) * df['returns']
                
                # Calculate metrics
                total_return = (df['strategy_returns'].sum() * 100)
                win_rate = len(df[df['strategy_returns'] > 0]) / len(df) * 100
                sharpe_ratio = df['strategy_returns'].mean() / df['strategy_returns'].std() * np.sqrt(252)
                
                self.results[symbol] = {
                    'total_return': total_return,
                    'win_rate': win_rate,
                    'sharpe_ratio': sharpe_ratio,
                    'trades': len(df[df['signal'] != 0])
                }
                
                logger.info(f"{symbol} Results:")
                logger.info(f"  Total Return: {total_return:.2f}%")
                logger.info(f"  Win Rate: {win_rate:.2f}%")
                logger.info(f"  Sharpe Ratio: {sharpe_ratio:.2f}")
        
        finally:
            mt5.shutdown()

if __name__ == '__main__':
    # Example: Backtest last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    backtest = BacktestEngine(SYMBOLS, start_date, end_date)
    backtest.run_backtest()
