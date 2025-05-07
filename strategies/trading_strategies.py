# strategies/trading_strategies.py
import pandas_ta as ta
from config import STRATEGY_PARAMS

class TradingStrategies:
    
    @staticmethod
    def calculate_sma(df):
        """Расчёт Simple Moving Average"""
        return ta.sma(df['close'], length=STRATEGY_PARAMS['sma_window'])
    
    @staticmethod
    def check_sma_crossover(df):
        sma = TradingStrategies.calculate_sma(df)
        if sma is None or len(df) < 2:
            return False
        return (df['close'].iloc[-2] < sma.iloc[-2]) & (df['close'].iloc[-1] > sma.iloc[-1])

    @staticmethod
    def calculate_rsi(df):
        return ta.rsi(df['close'], length=STRATEGY_PARAMS['rsi_period'])
    
    @staticmethod
    def check_rsi_oversold(df):
        rsi_values = TradingStrategies.calculate_rsi(df)
        if rsi_values is None or len(rsi_values) < 1:
            return False
        return (rsi_values.iloc[-1] < STRATEGY_PARAMS['rsi_oversold']) & \
               (rsi_values.iloc[-2] >= STRATEGY_PARAMS['rsi_oversold'])

    @staticmethod
    def calculate_macd(df):
        macd = ta.macd(
            df['close'],
            fast=STRATEGY_PARAMS['macd_fast'],
            slow=STRATEGY_PARAMS['macd_slow'],
            signal=STRATEGY_PARAMS['macd_signal']
        )
        return macd['MACD_12_26_9'], macd['MACDs_12_26_9'], macd['MACDh_12_26_9']

    @staticmethod
    def check_macd_crossover(df):
        macd, signal, _ = TradingStrategies.calculate_macd(df)
        if macd is None or signal is None or len(macd) < 2:
            return False
        return (macd.iloc[-1] > signal.iloc[-1]) & (macd.iloc[-2] <= signal.iloc[-2])

    @staticmethod
    def calculate_bollinger_bands(df):
        bb = ta.bbands(
            df['close'],
            length=STRATEGY_PARAMS['bollinger_period'],
            std=STRATEGY_PARAMS['bollinger_std_dev']
        )
        return bb['BBU_20_2.0'], bb['BBM_20_2.0'], bb['BBL_20_2.0']

    @staticmethod
    def check_bollinger_breakout(df):
        upper, _, lower = TradingStrategies.calculate_bollinger_bands(df)
        last_close = df['close'].iloc[-1]
        return (last_close > upper.iloc[-1]) | (last_close < lower.iloc[-1])

    @staticmethod
    def check_volume_spike(df):
        if len(df) < 2:
            return False
        avg_volume = df['volume'].iloc[:-1].mean()
        return df['volume'].iloc[-1] > avg_volume * STRATEGY_PARAMS['volume_multiplier']