import talib as ta
import numpy as np
from config import STRATEGY_PARAMS

class TradingStrategies:
    
    @staticmethod
    def calculate_sma(data):
        """Расчёт Simple Moving Average"""
        closes = np.array([c['close'] for c in data])
        return ta.SMA(closes, timeperiod=STRATEGY_PARAMS['sma_window'])
    
    @staticmethod
    def check_sma_crossover(data):
        """Проверка пересечения цены и SMA"""
        sma = TradingStrategies.calculate_sma(data)
        if len(sma) < 2:
            return False
        return data[-2]['close'] < sma[-2] and data[-1]['close'] > sma[-1]

    @staticmethod
    def calculate_rsi(data):
        """Расчёт Relative Strength Index"""
        closes = np.array([c['close'] for c in data])
        return ta.RSI(closes, timeperiod=STRATEGY_PARAMS['rsi_period'])
    
    @staticmethod
    def check_rsi_oversold(rsi_values):
        """Проверка RSI на перепроданность"""
        if len(rsi_values) == 0:
            return False
        return rsi_values[-1] < STRATEGY_PARAMS['rsi_oversold']

    @staticmethod
    def calculate_macd(data):
        """Расчёт MACD"""
        closes = np.array([c['close'] for c in data])
        return ta.MACD(
            closes,
            fastperiod=STRATEGY_PARAMS['macd_fast'],
            slowperiod=STRATEGY_PARAMS['macd_slow'],
            signalperiod=STRATEGY_PARAMS['macd_signal']
        )

    @staticmethod
    def check_macd_crossover(macd, signal):
        """Проверка пересечения MACD и сигнальной линии"""
        if len(macd) < 2 or len(signal) < 2:
            return False
        return macd[-1] > signal[-1] and macd[-2] <= signal[-2]

    @staticmethod
    def calculate_bollinger_bands(data):
        """Расчёт Bollinger Bands"""
        closes = np.array([c['close'] for c in data])
        upper, middle, lower = ta.BBANDS(
            closes,
            timeperiod=STRATEGY_PARAMS['bollinger_period'],
            nbdevup=STRATEGY_PARAMS['bollinger_std_dev'],
            nbdevdn=STRATEGY_PARAMS['bollinger_std_dev']
        )
        return upper, middle, lower

    @staticmethod
    def check_bollinger_breakout(data):
        """Проверка пробоя Bollinger Bands"""
        upper, _, lower = TradingStrategies.calculate_bollinger_bands(data)
        last_close = data[-1]['close']
        return last_close > upper[-1] or last_close < lower[-1]

    @staticmethod
    def check_volume_spike(data):
        """Проверка аномального объёма"""
        volumes = np.array([v['volume'] for v in data])
        if len(volumes) < 2:
            return False
        avg_volume = np.mean(volumes[:-1])
        return volumes[-1] > avg_volume * STRATEGY_PARAMS['volume_multiplier']