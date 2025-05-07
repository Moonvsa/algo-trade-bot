import pytz

# Основные настройки подключения к бирже
EXCHANGE = "binance"          # Поддерживаемые биржи: binance, bybit, okx
SYMBOLS = [                 # Доступные торговые пары
    'BTC/USDT', 
    'ETH/USDT', 
    'SOL/USDT', 
    'ADA/USDT', 
    'DOT/USDT'
]
TIMEFRAMES = ['15m', '1h', '4h', '1d']  # Доступные таймфреймы
CANDLES_LIMIT = 100         # Количество получаемых свечей
TIMEZONE = pytz.UTC         # Часовой пояс для временных меток

# Параметры торговых стратегий
STRATEGY_PARAMS = {
    # SMA
    'sma_window': 50,       # Период для Simple Moving Average
    
    # RSI
    'rsi_period': 14,       # Период для Relative Strength Index
    'rsi_oversold': 30,     # Порог перепроданности
    'rsi_overbought': 70,   # Порог перекупленности
    
    # MACD
    'macd_fast': 12,        # Быстрая EMA
    'macd_slow': 26,        # Медленная EMA
    'macd_signal': 9,       # Сигнальная линия
    
    # Bollinger Bands
    'bollinger_period': 20, # Период для Bollinger Bands
    'bollinger_std_dev': 2, # Количество стандартных отклонений
    
    # Volume Spike
    'volume_multiplier': 2.5 # Множитель для определения всплеска объема
}

# Настройки риска
RISK_PARAMS = {
    'max_position_size': 0.1, # Максимальный размер позиции (10% от капитала)
    'stop_loss_pct': 2.0,     # Стоп-лосс в процентах
    'take_profit_pct': 4.0    # Тейк-профит в процентах
}