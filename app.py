import streamlit as st
import feedparser
from datetime import datetime, timedelta

# --- 1. EXECUTIVE UI CONFIGURATION ---
st.set_page_config(page_title="Regu-Agri Command Center", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { 
        font-family: 'EB Garamond', serif !important; 
    }
    .stApp { background-color: #0a0e1a; color: #ffffff; }
    
    .bento-card { 
        background-color: #16213e; 
        border-radius: 4px; 
        padding: 14px; 
        border: 1px solid #1f2937; 
        margin-bottom: 10px;
    }
    .headline-link { 
        text-decoration: none; color: #f1f5f9 !important; 
        font-size: 16px; font-weight: 600; 
    }
    .meta-line { 
        color: #fbbf24; 
        font-size: 11px; 
        font-weight: 700; 
        text-transform: uppercase; 
        margin-bottom: 4px; 
        letter-spacing: 0.5px;
    }
    .section-header {
        border-bottom: 2px solid #1e293b; padding-bottom: 8px;
        color: #60a5fa; text-align: center; font-size: 22px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL LOGIC ---
COMMODITIES_LIST = ["Wheat", "Chana", "Maize", "Cashew", "Isabgol", "Edible Oil", "Milk", "Rice", "Sugar", "Spices"]
COMMODITIES_STR = " OR ".join([f"'{c}'" for c in COMMODITIES_LIST])

@st.cache_data(ttl=300)
def fetch_vault_data(query, time_range="m1", limit=20):
    try:
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:{time_range}"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def get_freshness(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days}D"
    hours = diff.seconds // 3600
    return f"{hours}H" if hours > 0 else "NEW"

def detect_commodity(title):
    for c in COMMODITIES_LIST:
        if c.lower() in title.lower(): return c.upper()
    return "AGRI-GEN"

# --- 3. DATA SCRAPING ---
# Left Side: Official FSSAI (Latest February 2026 Circulars/Gazettes)
left_query = f"site:fssai.gov.in ({COMMODITIES_STR}) (circular OR notification OR gazette OR order)"
fssai_official = fetch_vault_data(left_query, "m3", 15)

# Right Side: Pure Compliance/Safety (No Market/Atmanirbhar noise)
safety_keywords = "food safety adulteration govt safety measures actions regulator fssai mandate label nutrition"
right_query = f"({COMMODITIES_STR}) ({safety_keywords}) -atmanirbhar -market -price -sensex -stocks"
safety_news = fetch_vault_data(right_query, "m1", 20)

# --- 4. DASHBOARD RENDER ---
st.markdown("<h2 style='text-align: center; letter-spacing: 2px;'>🛡️ FSSAI REGULATORY INTELLIGENCE DECK</h2>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>🏛️ OFFICIAL FSSAI VAULT</h3>", unsafe_allow_html=True)
    for e in fssai_official:
        dt = datetime(*e.published_parsed[:6])
        comm = detect_commodity(e.title)
        st.markdown(f"""
        <div class='bento-card'>
            <div class='meta-line'>{comm} | OFFICIAL | {dt.strftime('%d %b %Y')} | {get_freshness(dt)}</div>
            <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='section-header'>⚖️ SAFETY & REGULATORY ACTIONS</h3>", unsafe_allow_html=True)
    for e in safety_news:
        if "fssai.gov.in" not in e.link:
            dt = datetime(*e.published_parsed[:6])
            comm = detect_commodity(e.title)
            st.markdown(f"""
            <div class='bento-card' style='border-left: 3px solid #60a5fa;'>
                <div class='meta-line'>{comm} | ACTION | {dt.strftime('%d %b %Y')} | {get_freshness(dt)}</div>
                <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a>
            </div>
            """, unsafe_allow_html=True)

st.markdown(f"<p style='text-align:center; color: #475569; font-size: 11px; margin-top: 30px;'>LIVE SYNC: {datetime.now().strftime('%H:%M:%S')} IST</p>", unsafe_allow_html=True)
