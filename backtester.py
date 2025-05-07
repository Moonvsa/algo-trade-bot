import pandas as pd
import numpy as np
from strategies import TradingStrategies
from config import STRATEGY_PARAMS, RISK_PARAMS

class Backtester:
    def __init__(self, historical_data, strategies_config=None, initial_balance=10000):
        self.df = pd.DataFrame(historical_data)
        self.strategies_config = strategies_config or {}
        self.grid_settings = {}
        self._preprocess_data()
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.trades = []
        self.open_positions = []
        self.orders = []
        
    def _preprocess_data(self):
        """Обработка временных меток и индексов"""
        self.df['datetime'] = pd.to_datetime(self.df['timestamp'], unit='ms')
        self.df.set_index('datetime', inplace=True)
        self.df.sort_index(inplace=True)
        
    def _validate_data(self):
        """Проверка минимального количества данных"""
        required = max(
            STRATEGY_PARAMS['sma_window'],
            STRATEGY_PARAMS['rsi_period'],
            STRATEGY_PARAMS['bollinger_period']
        )
        return len(self.df) > required
        
    def _get_signals(self):
        """Сбор сигналов от всех стратегий"""
        return {
            'sma': TradingStrategies.check_sma_crossover(self.df),
            'rsi': TradingStrategies.check_rsi_oversold(self.df),
            'macd': TradingStrategies.check_macd_crossover(self.df),
            'bollinger': TradingStrategies.check_bollinger_breakout(self.df),
            'volume': TradingStrategies.check_volume_spike(self.df)
        }
    
    def _calculate_position_size(self, price):
        """Расчёт размера позиции с учётом риска"""
        risk_amount = self.current_balance * RISK_PARAMS['max_position_size']
        return risk_amount / price
        
    def _open_position(self, candle):
        """Открытие новой позиции"""
        position = {
            'entry_time': candle.name,
            'entry_price': candle['close'],
            'size': self._calculate_position_size(candle['close']),
            'stop_loss': candle['close'] * (1 - RISK_PARAMS['stop_loss_pct']/100),
            'take_profit': candle['close'] * (1 + RISK_PARAMS['take_profit_pct']/100)
        }
        self.current_balance -= position['size'] * position['entry_price']
        self.open_positions.append(position)
        
    def _close_position(self, position, candle):
        """Закрытие позиции"""
        profit = (candle['close'] - position['entry_price']) * position['size']
        self.current_balance += position['size'] * candle['close'] + profit
        
        self.trades.append({
            **position,
            'exit_time': candle.name,
            'exit_price': candle['close'],
            'profit': profit,
            'balance': self.current_balance
        })
        self.open_positions.remove(position)
        
    def _check_exit_conditions(self, candle):
        """Проверка условий выхода для открытых позиций"""
        for pos in self.open_positions.copy():
            if (candle['close'] <= pos['stop_loss']) or \
               (candle['close'] >= pos['take_profit']):
                self._close_position(pos, candle)

    def _place_order(self, order_type, price, amount):
        """Создание нового ордера"""
        self.orders.append({
            'type': order_type,
            'price': price,
            'amount': amount,
            'executed': False,
            'timestamp': candle.name if hasattr(candle, 'name') else pd.Timestamp.now()
        })

    def _execute_order(self, order, candle):
        """Исполнение ордера"""
        if order['type'] == 'buy':
            position = {
                'entry_time': candle.name,
                'entry_price': order['price'],
                'size': order['amount'],
                'stop_loss': order['price'] * (1 - RISK_PARAMS['stop_loss_pct']/100),
                'take_profit': order['price'] * (1 + RISK_PARAMS['take_profit_pct']/100)
            }
            self.current_balance -= position['size'] * position['entry_price']
            self.open_positions.append(position)
            
        elif order['type'] == 'sell':
            # Логика для sell orders (если нужно)
            pass

    def _check_orders_execution(self, candle):
        """Проверка исполнения ордеров"""
        for order in self.orders.copy():
            if not order['executed']:
                if (order['type'] == 'buy' and candle['low'] <= order['price']) or \
                   (order['type'] == 'sell' and candle['high'] >= order['price']):
                    order['executed'] = True
                    self._execute_order(order, candle)
                    self.orders.remove(order)
                
    def run_backtest(self, required_signals=2):
        """Основной цикл бэктестинга"""
        if not self._validate_data():
            return pd.DataFrame()

        for i in range(1, len(self.df)):
            current_candle = self.df.iloc[i]
            self._check_orders_execution(current_candle)
            
            # Получаем текущие сигналы
            signals = self._get_signals()
            active_signals = sum(1 for v in signals.values() if v)
            
            # Логика входа
            if active_signals >= required_signals and not self.open_positions:
                if self.current_balance > 0:
                    # Размещение ордера вместо немедленного исполнения
                    price = current_candle['close']
                    amount = self._calculate_position_size(price)
                    self._place_order('buy', price, amount)
                
            # Логика выхода
            self._check_exit_conditions(current_candle)
            
        return self._generate_report()
    
    def _generate_report(self):
        """Генерация итогового отчёта"""
        if not self.trades:
            return pd.DataFrame()
    
        report = pd.DataFrame(self.trades)
        report['return_pct'] = (report['profit'] / self.initial_balance) * 100
        report['duration'] = report['exit_time'] - report['entry_time']
        return report

    def get_performance_metrics(self):
        """Ключевые метрики производительности"""
        if not self.trades:
            return {}
            
        balances = [self.initial_balance] + [t['balance'] for t in self.trades]
        returns = [t['profit'] for t in self.trades]
        
        # Расчет максимальной просадки
        peak = balances[0]
        max_drawdown = 0
        for balance in balances:
            if balance > peak:
                peak = balance
            dd = (peak - balance)/peak
            if dd > max_drawdown:
                max_drawdown = dd
                
        return {
            'total_trades': len(self.trades),
            'win_rate': sum(1 for r in returns if r > 0) / len(returns),
            'max_drawdown': max_drawdown * 100,
            'final_balance': self.current_balance,
            'total_return_pct': ((self.current_balance/self.initial_balance)-1)*100
        }