import streamlit as st
import feedparser
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(page_title="Regu-Agri Command Center", layout="wide")

# Custom CSS for the "Executive Deck" look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { font-family: 'EB Garamond', serif !important; }
    .stApp { background-color: #0a0e1a; color: #ffffff; }
    .bento-card { background-color: #16213e; border-radius: 12px; padding: 15px; border: 1px solid #1f2937; margin-bottom: 12px; }
    .headline-link { text-decoration: none; color: #ffffff !important; font-size: 15px; font-weight: 600; }
    .meta-badge { background-color: #0f3460; color: #ff9d5c; padding: 2px 8px; border-radius: 6px; font-size: 10.5px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# --- 2. CORE ENGINES ---
@st.cache_data(ttl=300)
def fetch_news(query, time_range="m3", limit=10):
    try:
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:{time_range}"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def get_time_diff(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days}d ago"
    hours = diff.seconds // 3600
    return f"{hours}h ago" if hours > 0 else f"{(diff.seconds // 60) % 60}m ago"

# --- 3. DATA ANCHORS ---
COMMODITIES = ["Wheat", "Chana", "Maize", "Cashew", "Isabgol", "Palm Oil", "Sugar"]
REG_KEYWORDS = "(FSSAI OR 'Import Duty' OR 'Export Policy' OR 'Stock Limit' OR 'DGFT')"

# --- 4. THE INTERFACE ---
st.title("🛡️ Regulatory & Agri-Intelligence Deck")

t1, t2 = st.tabs(["🏛️ Intelligence Pulse", "⚖️ Regulatory Deck"])

with t1:
    st.subheader("Live Commodity Pulse")
    cols = st.columns(len(COMMODITIES))
    for i, crop in enumerate(COMMODITIES):
        with cols[i]:
            st.markdown(f"**{crop}**")
            news = fetch_news(f"{crop} India", limit=5)
            for e in news:
                dt = datetime(*e.published_parsed[:6])
                st.markdown(f"<div class='bento-card'><span class='meta-badge'>{get_time_diff(dt)}</span><br><a href='{e.link}' target='_blank' class='headline-link'>{e.title[:50]}...</a></div>", unsafe_allow_html=True)

with t2:
    st.subheader("Regulatory Compliance & Policy Review")
    target = st.selectbox("Select Commodity for Review:", COMMODITIES)
    
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown(f"#### 📜 Latest Official Notifications: {target}")
        reg_news = fetch_news(f"{target} {REG_KEYWORDS}", limit=10)
        for e in reg_news:
            dt = datetime(*e.published_parsed[:6])
            st.markdown(f"<div class='bento-card' style='border-left: 4px solid #ff4b4b;'><span class='meta-badge'>POLICY | {get_time_diff(dt)}</span><br><b><a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></b></div>", unsafe_allow_html=True)
    
    with col_r:
        st.markdown("#### ⚖️ Impact Assessment")
        st.info(f"**Monitoring Checklist for {target}:**\n- Check FSSAI MRLs\n- Monitor DGFT Export Caps\n- Watch GST Council updates")
