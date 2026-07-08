#!/usr/bin/env python3
"""
Performance Analytics Module
Tracks and analyzes trading performance metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceAnalytics:
    def __init__(self):
        """Initialize performance analytics."""
        self.trades = []
        self.daily_returns = {}
        
    def add_trade(self, symbol, entry_price, exit_price, entry_time, exit_time, lot_size):
        """Add a completed trade."""
        profit_loss = (exit_price - entry_price) * lot_size * 100000
        duration = (exit_time - entry_time).total_seconds() / 60  # in minutes
        
        trade = {
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'lot_size': lot_size,
            'profit_loss': profit_loss,
            'roi': (profit_loss / (entry_price * lot_size)) * 100,
            'duration': duration
        }
        
        self.trades.append(trade)
        logger.info(f"Trade added: {symbol} | P&L: ${profit_loss:.2f}")
        
        return trade
    
    def get_total_return(self):
        """Calculate total return."""
        if not self.trades:
            return 0
        return sum(t['profit_loss'] for t in self.trades)
    
    def get_win_rate(self):
        """Calculate win rate."""
        if not self.trades:
            return 0
        
        winning_trades = len([t for t in self.trades if t['profit_loss'] > 0])
        return (winning_trades / len(self.trades)) * 100
    
    def get_average_win(self):
        """Calculate average winning trade."""
        winning_trades = [t for t in self.trades if t['profit_loss'] > 0]
        if not winning_trades:
            return 0
        return np.mean([t['profit_loss'] for t in winning_trades])
    
    def get_average_loss(self):
        """Calculate average losing trade."""
        losing_trades = [t for t in self.trades if t['profit_loss'] < 0]
        if not losing_trades:
            return 0
        return np.mean([t['profit_loss'] for t in losing_trades])
    
    def get_profit_factor(self):
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = sum(t['profit_loss'] for t in self.trades if t['profit_loss'] > 0)
        gross_loss = abs(sum(t['profit_loss'] for t in self.trades if t['profit_loss'] < 0))
        
        if gross_loss == 0:
            return 0
        
        return gross_profit / gross_loss
    
    def get_sharpe_ratio(self, risk_free_rate=0.02):
        """Calculate Sharpe ratio."""
        if not self.trades:
            return 0
        
        returns = [t['roi'] for t in self.trades]
        mean_return = np.mean(returns)
        std_dev = np.std(returns)
        
        if std_dev == 0:
            return 0
        
        sharpe_ratio = (mean_return - risk_free_rate) / std_dev
        return sharpe_ratio
    
    def get_max_drawdown(self):
        """Calculate maximum drawdown."""
        if not self.trades:
            return 0
        
        cumulative_returns = []
        cumsum = 0
        
        for trade in self.trades:
            cumsum += trade['profit_loss']
            cumulative_returns.append(cumsum)
        
        peak = cumulative_returns[0]
        max_dd = 0
        
        for value in cumulative_returns:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak if peak != 0 else 0
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd * 100
    
    def get_recovery_factor(self):
        """Calculate recovery factor."""
        total_return = self.get_total_return()
        max_drawdown_value = self.get_max_drawdown() / 100
        
        if max_drawdown_value == 0:
            return 0
        
        return total_return / (max_drawdown_value * 100)
    
    def get_statistics(self):
        """Get comprehensive statistics."""
        stats = {
            'total_trades': len(self.trades),
            'total_return': self.get_total_return(),
            'win_rate': self.get_win_rate(),
            'average_win': self.get_average_win(),
            'average_loss': self.get_average_loss(),
            'profit_factor': self.get_profit_factor(),
            'sharpe_ratio': self.get_sharpe_ratio(),
            'max_drawdown': self.get_max_drawdown(),
            'recovery_factor': self.get_recovery_factor()
        }
        return stats
    
    def print_report(self):
        """Print performance report."""
        stats = self.get_statistics()
        
        logger.info("\n" + "="*60)
        logger.info("PERFORMANCE REPORT")
        logger.info("="*60)
        logger.info(f"Total Trades: {stats['total_trades']}")
        logger.info(f"Total Return: ${stats['total_return']:.2f}")
        logger.info(f"Win Rate: {stats['win_rate']:.2f}%")
        logger.info(f"Average Win: ${stats['average_win']:.2f}")
        logger.info(f"Average Loss: ${stats['average_loss']:.2f}")
        logger.info(f"Profit Factor: {stats['profit_factor']:.2f}")
        logger.info(f"Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
        logger.info(f"Max Drawdown: {stats['max_drawdown']:.2f}%")
        logger.info(f"Recovery Factor: {stats['recovery_factor']:.2f}")
        logger.info("="*60 + "\n")
    
    def export_to_csv(self, filename='trades.csv'):
        """Export trades to CSV file."""
        try:
            df = pd.DataFrame(self.trades)
            df.to_csv(filename, index=False)
            logger.info(f"Trades exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting trades: {str(e)}")
            return False
    
    def plot_equity_curve(self):
        """Plot equity curve."""
        try:
            import matplotlib.pyplot as plt
            
            cumulative_pnl = []
            cumsum = 0
            
            for trade in self.trades:
                cumsum += trade['profit_loss']
                cumulative_pnl.append(cumsum)
            
            plt.figure(figsize=(12, 6))
            plt.plot(cumulative_pnl, marker='o')
            plt.title('Equity Curve')
            plt.xlabel('Trade Number')
            plt.ylabel('Cumulative P&L ($)')
            plt.grid(True)
            plt.savefig('equity_curve.png')
            logger.info("Equity curve saved to equity_curve.png")
            
            return True
        except Exception as e:
            logger.error(f"Error plotting equity curve: {str(e)}")
            return False

if __name__ == '__main__':
    # Example usage
    analytics = PerformanceAnalytics()
    
    # Add sample trades
    analytics.add_trade('EURUSD', 1.1000, 1.1050, datetime.now(), datetime.now(), 0.01)
    analytics.add_trade('EURUSD', 1.1050, 1.1030, datetime.now(), datetime.now(), 0.01)
    analytics.add_trade('XAUUSD', 2000, 2010, datetime.now(), datetime.now(), 0.01)
    
    # Print report
    analytics.print_report()
