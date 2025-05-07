import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from backtester import Backtester
from exchange_api import ExchangeAPI
import pandas as pd

# Инициализация Dash приложения
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Algo Trading Dashboard", style={
        'textAlign': 'center',
        'color': '#2c3e50',
        'marginBottom': '30px'
    }),
    
    html.Div([
        html.Div([
            html.H3("Настройки стратегии", style={'color': '#34495e'}),
            
            dcc.Checklist(
                id='strategy-selector',
                options=[
                    {'label': ' SMA Crossover', 'value': 'sma'},
                    {'label': ' RSI Strategy', 'value': 'rsi'},
                    {'label': ' MACD Crossover', 'value': 'macd'}
                ],
                value=['sma', 'rsi'],
                labelStyle={'display': 'block', 'margin': '5px 0'}
            ),
            
            html.Div([
                html.Label("Сигналов для входа:",
                          style={'margin': '15px 0 5px 0', 'display': 'block'}),
                dcc.Slider(
                    id='signals-required',
                    min=1,
                    max=5,
                    step=1,
                    value=3,
                    marks={i: str(i) for i in range(1, 6)},
                )
            ], style={'margin': '20px 0'}),

            html.Div([
                html.Label("Торговая пара:", style={'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='symbol-selector',
                    options=[{'label': s, 'value': s} for s in ExchangeAPI().get_valid_symbols()],
                    value='BTC/USDT',
                    clearable=False
                )
            ], style={'margin': '10px 0'}),

            html.Div([
                html.Label("Таймфрейм:", style={'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='timeframe-selector',
                    options=[
                        {'label': '15 Minutes', 'value': '15m'},
                        {'label': '1 Hour', 'value': '1h'},
                        {'label': '4 Hours', 'value': '4h'},
                        {'label': '1 Day', 'value': '1d'}
                    ],
                    value='4h',
                    clearable=False
                )
            ], style={'margin': '10px 0'}),

            html.Div([
                html.Label("Риск на ордер (%):", style={'marginBottom': '5px'}),
                dcc.Slider(
                    id='risk-slider',
                    min=1,
                    max=10,
                    step=1,
                    value=2,
                    marks={i: f'{i}%' for i in range(1, 11)},
                )
            ], style={'margin': '20px 0'})

        ], style={
            'padding': '25px',
            'backgroundColor': '#ffffff',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
        })
    ], style={
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '20px'
    }),

    html.Div([
        dcc.Graph(id='price-chart',
                 style={'height': '600px', 'marginTop': '20px'}),
        html.Div(id='backtest-results',
                style={'marginTop': '30px', 'padding': '20px'})
    ])
])

