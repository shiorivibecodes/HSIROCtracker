import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# 1. SET UP THE PAGE
st.set_page_config(page_title="Vibecoding: Taiwan Strait vs HSI", layout="wide")
st.title("📈 Hang Seng Index vs. Taiwan Strait News")
st.write("Tracking the 'vibes' between geopolitical news and the Hong Kong market.")
# Download the vibe dictionary
nltk.download('vader_lexicon')
analyzer = SentimentIntensityAnalyzer()

# Define the scoring function so it's ready to use later
def get_vibe_score(text):
    score = analyzer.polarity_scores(text)
    return score['compound']

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

# --- START REPLACEMENT ---
news_found = False
scores = [] # We'll store all the vibes here to calculate an average later

# Initialize the analyzer (Make sure you have nltk.download('vader_lexicon') at the top of your script!)
sia = SentimentIntensityAnalyzer()

for url in feeds:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        if any(key.lower() in entry.title.lower() for key in keywords):
            news_found = True
            
            # 1. CALCULATE THE VIBE
            vibe_score = sia.polarity_scores(entry.title)['compound']
            scores.append(vibe_score)
            
            # 2. CHOOSE COLOR BASED ON VIBE
            # Negative news (drills, conflict) usually scores below -0.1
            if vibe_score < -0.1:
                st.error(f"🔴 **Negative Vibe ({vibe_score})**")
            elif vibe_score > 0.1:
                st.success(f"🟢 **Positive Vibe ({vibe_score})**")
            else:
                st.info(f"⚪ **Neutral Vibe ({vibe_score})**")

            # 3. DISPLAY THE NEWS
            date = getattr(entry, 'published', 'Recent')
            st.write(f"**{date}**: {entry.title}")
            st.write(f"[Read more]({entry.link})")
            st.divider() # Adds a nice line between stories

# 4. SHOW THE TOTAL MARKET VIBE
if news_found:
    avg_vibe = sum(scores) / len(scores)
    # This creates a cool 'odometer' style display
    st.metric(label="Overall News Sentiment", value=f"{avg_vibe:.2f}", 
              delta="Tense" if avg_vibe < 0 else "Calm")

if not news_found:
    st.info("No Taiwan Strait military news detected in the last few hours.")
# --- END REPLACEMENT ---


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

