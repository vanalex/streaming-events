import streamlit as st
import redis
import pandas as pd
import json
import time

r = redis.Redis(host="redis", port=6379, db=1, decode_responses=True)

st.set_page_config(page_title="Coinbase Ticker Live", layout="wide")
st.title("Live Ticker from Coinbase → Redpanda → Redis")

refresh = st.sidebar.slider("Refresh every (s)", 1, 5, 2)
pattern = st.sidebar.text_input("Key pattern", "ticker:*")
max_keys = st.sidebar.slider("Max keys to display", 10, 100, 50)

placeholder = st.empty()

def fetch_data():
    keys = list(r.scan_iter(match=pattern, count=max_keys))[:max_keys]
    rows = []
    for k in keys:
        try:
            data = r.hgetall(k)
            data['_key'] = k
            rows.append(data)
        except Exception as e:
            print(f"Error reading key {k}: {e}")

    if rows:
        df = pd.DataFrame(rows)
        # Sort by key (which includes timestamp) in descending order
        if '_key' in df.columns:
            df = df.sort_values('_key', ascending=False)
    else:
        df = pd.DataFrame()
    return df

while True:
    df = fetch_data()
    with placeholder.container():
        st.write(f"Showing {len(df)} keys matching pattern: {pattern}")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data available yet. Waiting for messages...")
    time.sleep(refresh)
