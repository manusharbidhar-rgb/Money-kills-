#!/usr/bin/env python3
"""
Forex Trading Bot - EURUSD & XAUUSD
Automated trading bot with market analysis and technical indicators.
Supports automated order execution with SL/TP management.
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time
from config import SYMBOLS, LOT_SIZE, SL_POINTS, TP_RATIO, TIMEFRAME, MIN_BALANCE

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ForexTradingBot:
    def __init__(self):
        """Initialize the trading bot."""
        self.symbols = SYMBOLS
        self.lot_size = LOT_SIZE
        self.sl_points = SL_POINTS
        self.tp_ratio = TP_RATIO
        self.timeframe = TIMEFRAME
        self.min_balance = MIN_BALANCE
        self.active_orders = {}
        
    def initialize_mt5(self):
        """Initialize MetaTrader 5 connection."""
        try:
            if not mt5.initialize():
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            logger.info("MetaTrader 5 initialized successfully")
            account_info = mt5.account_info()
            logger.info(f"Account: {account_info.login} | Balance: ${account_info.balance:.2f}")
            return True
        except Exception as e:
            logger.error(f"Error initializing MT5: {str(e)}")
            return False
    
    def shutdown_mt5(self):
        """Shutdown MetaTrader 5 connection."""
        try:
            mt5.shutdown()
            logger.info("MetaTrader 5 shutdown successfully")
        except Exception as e:
            logger.error(f"Error shutting down MT5: {str(e)}")
    
    def get_market_data(self, symbol, bars=100):
        """Fetch market data for technical analysis."""
        try:
            rates = mt5.copy_rates_from_pos(symbol, self.timeframe, 0, bars)
            if rates is None:
                logger.error(f"Failed to get rates for {symbol}")
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {str(e)}")
            return None
    
    def calculate_sma(self, df, period=20):
        """Calculate Simple Moving Average."""
        return df['close'].rolling(window=period).mean()
    
    def calculate_rsi(self, df, period=14):
        """Calculate Relative Strength Index."""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        """Calculate MACD indicator."""
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, df, period=20, std_dev=2):
        """Calculate Bollinger Bands."""
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    def analyze_market(self, symbol):
        """Analyze market conditions using multiple indicators."""
        try:
            df = self.get_market_data(symbol, bars=100)
            if df is None or len(df) < 50:
                return None
            
            # Calculate indicators
            sma_20 = self.calculate_sma(df, 20)
            sma_50 = self.calculate_sma(df, 50)
            rsi = self.calculate_rsi(df)
            macd_line, signal_line, histogram = self.calculate_macd(df)
            upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(df)
            
            # Get current price
            current_price = df['close'].iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_macd_hist = histogram.iloc[-1]
            prev_macd_hist = histogram.iloc[-2]
            
            # Trend analysis
            sma_20_val = sma_20.iloc[-1]
            sma_50_val = sma_50.iloc[-1]
            
            analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'sma_20': sma_20_val,
                'sma_50': sma_50_val,
                'rsi': current_rsi,
                'macd_histogram': current_macd_hist,
                'macd_histogram_prev': prev_macd_hist,
                'upper_bb': upper_bb.iloc[-1],
                'lower_bb': lower_bb.iloc[-1],
                'timestamp': datetime.now()
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing market for {symbol}: {str(e)}")
            return None
    
    def determine_signal(self, analysis):
        """Determine trading signal based on analysis."""
        if analysis is None:
            return None
        
        signal = {
            'symbol': analysis['symbol'],
            'signal': None,
            'confidence': 0,
            'reason': []
        }
        
        price = analysis['current_price']
        sma_20 = analysis['sma_20']
        sma_50 = analysis['sma_50']
        rsi = analysis['rsi']
        macd_hist = analysis['macd_histogram']
        macd_hist_prev = analysis['macd_histogram_prev']
        
        buy_signals = 0
        sell_signals = 0
        
        # SMA Crossover
        if sma_20 > sma_50:
            buy_signals += 1
            signal['reason'].append('SMA20 > SMA50 (Uptrend)')
        else:
            sell_signals += 1
            signal['reason'].append('SMA20 < SMA50 (Downtrend)')
        
        # RSI Analysis
        if rsi < 30:
            buy_signals += 1
            signal['reason'].append('RSI < 30 (Oversold)')
        elif rsi > 70:
            sell_signals += 1
            signal['reason'].append('RSI > 70 (Overbought)')
        
        # MACD Analysis
        if macd_hist > 0 and macd_hist_prev <= 0:
            buy_signals += 1
            signal['reason'].append('MACD Bullish Crossover')
        elif macd_hist < 0 and macd_hist_prev >= 0:
            sell_signals += 1
            signal['reason'].append('MACD Bearish Crossover')
        
        # Price Position
        if price < analysis['lower_bb']:
            buy_signals += 1
            signal['reason'].append('Price Below Lower Bollinger Band')
        elif price > analysis['upper_bb']:
            sell_signals += 1
            signal['reason'].append('Price Above Upper Bollinger Band')
        
        # Determine final signal
        if buy_signals > sell_signals and buy_signals >= 2:
            signal['signal'] = 'BUY'
            signal['confidence'] = buy_signals / 4
        elif sell_signals > buy_signals and sell_signals >= 2:
            signal['signal'] = 'SELL'
            signal['confidence'] = sell_signals / 4
        else:
            signal['signal'] = 'HOLD'
            signal['confidence'] = 0
        
        return signal
    
    def get_point_value(self, symbol):
        """Get point value for the symbol."""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                return symbol_info.point
            return 0.0001
        except Exception as e:
            logger.error(f"Error getting point value for {symbol}: {str(e)}")
            return 0.0001
    
    def place_order(self, signal):
        """Place order based on trading signal."""
        try:
            if signal['signal'] is None or signal['signal'] == 'HOLD':
                return None
            
            symbol = signal['symbol']
            point = self.get_point_value(symbol)
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Failed to get tick for {symbol}")
                return None
            
            current_price = tick.ask if signal['signal'] == 'BUY' else tick.bid
            
            # Calculate SL and TP
            sl_distance = self.sl_points * point
            tp_distance = sl_distance * self.tp_ratio
            
            if signal['signal'] == 'BUY':
                stop_loss = current_price - sl_distance
                take_profit = current_price + tp_distance
                order_type = mt5.ORDER_TYPE_BUY
                action = mt5.TRADE_ACTION_DEAL
            else:  # SELL
                stop_loss = current_price + sl_distance
                take_profit = current_price - tp_distance
                order_type = mt5.ORDER_TYPE_SELL
                action = mt5.TRADE_ACTION_DEAL
            
            # Check account balance
            account_info = mt5.account_info()
            if account_info.balance < self.min_balance:
                logger.warning(f"Insufficient balance. Current: ${account_info.balance}, Required: ${self.min_balance}")
                return None
            
            # Prepare order request
            request = {
                "action": action,
                "symbol": symbol,
                "volume": self.lot_size,
                "type": order_type,
                "price": current_price,
                "sl": stop_loss,
                "tp": take_profit,
                "deviation": 20,
                "magic": 234000,
                "comment": f"AutoBot {signal['signal']} - Confidence: {signal['confidence']:.2%}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed for {symbol}: {result.comment}")
                return None
            
            logger.info(f"Order placed - {signal['signal']} {symbol} | Volume: {self.lot_size} | SL: {stop_loss:.5f} | TP: {take_profit:.5f}")
            
            self.active_orders[result.order] = {
                'symbol': symbol,
                'type': signal['signal'],
                'entry_price': current_price,
                'sl': stop_loss,
                'tp': take_profit,
                'lot_size': self.lot_size,
                'timestamp': datetime.now()
            }
            
            return result
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
    
    def check_active_orders(self):
        """Check and monitor active orders."""
        try:
            orders = mt5.positions_get()
            if not orders:
                return
            
            for order in orders:
                if order.magic == 234000:  # Our bot's magic number
                    profit = order.profit
                    logger.info(f"Order #{order.ticket}: {order.symbol} | Type: {'BUY' if order.type == 0 else 'SELL'} | Profit: ${profit:.2f}")
        except Exception as e:
            logger.error(f"Error checking active orders: {str(e)}")
    
    def run(self):
        """Main trading loop."""
        if not self.initialize_mt5():
            return
        
        try:
            logger.info("Starting Forex Trading Bot...")
            iteration = 0
            
            while True:
                try:
                    iteration += 1
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Iteration: {iteration} | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"{'='*60}")
                    
                    # Check active orders
                    self.check_active_orders()
                    
                    # Analyze each symbol
                    for symbol in self.symbols:
                        try:
                            logger.info(f"\nAnalyzing {symbol}...")
                            
                            # Market analysis
                            analysis = self.analyze_market(symbol)
                            if analysis is None:
                                logger.warning(f"Could not analyze {symbol}")
                                continue
                            
                            logger.info(f"{symbol} Price: {analysis['current_price']:.5f}")
                            logger.info(f"SMA20: {analysis['sma_20']:.5f} | SMA50: {analysis['sma_50']:.5f}")
                            logger.info(f"RSI: {analysis['rsi']:.2f}")
                            
                            # Get trading signal
                            signal = self.determine_signal(analysis)
                            
                            if signal:
                                logger.info(f"Signal: {signal['signal']} | Confidence: {signal['confidence']:.2%}")
                                for reason in signal['reason']:
                                    logger.info(f"  - {reason}")
                                
                                # Place order if strong signal
                                if signal['signal'] in ['BUY', 'SELL'] and signal['confidence'] >= 0.50:
                                    self.place_order(signal)
                        
                        except Exception as e:
                            logger.error(f"Error processing {symbol}: {str(e)}")
                            continue
                    
                    # Wait for next iteration (5 minutes)
                    logger.info(f"\nWaiting 5 minutes for next analysis...")
                    time.sleep(300)
                
                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {str(e)}")
                    time.sleep(60)
        
        finally:
            self.shutdown_mt5()
            logger.info("Trading bot stopped")

def main():
    """Main entry point."""
    bot = ForexTradingBot()
    bot.run()

if __name__ == '__main__':
    main()