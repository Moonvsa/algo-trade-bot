from exchange_api import ExchangeAPI
from backtester import Backtester
from visualizer import TradingVisualizer
from config import SYMBOLS, TIMEFRAMES, RISK_PARAMS
import pandas as pd

def main():
    # Инициализация API
    api = ExchangeAPI()
    
    # Выбор параметров теста
    symbol = SYMBOLS[1]    # BTC/USDT
    timeframe = TIMEFRAMES[1]  # 4h
    
    print(f"🔍 Загрузка данных {symbol} ({timeframe})...")
    data = api.fetch_ohlcv(symbol, timeframe)
    
    if not data:
        print("❌ Ошибка загрузки данных")
        return

    # Запуск бэктеста
    print("\n🔄 Запуск бэктеста...")
    backtester = Backtester(data)
    report = backtester.run_backtest(required_conditions=0)
    
    if report.empty:
        print("\n📊 Условия для входа не выполнялись")
    else:
        print("\n✅ Успешные сделки:")
        print(report[['entry_time', 'entry_price', 'exit_price', 'profit']])
        print(f"\n💵 Итоговый баланс: ${backtester.current_balance:.2f}")

    # Визуализация
    print("\n🎨 Генерация графиков...")
    visualizer = TradingVisualizer(data)
    
    try:
        visualizer.plot_full_analysis(
            trades=backtester.trade_history,
            filepath='trading_analysis.png'
        )
        print("📈 График сохранён в trading_analysis.png")
    except Exception as e:
        print(f"❌ Ошибка визуализации: {e}")

if __name__ == "__main__":
    main()