#!/usr/bin/env python3
"""
Mobile Trading Bot Dashboard
Flask web server for mobile-friendly trading bot interface
Access from any device: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
import MetaTrader5 as mt5
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

class MobileTrader:
    def __init__(self):
        """Initialize mobile trader."""
        self.account_balance = 0
        self.equity = 0
        self.positions = []
        self.trades_today = 0
        self.daily_profit = 0
        
    def connect_mt5(self, account, password, server):
        """Connect to MetaTrader 5."""
        try:
            if not mt5.initialize(login=account, password=password, server=server):
                logger.error(f"MT5 connection failed: {mt5.last_error()}")
                return False
            
            logger.info("✅ Connected to MT5")
            return True
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False
    
    def get_account_info(self):
        """Get account information."""
        try:
            account_info = mt5.account_info()
            if account_info:
                return {
                    'login': account_info.login,
                    'balance': round(account_info.balance, 2),
                    'equity': round(account_info.equity, 2),
                    'free_margin': round(account_info.margin_free, 2),
                    'margin_level': round(account_info.margin_level, 2) if account_info.margin_level else 0,
                    'server': account_info.server
                }
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
        return None
    
    def get_open_positions(self):
        """Get all open positions."""
        try:
            positions = mt5.positions_get()
            if positions:
                pos_list = []
                for pos in positions:
                    pos_list.append({
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': 'BUY' if pos.type == 0 else 'SELL',
                        'volume': pos.volume,
                        'open_price': round(pos.price_open, 5),
                        'current_price': round(pos.price_current, 5),
                        'sl': round(pos.sl, 5) if pos.sl else 0,
                        'tp': round(pos.tp, 5) if pos.tp else 0,
                        'profit': round(pos.profit, 2),
                        'open_time': pos.time_setup.strftime('%Y-%m-%d %H:%M:%S')
                    })
                return pos_list
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
        return []
    
    def get_trading_history(self, days=1):
        """Get trading history for last N days."""
        try:
            from datetime import timedelta
            
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            deals = mt5.history_deals_get(start_time, end_time)
            if deals:
                history = []
                for deal in deals:
                    if deal.entry == 1:  # Only closed deals
                        history.append({
                            'ticket': deal.ticket,
                            'symbol': deal.symbol,
                            'type': 'BUY' if deal.type == 0 else 'SELL',
                            'volume': deal.volume,
                            'price': round(deal.price, 5),
                            'profit': round(deal.profit, 2),
                            'commission': round(deal.commission, 2),
                            'time': deal.time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                return history
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
        return []
    
    def place_order(self, symbol, order_type, volume, price, sl, tp, comment):
        """Place an order."""
        try:
            order_type_val = mt5.ORDER_TYPE_BUY if order_type == 'BUY' else mt5.ORDER_TYPE_SELL
            
            request_dict = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': symbol,
                'volume': volume,
                'type': order_type_val,
                'price': price,
                'sl': sl,
                'tp': tp,
                'deviation': 20,
                'magic': 123456,
                'comment': comment,
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request_dict)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Order placed: {order_type} {symbol}")
                return {'success': True, 'order': result.order, 'message': 'Order placed successfully'}
            else:
                logger.error(f"Order failed: {result.comment}")
                return {'success': False, 'message': result.comment}
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def close_position(self, ticket):
        """Close a position."""
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return {'success': False, 'message': 'Position not found'}
            
            pos = position[0]
            order_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            
            request_dict = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': pos.symbol,
                'volume': pos.volume,
                'type': order_type,
                'position': ticket,
                'deviation': 20,
                'magic': 123456,
                'comment': 'Mobile close',
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request_dict)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Position closed: {ticket}")
                return {'success': True, 'message': 'Position closed successfully'}
            else:
                return {'success': False, 'message': result.comment}
        except Exception as e:
            logger.error(f"Error closing position: {str(e)}")
            return {'success': False, 'message': str(e)}

# Initialize trader
trader = MobileTrader()

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/connect', methods=['POST'])
def connect():
    """Connect to MT5."""
    data = request.json
    account = int(data.get('account'))
    password = data.get('password')
    server = data.get('server')
    
    if trader.connect_mt5(account, password, server):
        return jsonify({'success': True, 'message': 'Connected to MT5'})
    return jsonify({'success': False, 'message': 'Connection failed'})

@app.route('/api/account', methods=['GET'])
def get_account():
    """Get account information."""
    info = trader.get_account_info()
    return jsonify(info if info else {'error': 'Failed to get account info'})

@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get open positions."""
    positions = trader.get_open_positions()
    return jsonify({'positions': positions})

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get trading history."""
    days = request.args.get('days', 1, type=int)
    history = trader.get_trading_history(days)
    return jsonify({'history': history})

@app.route('/api/order', methods=['POST'])
def place_order():
    """Place an order."""
    data = request.json
    result = trader.place_order(
        data.get('symbol'),
        data.get('type'),
        float(data.get('volume')),
        float(data.get('price')),
        float(data.get('sl')),
        float(data.get('tp')),
        data.get('comment', 'Mobile order')
    )
    return jsonify(result)

@app.route('/api/close', methods=['POST'])
def close_position():
    """Close a position."""
    data = request.json
    result = trader.close_position(int(data.get('ticket')))
    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get trading statistics."""
    account_info = trader.get_account_info()
    positions = trader.get_open_positions()
    history = trader.get_trading_history(1)
    
    total_profit = sum(h['profit'] for h in history)
    win_trades = len([h for h in history if h['profit'] > 0])
    total_trades = len(history)
    
    return jsonify({
        'account': account_info,
        'open_positions': len(positions),
        'today_profit': round(total_profit, 2),
        'win_rate': round((win_trades / total_trades * 100) if total_trades > 0 else 0, 2),
        'total_trades': total_trades
    })

if __name__ == '__main__':
    # Run on all network interfaces so you can access from mobile
    app.run(host='0.0.0.0', port=5000, debug=True)
