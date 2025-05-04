import pandas as pd
import numpy as np
from strategies import TradingStrategies
from config import STRATEGY_PARAMS, RISK_PARAMS

class Backtester:
    def __init__(self, historical_data):
        """
        Инициализация бэктестера
        :param historical_data: список словарей с историческими данными
        """
        self.data = historical_data
        self.df = pd.DataFrame(historical_data)
        self.positions = []
        self.trade_history = []
        self.current_balance = 10000  # Стартовый баланс

    def _validate_data(self):
        """Проверка минимального количества данных"""
        min_data_required = max(
            STRATEGY_PARAMS['sma_window'],
            STRATEGY_PARAMS['rsi_period'],
            STRATEGY_PARAMS['bollinger_period']
        )
        return len(self.data) >= min_data_required

    def evaluate_conditions(self):
        """Оценка выполнения торговых условий"""
        if not self._validate_data():
            raise ValueError("Недостаточно данных для анализа")

        conditions = {
            'sma_crossover': TradingStrategies.check_sma_crossover(self.data),
            'rsi_oversold': self._check_rsi_condition(),
            'macd_crossover': self._check_macd_condition(),
            'bollinger_breakout': TradingStrategies.check_bollinger_breakout(self.data),
            'volume_spike': TradingStrategies.check_volume_spike(self.data)
        }
        return conditions

    def _check_rsi_condition(self):
        """Проверка условия RSI"""
        rsi_values = TradingStrategies.calculate_rsi(self.data)
        return TradingStrategies.check_rsi_oversold(rsi_values)

    def _check_macd_condition(self):
        """Проверка условия MACD"""
        macd, signal, _ = TradingStrategies.calculate_macd(self.data)
        return TradingStrategies.check_macd_crossover(macd, signal)

    def run_backtest(self, required_conditions=2):
        """Запуск процесса бэктестинга"""
        if not self._validate_data():
            print("Недостаточно данных для тестирования")
            return

        for i in range(len(self.data)):
            current_data = self.data[:i+1]
            if len(current_data) < STRATEGY_PARAMS['sma_window']:
                continue

            conditions = self.evaluate_conditions()
            if sum(conditions.values()) >= required_conditions:
                self._open_position(current_data[-1])

            self._check_exit_conditions(current_data[-1])

        return self._generate_report()

    def _open_position(self, candle):
        """Открытие позиции"""
        position_size = self.current_balance * RISK_PARAMS['max_position_size']
        self.positions.append({
            'entry_time': candle['datetime'],
            'entry_price': candle['close'],
            'size': position_size,
            'stop_loss': candle['close'] * (1 - RISK_PARAMS['stop_loss_pct']/100),
            'take_profit': candle['close'] * (1 + RISK_PARAMS['take_profit_pct']/100)
        })
        self.current_balance -= position_size

    def _check_exit_conditions(self, candle):
        """Проверка условий выхода"""
        for position in self.positions.copy():
            if candle['close'] <= position['stop_loss'] or \
               candle['close'] >= position['take_profit']:
                self._close_position(position, candle)

    def _close_position(self, position, candle):
        """Закрытие позиции"""
        profit = (candle['close'] - position['entry_price']) * position['size']
        self.current_balance += position['size'] + profit
        
        self.trade_history.append({
            **position,
            'exit_time': candle['datetime'],
            'exit_price': candle['close'],
            'profit': profit,
            'balance': self.current_balance
        })
        self.positions.remove(position)

    def _generate_report(self):
        """Генерация итогового отчёта"""
        return pd.DataFrame(self.trade_history)