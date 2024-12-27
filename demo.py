
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import riskfolio as rp
import matplotlib.pyplot as plt

# Function to fetch stock data
def get_stock_data(tickers, start_date, end_date):
    # return yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    data = yf.download(tickers, start=start_date, end=end_date)
    if data.empty:
        raise ValueError("No data retrieved. Please check the tickers or date range.")
    if 'Adj Close' in data:
        return data['Adj Close']
    else:
        st.warning("Adjusted Close data not found. Using Close prices instead.")
        return data['Close']

# Function to optimize portfolio
def optimize_portfolio(data, risk_measure, objective):
    returns = data.pct_change().dropna()
    port = rp.Portfolio(returns=returns)
    port.assets_stats(method_mu='hist', method_cov='hist')
    optimal_weights = port.optimization(model='Classic', rm=risk_measure, obj=objective, rf=0, l=0, hist=True)
    return optimal_weights

# plt.figure(figsize=(10, 6))
# rp.plot_pie(w=selected_df['optimal_weights'].values[0],
#             title=f"Optimized Portfolio Allocation - {portfolio_key}",
#             others=0.05,
#             nrow=25)
# plt.legend(fontsize="x-large")
# plt.grid(True)
# plt.show()

# Streamlit app interface
st.title("Portfolio Optimization Web App")
st.sidebar.header("User Input Parameters")

# Sidebar inputs
tickers_input = st.sidebar.text_input("Enter stock tickers (comma-separated)", "AAPL,MSFT,GOOG")
start_date = st.sidebar.date_input("Start Date", pd.Timestamp("2015-01-01"))
end_date = st.sidebar.date_input("End Date", pd.Timestamp("2024-12-14"))
risk_measure = st.sidebar.selectbox("Select Risk Measure", ["MV", "MAD", "CVaR", "MSV"])
objective = st.sidebar.selectbox("Select Objective", ["Sharpe", "MinRisk"])

# Fetch and display stock data
if st.sidebar.button("Run Optimization"):
    tickers = tickers_input.split(",")
    st.write(f"Fetching data for: {tickers}")
    data = get_stock_data(tickers, start_date, end_date)
    st.line_chart(data)
    
    st.write("Optimizing Portfolio...")
    optimal_weights = optimize_portfolio(data, risk_measure, objective)
    
    st.write("Optimal Weights:")
    st.write(optimal_weights)
    
    # Pie chart of allocations
    fig, ax = plt.subplots()
    # optimal_weights.plot.pie(ax=ax, autopct='%1.1f%%', figsize=(6, 6))
    rp.plot_pie(w=optimal_weights,
            title=f"Optimized Portfolio Allocation",
            others=0.05,
            nrow=25)
    st.pyplot(fig)
