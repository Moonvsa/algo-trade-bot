from abc import ABC, abstractmethod
import pandas_ta as ta
from .trading_strategies import TradingStrategies

__all__ = ['TradingStrategies']

def __init__(self, historical_data, strategies_config=None, initial_balance=10000):
    self.strategies_config = strategies_config or {}

class BaseStrategy(ABC):
    def __init__(self, params):
        self.params = params

    @abstractmethod
    def generate_signal(self, df):
        pass

class SMACrossover(BaseStrategy):
    def generate_signal(self, df):
        sma = ta.sma(df['close'], length=self.params['sma_window'])
        if sma is None or len(df) < 2:
            return 0
        return 1 if (df['close'].iloc[-2] < sma.iloc[-2]) and (df['close'].iloc[-1] > sma.iloc[-1]) else 0

class RSIStrategy(BaseStrategy):
    def generate_signal(self, df):
        rsi = ta.rsi(df['close'], length=self.params['rsi_period'])
        if rsi is None or len(rsi) < 1:
            return 0
        return 1 if rsi.iloc[-1] < self.params['rsi_oversold'] else -1 if rsi.iloc[-1] > self.params['rsi_overbought'] else 0

class MACDCrossover(BaseStrategy):
    def generate_signal(self, df):
        macd_df = ta.macd(df['close'], 
                         fast=self.params['macd_fast'],
                         slow=self.params['macd_slow'],
                         signal=self.params['macd_signal'])
        if macd_df is None or len(macd_df) < 2:
            return 0
        return 1 if (macd_df.iloc[-1, 0] > macd_df.iloc[-1, 1]) and (macd_df.iloc[-2, 0] <= macd_df.iloc[-2, 1]) else 0

STRATEGIES = {
    'sma': SMACrossover,
    'rsi': RSIStrategy,
    'macd': MACDCrossover
}