@app.callback(
    [Output('price-chart', 'figure'),
     Output('backtest-results', 'children')],
    [Input('symbol-selector', 'value'),
     Input('timeframe-selector', 'value'),
     Input('strategy-selector', 'value'),
     Input('signals-required', 'value'),
     Input('risk-slider', 'value')]
)
def update_dashboard(symbol, timeframe, selected_strategies, signals_required, risk_percent):
    # 1. Получение данных
    api = ExchangeAPI()
    data = api.fetch_ohlcv(symbol, timeframe)
    
    if not data:
        return go.Figure(), html.Div("❌ Ошибка загрузки данных", 
                                   style={'color': '#e74c3c', 'padding': '20px'})
    
    # 2. Конфигурация стратегий
    strategies_config = {
        'sma': {'sma_window': 50},
        'rsi': {'rsi_period': 14, 'rsi_oversold': 30, 'rsi_overbought': 70},
        'macd': {'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9}
    }
    filtered_config = {k: v for k, v in strategies_config.items() if k in selected_strategies}
    
    # 3. Инициализация бэктестера
    backtester = Backtester(
        historical_data=data,
        strategies_config=filtered_config,
        initial_balance=10000
    )
    
    # 4. Настройка параметров
    backtester.grid_settings.update({
        'signals_required': signals_required,
        'risk_per_order': risk_percent / 100
    })
    
    # 5. Запуск теста
    report = backtester.run_backtest()
    
    # 6. Визуализация
    fig = go.Figure()
    
    # График цен
    fig.add_trace(go.Candlestick(
        x=[d['datetime'] for d in data],
        open=[d['open'] for d in data],
        high=[d['high'] for d in data],
        low=[d['low'] for d in data],
        close=[d['close'] for d in data],
        name='Price',
        increasing_line_color='#2ecc71',
        decreasing_line_color='#e74c3c'
    ))
    
    # Ордера
    if backtester.orders:
        order_prices = [o['price'] for o in backtester.orders if not o['executed']]
        fig.add_trace(go.Scatter(
            x=[data[-1]['datetime']]*len(order_prices),
            y=order_prices,
            mode='markers',
            marker=dict(
                color='rgba(52, 152, 219, 0.5)',
                size=12,
                line=dict(width=1, color='#2c3e50')
            ),
            name='Pending Orders'
        ))
    
    # Сделки
    if not report.empty:
        entries = report['entry_time'].dt.to_pydatetime().tolist()
        entry_prices = report['entry_price'].tolist()
        exits = report['exit_time'].dt.to_pydatetime().tolist()
        exit_prices = report['exit_price'].tolist()
        
        fig.add_trace(go.Scatter(
            x=entries,
            y=entry_prices,
            mode='markers',
            marker=dict(
                color='#27ae60',
                size=10,
                line=dict(width=1, color='white')
            ),
            name='Buy'
        ))
        
        fig.add_trace(go.Scatter(
            x=exits,
            y=exit_prices,
            mode='markers',
            marker=dict(
                color='#c0392b',
                size=10,
                line=dict(width=1, color='white')
            ),
            name='Sell'
        ))

    fig.update_layout(
        title=f'{symbol} {timeframe} - Trading Analysis',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_white',
        hovermode='x unified',
        font=dict(family="Arial, sans-serif"),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Результаты
    if not report.empty:
        max_drawdown = min((t['balance']/10000-1)*100 for t in report) if report else 0
        stats = html.Div([
            html.H3("Результаты бэктеста", style={'color': '#2c3e50'}),
            html.Div([
                html.Div([
                    html.P("Всего сделок:", style={'fontWeight': 'bold'}),
                    html.P(f"{len(report)}", style={'fontSize': '24px'})
                ], style={'flex': 1, 'textAlign': 'center'}),
                
                html.Div([
                    html.P("Конечный баланс:", style={'fontWeight': 'bold'}),
                    html.P(f"${backtester.current_balance:,.2f}", 
                          style={'color': '#27ae60' if backtester.current_balance >= 10000 else '#c0392b', 
                                'fontSize': '24px'})
                ], style={'flex': 1, 'textAlign': 'center'}),
                
                html.Div([
                    html.P("Прибыль/Убыток:", style={'fontWeight': 'bold'}),
                    html.P(f"{((backtester.current_balance/10000)-1)*100:.2f}%", 
                          style={'color': '#27ae60' if backtester.current_balance >= 10000 else '#c0392b', 
                                'fontSize': '24px'})
                ], style={'flex': 1, 'textAlign': 'center'}),
                
                html.Div([
                    html.P("Макс. просадка:", style={'fontWeight': 'bold'}),
                    html.P(f"{max_drawdown:.2f}%", 
                          style={'color': '#c0392b' if max_drawdown < 0 else '#2c3e50', 
                                'fontSize': '24px'})
                ], style={'flex': 1, 'textAlign': 'center'})
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'marginTop': '20px',
                'padding': '20px',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '10px'
            })
        ])
    else:
        stats = html.Div("🤷 Нет сделок для отображения", 
                        style={
                            'color': '#7f8c8d',
                            'textAlign': 'center',
                            'padding': '20px'
                        })
    
    return fig, stats

if __name__ == '__main__':
    app.run(debug=True, port=8051)