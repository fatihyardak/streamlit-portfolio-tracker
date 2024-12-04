import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Define absolute file path
PORTFOLIO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portfolio_data.csv')

# Define the list of available assets at the top of your code
AVAILABLE_ASSETS = [
    'BTC-USD',  
    'AAPL',
    'GOOGL', 
    'MSFT', 
    'AMZN', 
    'TSLA', 
    'NVDA'
]

def load_portfolio():
    try:
        if os.path.exists(PORTFOLIO_FILE):
            df = pd.read_csv(PORTFOLIO_FILE)
            # Convert Purchase Date back to datetime
            df['Purchase Date'] = pd.to_datetime(df['Purchase Date']).dt.date
            return df
        return pd.DataFrame(columns=['Stock', 'Shares', 'Purchase Date', 'Purchase Price'])
    except Exception as e:
        st.error(f"Error loading portfolio: {str(e)}")
        return pd.DataFrame(columns=['Stock', 'Shares', 'Purchase Date', 'Purchase Price'])

def save_portfolio(portfolio_df):
    try:
        portfolio_df.to_csv(PORTFOLIO_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving portfolio: {str(e)}")
        return False

# Initialize portfolio from file
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_portfolio()

st.set_page_config(page_title="Portfolio Tracker", layout="wide")
st.title('My Stock Portfolio Tracker')

# Sidebar for adding new positions
st.sidebar.header('Add New Position')
new_stock = st.sidebar.selectbox(
    'Select Asset', 
    AVAILABLE_ASSETS,
    format_func=lambda x: 'Bitcoin' if x == 'BTC-USD' else x
)
shares = st.sidebar.number_input('Number of Shares', min_value=0.01, step=0.01)
purchase_date = st.sidebar.date_input('Purchase Date')
purchase_price = st.sidebar.number_input('Purchase Price per Share', min_value=0.01, step=0.01)

if st.sidebar.button('Add to Portfolio'):
    new_position = pd.DataFrame({
        'Stock': [new_stock],
        'Shares': [shares],
        'Purchase Date': [purchase_date],
        'Purchase Price': [purchase_price]
    })
    st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_position], ignore_index=True)
    if save_portfolio(st.session_state.portfolio):
        st.sidebar.success('Position added successfully!')
    else:
        st.sidebar.error('Failed to save position')

# Display current portfolio
if not st.session_state.portfolio.empty:
    st.subheader('Your Portfolio')
    
    # Get current prices
    current_prices = {}
    total_current_value = 0
    total_invested = 0
    
    portfolio_data = []
    
    for _, row in st.session_state.portfolio.iterrows():
        stock = yf.Ticker(row['Stock'])
        current_price = stock.history(period='1d')['Close'].iloc[-1]
        
        position_current_value = current_price * row['Shares']
        position_invested = row['Purchase Price'] * row['Shares']
        position_gain_loss = position_current_value - position_invested
        position_gain_loss_pct = (position_gain_loss / position_invested) * 100
        
        portfolio_data.append({
            'Stock': row['Stock'],
            'Shares': row['Shares'],
            'Purchase Date': row['Purchase Date'],
            'Purchase Price': f"${row['Purchase Price']:.2f}",
            'Current Price': f"${current_price:.2f}",
            'Initial Investment': f"${position_invested:.2f}",
            'Current Value': f"${position_current_value:.2f}",
            'Gain/Loss': f"${position_gain_loss:.2f}",
            'Return %': f"{position_gain_loss_pct:.2f}%"
        })
        
        total_current_value += position_current_value
        total_invested += position_invested
    
    # Display portfolio table
    portfolio_df = pd.DataFrame(portfolio_data)
    st.dataframe(portfolio_df, use_container_width=True)
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Invested", f"${total_invested:.2f}")
    with col2:
        st.metric("Current Value", f"${total_current_value:.2f}")
    with col3:
        total_return = ((total_current_value - total_invested) / total_invested) * 100
        st.metric("Total Return", f"{total_return:.2f}%")
    
    # Add a button to clear portfolio
    if st.button('Clear Portfolio'):
        st.session_state.portfolio = pd.DataFrame(columns=['Stock', 'Shares', 'Purchase Date', 'Purchase Price'])
        save_portfolio(st.session_state.portfolio)
        st.experimental_rerun()

else:
    st.info('Add your first position using the sidebar!')

# Debug information
st.sidebar.markdown("---")
st.sidebar.subheader("Debug Information")
st.sidebar.write(f"Portfolio file location: {PORTFOLIO_FILE}")
st.sidebar.write(f"File exists: {os.path.exists(PORTFOLIO_FILE)}")
if os.path.exists(PORTFOLIO_FILE):
    st.sidebar.write(f"File size: {os.path.getsize(PORTFOLIO_FILE)} bytes")