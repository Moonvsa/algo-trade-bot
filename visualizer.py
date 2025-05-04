import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from strategies import TradingStrategies
from config import STRATEGY_PARAMS

class TradingVisualizer:
    def __init__(self, historical_data):
        self.df = pd.DataFrame(historical_data)
        self._prepare_data()

    def _prepare_data(self):
        self.df['datetime'] = pd.to_datetime(self.df['timestamp'], unit='ms')
        self.df.set_index('datetime', inplace=True)
        self._calculate_indicators()

    def _calculate_indicators(self):
        # SMA
        self.df['sma'] = TradingStrategies.calculate_sma(self.df.to_dict('records'))
        
        # RSI
        rsi_values = TradingStrategies.calculate_rsi(self.df.to_dict('records'))
        self.df['rsi'] = rsi_values
        
        # MACD
        macd, signal, _ = TradingStrategies.calculate_macd(self.df.to_dict('records'))
        self.df['macd'] = macd
        self.df['macd_signal'] = signal
        
        # Bollinger Bands
        upper, _, lower = TradingStrategies.calculate_bollinger_bands(self.df.to_dict('records'))
        self.df['bb_upper'] = upper
        self.df['bb_lower'] = lower

    def plot_full_analysis(self, trades=None, filepath=None):
        plt.figure(figsize=(16, 12))
        
        # 1. График цены
        ax1 = plt.subplot(4, 1, 1)
        ax1.plot(self.df.index, self.df['close'], label='Price', color='#1f77b4')
        ax1.plot(self.df.index, self.df['sma'], label=f"SMA {STRATEGY_PARAMS['sma_window']}", color='#ff7f0e')
        ax1.fill_between(self.df.index, self.df['bb_upper'], self.df['bb_lower'], 
                        color='#e0e0e0', alpha=0.3, label='Bollinger Bands')
        
        # 2. RSI
        ax2 = plt.subplot(4, 1, 2)
        ax2.plot(self.df.index, self.df['rsi'], label='RSI', color='#9467bd')
        ax2.axhline(STRATEGY_PARAMS['rsi_oversold'], color='#2ca02c', linestyle='--')
        ax2.axhline(STRATEGY_PARAMS['rsi_overbought'], color='#d62728', linestyle='--')
        
        # 3. MACD
        ax3 = plt.subplot(4, 1, 3)
        ax3.plot(self.df.index, self.df['macd'], label='MACD', color='#17becf')
        ax3.plot(self.df.index, self.df['macd_signal'], label='Signal Line', color='#bcbd22')
        
        # 4. Объёмы
        ax4 = plt.subplot(4, 1, 4)
        ax4.bar(self.df.index, self.df['volume'], color='#7f7f7f', alpha=0.8)
        
        # Сделки
        if trades:
            entry_dates = [pd.to_datetime(t['entry_time']) for t in trades]
            entry_prices = [t['entry_price'] for t in trades]
            exit_dates = [pd.to_datetime(t['exit_time']) for t in trades]
            exit_prices = [t['exit_price'] for t in trades]
            
            ax1.scatter(entry_dates, entry_prices, marker='^', 
                       color='#2ca02c', s=100, label='Entry', zorder=5)
            ax1.scatter(exit_dates, exit_prices, marker='v', 
                       color='#d62728', s=100, label='Exit', zorder=5)

        # Форматирование
        for ax in [ax1, ax2, ax3, ax4]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend()

        plt.tight_layout()
        
        if filepath:
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()