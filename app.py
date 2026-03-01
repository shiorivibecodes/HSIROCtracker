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
# We use '^HSI' which is the ticker symbol for the Hang Seng Index
with st.spinner('Fetching market data...'):
    hsi_data = yf.download('^HSI', period='1mo', interval='1d')

# 3. FETCH NEWS (RSS FEED)
# We are using a public news feed. In a 'pro' version, you'd use a search API.
# For now, we'll pull the latest World News to look for keywords.
st.subheader("Latest Relevant Headlines")
rss_url = "https://feeds.bbci.co.uk"
feed = feedparser.parse(rss_url)

# Keywords we want to highlight
keywords = ["Taiwan", "China", "Military", "Strait", "PLA", "Drills"]

for entry in feed.entries:
    # Check if any of our keywords are in the headline
    if any(key.lower() in entry.title.lower() for key in keywords):
        st.warning(f"**{entry.published}**: {entry.title}")
        st.write(f"[Read more]({entry.link})")

# 4. CREATE THE CHART
st.subheader("Hang Seng Index (Past 30 Days)")
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
