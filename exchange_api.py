import ccxt
from config import EXCHANGE, CANDLES_LIMIT, SYMBOLS, TIMEFRAMES
from datetime import datetime
import pytz

class ExchangeAPI:
    def __init__(self):
        self.exchange = self._init_exchange()
        self.timezone = pytz.UTC
        
    def _init_exchange(self):
        """Инициализация подключения к бирже"""
        try:
            exchange_class = getattr(ccxt, EXCHANGE)
            return exchange_class({
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            })
        except AttributeError:
            raise ValueError(f"Биржа {EXCHANGE} не поддерживается")

    def get_valid_symbols(self):
        """Получение доступных торговых пар"""
        return SYMBOLS
    
    def get_valid_timeframes(self):
        """Получение доступных таймфреймов"""
        return TIMEFRAMES

    def fetch_ohlcv(self, symbol, timeframe):
        """
        Получение исторических данных
        :param symbol: Торговая пара (например BTC/USDT)
        :param timeframe: Таймфрейм (например 1h)
        :return: Список словарей с данными свечей
        """
        try:
            data = self.exchange.fetch_ohlcv(
                symbol, 
                timeframe, 
                limit=CANDLES_LIMIT
            )
            return self._parse_ohlcv(data)
        except ccxt.NetworkError as e:
            print(f"Ошибка сети: {e}")
        except ccxt.ExchangeError as e:
            print(f"Ошибка биржи: {e}")
        return None

    def _parse_ohlcv(self, raw_data):
        """Преобразование сырых данных в структурированный формат"""
        parsed = []
        for candle in raw_data:
            parsed.append({
                'timestamp': candle[0],
                'datetime': self._convert_timestamp(candle[0]),
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': float(candle[5])
            })
        return parsed

    def _convert_timestamp(self, ts):
        """Конвертация временной метки в читаемый формат"""
        return datetime.fromtimestamp(ts / 1000, tz=self.timezone)