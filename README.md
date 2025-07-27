# 📈 Commodity Momentum Backtest Strategy

This Python script implements a flexible backtesting engine to evaluate momentum or contrarian trading strategies across multiple commodities using historical price data.

## 🔍 Features

- Ranks commodities based on historical returns
- Dynamically allocates capital to top N commodities
- Supports both momentum and contrarian logic
- Customizable parameters:
  - Lookback period
  - Rebalancing frequency
  - Initial capital
  - Start date
  - Number of commodities to select
- Generates interactive equity curve using Plotly

## 📁 Project Structure

| File | Description |
|------|-------------|
| `backtest.py`     | Main Python script for strategy execution |
| `Commodity.xlsx`  | Sample input file with historical commodity prices |
| `README.md`       | Project overview and usage guide |
| `.gitignore`      | Specifies files to exclude from version control |
| `requirements.txt`| Python dependencies for the project (optional) |

## ▶️ How to Run

1. **Install Python** (if not already installed)

2. **Install required libraries**:
   ```bash
   pip install pandas numpy plotly openpyxl
3. Input Data:
   This repository includes a sample Commodity.xlsx file used in the backtest.
   If you're using your own data, ensure it follows the same format:
   Dates in the first column
   Each commodity as a separate column with daily prices
4. Run the Script:
   python backtest.py

5. Customize the Strategy:
   Modify parameters in backtest.py to explore different configurations:
   backtest(
      Asset=Commodity,
      lookback=252,
      rebalance=10,
      capital=1e7,
      start_date=None,
      Contrarian=False  # Set to True for contrarian strategy,
      N=2.0)
   
✅ Output
Interactive Plotly line chart showing the strategy’s equity curve





