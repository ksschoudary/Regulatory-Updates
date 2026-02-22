import streamlit as st
import feedparser
from datetime import datetime, timedelta

# --- 1. EXECUTIVE UI CONFIGURATION ---
st.set_page_config(page_title="Regulatory & Food Safety Command Center", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { 
        font-family: 'EB Garamond', serif !important; 
    }
    .stApp { background-color: #0a0e1a; color: #ffffff; }
    
    .bento-card { 
        background-color: #16213e; 
        border-radius: 6px; 
        padding: 16px; 
        border: 1px solid #1f2937; 
        margin-bottom: 12px;
    }
    .headline-link { 
        text-decoration: none; color: #f8fafc !important; 
        font-size: 17px; font-weight: 600; 
    }
    .meta-badge { 
        background-color: #0f3460; color: #fbbf24; 
        padding: 2px 8px; border-radius: 3px; 
        font-size: 10px; font-weight: 700; 
        text-transform: uppercase; margin-bottom: 6px; display: inline-block;
    }
    .section-header {
        border-bottom: 2px solid #1e293b; padding-bottom: 10px;
        color: #60a5fa; text-align: center; font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL SEARCH ENGINE ---
COMMODITIES = "Wheat OR Chana OR Maize OR Cashew OR Isabgol OR 'Edible Oil' OR 'Rice' OR 'Milk'"

@st.cache_data(ttl=300)
def fetch_compliance(query, time_range="m1", limit=20):
    try:
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:{time_range}"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

# --- 3. DATA PULLS ---
# LEFT: Strictly Official FSSAI site updates (Latest Circulars/Gazettes)
left_query = f"site:fssai.gov.in ({COMMODITIES}) (circular OR notification OR gazette OR order)"
fssai_official = fetch_compliance(left_query, "m3", 15)

# RIGHT: Regulatory actions & Safety News (Filtered for specific keywords)
# Specifically excluding "atmanirbhar", "stock market", "price update"
right_query = f"({COMMODITIES}) (adulteration OR 'food safety' OR 'FSSAI mandate' OR 'labelling' OR 'safety measure' OR 'regulator action') -atmanirbhar -market -price -sensex"
safety_news = fetch_compliance(right_query, "m1", 15)

# --- 4. DASHBOARD RENDER ---
st.markdown("<h2 style='text-align: center;'>🛡️ FSSAI Regulatory & Safety Intelligence</h2>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>📜 Latest FSSAI Official Updates</h3>", unsafe_allow_html=True)
    if fssai_official:
        for e in fssai_official:
            dt = datetime(*e.published_parsed[:6])
            st.markdown(f"""
            <div class='bento-card' style='border-left: 4px solid #fbbf24;'>
                <span class='meta-badge'>OFFICIAL | {dt.strftime('%d %b %Y')}</span><br>
                <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Searching FSSAI.gov.in for latest February 2026 mandates...")

with col2:
    st.markdown("<h3 class='section-header'>⚖️ Compliance & Safety Actions</h3>", unsafe_allow_html=True)
    if safety_news:
        for e in safety_news:
            # Prevent duplication if FSSAI site appears in news results
            if "fssai.gov.in" not in e.link:
                dt = datetime(*e.published_parsed[:6])
                st.markdown(f"""
                <div class='bento-card' style='border-left: 4px solid #ef4444;'>
                    <span class='meta-badge'>SAFETY ALERT | {dt.strftime('%d %b %Y')}</span><br>
                    <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No major safety actions or adulteration reports detected in the last 30 days.")

# Freshness Marker
st.markdown(f"<p style='text-align:center; color: #475569; font-size: 12px;'>Last Sync: {datetime.now().strftime('%H:%M:%S')} IST</p>", unsafe_allow_html=True)
