
import pandas as pd
import numpy as np
import yfinance as yf
import riskfolio as rp
import plotly.express as px
import matplotlib.pyplot as plt  # Ensure this is imported at the top

run_in_browser = True

if run_in_browser:
    import streamlit as st
else:
    # Fake Streamlit class to mimic Streamlit behavior in the console
    class FakeStreamlit:
        def __init__(self):
            self.sidebar = self.Sidebar()

        class Sidebar:
            def header(self, text):
                print(f"[SIDEBAR HEADER]: {text}")

            def checkbox(self, label, value=False):
                print(f"[SIDEBAR CHECKBOX]: {label} (Default: {value})")
                return value  # Default behavior

            def date_input(self, label, default):
                print(f"[SIDEBAR DATE INPUT]: {label} (Default: {default})")
                return default  # Default date

            def selectbox(self, label, options, index=0):
                print(f"[SIDEBAR SELECTBOX]: {label} (Options: {options}, Default: {options[index]})")
                return options[index]  # Default selection

            def button(self, label):
                print(f"[SIDEBAR BUTTON]: {label}")
                return True  # Default to button being "pressed"

            def write(self, content):
                print(f"[SIDEBAR WRITE]: {content}")

        def title(self, text):
            print(f"[TITLE]: {text}")

        def write(self, text):
            print(f"[WRITE]: {text}")

        def error(self, text):
            print(f"[ERROR]: {text}")

        def line_chart(self, data):
            print("[LINE CHART]: Displaying line chart with data.")
            print(data)

        def plotly_chart(self, fig):
            print("[PLOTLY CHART]: Displaying chart.")
            print(fig)

        def warning(self, text):
            print(f"[WARNING]: {text}")

        def success(self, text):
            print(f"[SUCCESS]: {text}")

    st = FakeStreamlit()

# Predefined stock categories
fixed_etfs = ["BND", "AGG", "FBND", "BSV", "LQD", "IEF", "VCIT", "HYG", "TIP", "MUB"]
public_etfs = ["XLK", "XLP", "XLY", "XLF", "XLE", "XLV", "XLRE", "VGK", "VWO"]
individual_stocks = ["KO", "SBUX", "JPM", "XOM", "UNH", "F", "O", "MSFT", "AAPL", "NVDA"]
trump_donor_stocks = ["LLYVK", "IBKR", "SCHW"]
pelosi_stocks = ["PANW", "CRWD", "AMZN", "AB", "DIS"]
CHATGPT_4_STOCKS = ["QQQ", "BX", "COST", "QCOM", "IHF"]
global_equities = ["VEU", "EFA", "IEMG", "VTI", "VXUS", "FSKAX"]
YOLO_STOCKS = ["PLTR", "AVGO", "TSLA"]

risk_measures_list = [
    ("MV", True, "ok"),
    ("KT", True, "ok"),
    ("MAD", True, "ok"),
    ("GMD", False, "Takes too much time"),
    ("MSV", True, "ok"),
    ("SKT", True, "ok"),
    ("FLPM", True, "ok"),
    ("SLPM", True, "ok"),
    ("CVaR", True, "ok"),
    ("TG", False, "Takes too much time"),
    ("EVaR", False, "Takes too much time"),
    ("RLVaR", False, "Takes too much time"),
    ("WR", True, ""),
    ("RG", True, ""),
    ("CVRG", True, ""),
    ("TGRG", False, "Takes too much time"),
    ("MDD", True, ""),
    ("ADD", True, ""),
    ("CDaR", True, ""),
    ("EDaR", False, "Takes too much time"),
    ("RLDaR", True, ""),
    ("UCI", True, "")
]

# Filter available risk measures
available_risk_measures = [rm[0] for rm in risk_measures_list if rm[1]]

# Function to fetch stock data
def get_stock_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)
    if data.empty:
        raise ValueError("No data retrieved. Please check the tickers or date range.")
    if 'Adj Close' in data:
        return data['Adj Close']
    else:
        return data['Close']

# Function to optimize portfolio
def optimize_portfolio(data, risk_measure, objective):
    returns = data.pct_change().dropna()
    port = rp.Portfolio(returns=returns)
    port.assets_stats(method_mu='hist', method_cov='hist')
    optimal_weights = port.optimization(model='Classic', rm=risk_measure, obj=objective, rf=0, l=0, hist=True)
    return optimal_weights

# Function to calculate growth of a dollar
def calculate_growth_of_dollar(data, weights, initial_investment):
    returns = data.pct_change().dropna()
    portfolio_returns = returns.dot(weights)
    cum_returns = (1 + portfolio_returns).cumprod()
    growth_of_dollar = cum_returns * initial_investment
    return growth_of_dollar

