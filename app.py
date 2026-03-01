import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
import pandas as pd

# 1. SET UP THE PAGE
st.set_page_config(page_title="Vibecoding: Taiwan Strait vs HSI", layout="wide")
st.title("📈 Hang Seng Index vs. Taiwan Strait News")
st.write("Tracking the 'vibes' between geopolitical news and the Hong Kong market.")

# 2. FETCH HANG SENG INDEX DATA
with st.spinner('Fetching market data...'):
    # We download 2 months to avoid 'weekend gaps' on the chart
    hsi_data = yf.download('^HSI', period='2mo', interval='1d')
    # Flatten the columns to avoid the 'blank chart' bug
    if not hsi_data.empty:
        hsi_data.columns = hsi_data.columns.get_level_values(0)

# 3. FETCH NEWS (MULTIPLE RSS FEEDS)
st.subheader("Latest Geopolitical Headlines")

# List of feeds for better coverage in 2026
feeds = [
    "https://feeds.bbci.co.uk",
    "https://www.taiwannews.com.tw",
    "https://www.aljazeera.com"
]

keywords = ["Taiwan", "China", "Military", "Strait", "PLA", "Drills", "Defense", "Naval", "Vessel", "Beijing", "Taipei", "Conflict"]

# Track if we found any news to avoid a blank screen
news_found = False

for url in feeds:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        # Check if any keyword is in the title
        if any(key.lower() in entry.title.lower() for key in keywords):
            news_found = True
            # Use 'getattr' to safely get the date if 'published' is missing
            date = getattr(entry, 'published', 'Recent')
            st.warning(f"**{date}**: {entry.title}")
            st.write(f"[Read more]({entry.link})")

if not news_found:
    st.info("No Taiwan Strait military news detected in the last few hours.")

# 4. CREATE THE CHART
st.subheader("Hang Seng Index (Recent Performance)")
if not hsi_data.empty:
    fig = go.Figure(data=[go.Candlestick(
        x=hsi_data.index,
        open=hsi_data['Open'],
        high=hsi_data['High'],
        low=hsi_data['Low'],
        close=hsi_data['Close']
    )])
    
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Could not load market data. Try refreshing.")