# Streamlit app interface
st.title("Portfolio Optimization Web App")
st.sidebar.header("User Input Parameters")

# Sidebar: Category selection
selected_tickers = []

if st.sidebar.checkbox("Fixed ETFs"):
    selected_tickers.extend(fixed_etfs)
if st.sidebar.checkbox("Public ETFs"):
    selected_tickers.extend(public_etfs)
if st.sidebar.checkbox("Individual Stocks"):
    selected_tickers.extend(individual_stocks)
if st.sidebar.checkbox("Trump Donor Stocks"):
    selected_tickers.extend(trump_donor_stocks)
if st.sidebar.checkbox("Pelosi Stocks"):
    selected_tickers.extend(pelosi_stocks)
if st.sidebar.checkbox("CHATGPT 4 Stocks"):
    selected_tickers.extend(CHATGPT_4_STOCKS)
if st.sidebar.checkbox("Global Equities"):
    selected_tickers.extend(global_equities)
if st.sidebar.checkbox("YOLO Stocks"):
    selected_tickers.extend(YOLO_STOCKS)

# Sidebar: Other parameters
start_date = st.sidebar.date_input("Start Date", pd.Timestamp("2015-01-01"))
end_date = st.sidebar.date_input("End Date", pd.Timestamp("2024-12-14"))
risk_measure = st.sidebar.selectbox("Select Risk Measure", available_risk_measures)
objective = st.sidebar.selectbox("Select Objective", ["Sharpe", "MinRisk", "MaxRet"])
initial_investment = st.sidebar.number_input("Initial Investment ($)", value=100_000, step=1_000) if run_in_browser else 100_000

# Display selected tickers
# Sidebar: Edit selected tickers
st.sidebar.header("Customize Your Ticker Selection")

# Multiselect for existing tickers
current_tickers = st.sidebar.multiselect(
    "Edit Selected Tickers:",
    selected_tickers,
    selected_tickers,  # Default to the current selection
    help="Select or deselect tickers from your current selection."
)

# Text input for adding new tickers
new_ticker = st.sidebar.text_input(
    "Add a New Ticker:",
    "",
    help="Type a new ticker symbol to add to the list."
)
if new_ticker:
    if new_ticker not in current_tickers:
        current_tickers.append(new_ticker.upper())
    else:
        st.sidebar.warning(f"{new_ticker.upper()} is already in the list.")

# Update the selected tickers with the user's modifications
selected_tickers = current_tickers

# Display selected tickers
st.sidebar.write("Final Selected Tickers:")
st.sidebar.write(", ".join(selected_tickers))

def plot_cumulative_returns(initial_investment_dollars, result_df, title):
    try:
        fig = px.line(
            result_df,
            x="Time",
            y=f"Growth of ${initial_investment_dollars}",
            title=title,
            labels={"Time": "Time", f"Growth of ${initial_investment_dollars}": "Value"},
        )
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error in plotting cumulative returns: {e}")

if run_in_browser is False:
    selected_tickers = ["AAPL", "MSFT"]

# Fetch and display stock data
if st.sidebar.button("Run Optimization") or run_in_browser == False:
    if not selected_tickers:
        st.error("Please select at least one category of stocks.")
    else:
        st.write(f"Fetching data for: {selected_tickers}")
        st.write(f"Initial Investment: ${initial_investment:,}")
        try:
            data = get_stock_data(selected_tickers, start_date, end_date)
            st.line_chart(data)

            st.write("Optimizing Portfolio...")
            optimal_weights = optimize_portfolio(data, risk_measure, objective)

            st.write("Optimal Weights:")
            st.write(optimal_weights)

            # Growth of a Dollar Calculation
            growth_of_dollar = calculate_growth_of_dollar(data, optimal_weights, initial_investment)
            result_df = growth_of_dollar.reset_index()  # Convert Series to DataFrame
            result_df.columns = ["Time", f"Growth of ${initial_investment}"]  # Rename columns

            # Plot cumulative returns
            st.write(f"Growth of Initial Investment (${initial_investment:,}) Over Time:")
            plot_cumulative_returns(initial_investment, result_df, "Growth of Investment Over Time")
            # Interactive Pie Chart for Allocations
            # Pie chart of allocations
            fig, ax = plt.subplots(figsize=(6, 6))
            rp.plot_pie(
                w=optimal_weights,
                title="Optimized Portfolio Allocation",
                others=0.05,  # Combine smaller weights into "Others" category
                nrow=25,      # Maximum number of rows to show in legend
                ax=ax         # Use the created matplotlib axis
            )
            st.pyplot(fig)

        except Exception as e:
            st.error(f"An error occurred: {e}")
