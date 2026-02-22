import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pytz
import math

# --- 1. THE EXECUTIVE THEME: REFINED MOSS & GOLD ---
st.set_page_config(page_title="Agri-Compliance Command Center", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { font-family: 'EB Garamond', serif !important; }
    .stApp { background-color: #1a2421; color: #fdfae1; }
    .bento-card { 
        background-color: #26322e; border-radius: 4px; padding: 15px; 
        border: 1px solid #d4af37; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .headline-link { text-decoration: none; color: #ffffff !important; font-size: 16.5px; font-weight: 600; }
    .meta-line { color: #d4af37; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 1px; }
    .section-header { border-bottom: 3px solid #d4af37; color: #d4af37; text-align: center; text-transform: uppercase; letter-spacing: 2px; padding-bottom: 10px; }
    .sync-text { font-size: 14px; color: #d4af37; font-weight: 600; text-align: right; }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL DATA ENGINE: 28 COMMODITIES & NO PRICE NOISE ---
COMMODITIES = [
    "Milk", "Paneer", "Ghee", "Khoya", "Edible Oil", "Mustard Oil", "Chana", "Wheat", "Sugar",
    "Maize", "Spices", "Chilli", "Turmeric", "Cashew", "Isabgol", "Rice Bran Oil",
    "Soyabean Oil", "Sunflower Oil", "Almond", "Raisins", "Oats", "Cocoa", "Cardamom", "Black Pepper"
]
COMM_STR = " OR ".join([f"'{c}'" for c in COMMODITIES])

# FORCE focus on safety/enforcement; EXCLUDE all market/price noise
ENFORCEMENT_ONLY = "(seized OR raid OR crackdown OR confiscated OR fake OR 'safety test' OR adulteration OR misbranding OR 'Section 16' OR FoSCoS OR surveillance)"
STRICT_BLOCKER = "-rupee -imports -volume -price -trillion -crore -exchange -market -trade -atmanirbhar -economy -stocks -sensex -nifty"

@st.cache_data(ttl=600)
def fetch_enforcement_intel(query, limit=150):
    try:
        # location:India ensures regional focus
        full_query = f"{query} {STRICT_BLOCKER} location:India"
        url = f"https://news.google.com/rss/search?q={full_query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:m6"
        feed = feedparser.parse(url)
        # Double-pass manual filter to ensure zero price/market news slips through
        filtered = [e for e in feed.entries if not any(x in e.title.lower() for x in ["price", "market", "import", "rupee", "stock"])]
        return sorted(filtered, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def get_freshness_label(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    return f"{hours} hrs ago" if hours > 0 else f"{(diff.seconds // 60) % 60} mins ago"

# --- 3. HEADER & TIME-SYNC ---
ist_tz = pytz.timezone('Asia/Kolkata')
last_sync = datetime.now(ist_tz).strftime('%d %b %Y | %I:%M %p IST')

h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("<h2 style='color:#d4af37; margin:0;'>🛡️ AGRI-COMPLIANCE COMMAND CENTER</h2>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"<div class='sync-text'>Sync: {last_sync}</div>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Enforcement Feed"):
        st.cache_data.clear()
        st.rerun()
st.write("---")

# --- 4. DATA ACQUISITION ---
# LEFT: Official Vault (Direct FSSAI Orders)
vault_data = fetch_enforcement_intel(f"site:fssai.gov.in ({COMM_STR}) ({ENFORCEMENT_ONLY} OR circular OR sampling)")
# RIGHT: Enforcement News (Raids & Crackdowns)
intel_data = [e for e in fetch_enforcement_intel(f"({COMM_STR}) ({ENFORCEMENT_ONLY})") if "fssai.gov.in" not in e.link]

# --- 5. RENDER (PAGINATION: 75) ---
PAGE_SIZE = 75
if 'page' not in st.session_state: st.session_state.page = 1
total_max = max(len(vault_data), len(intel_data))
max_p = math.ceil(total_max / PAGE_SIZE) if total_max > 0 else 1
start, end = (st.session_state.page - 1) * PAGE_SIZE, st.session_state.page * PAGE_SIZE

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>🏛️ FSSAI OFFICIAL VAULT</h3>", unsafe_allow_html=True)
    for e in vault_data[start:end]:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>OFFICIAL | {dt.strftime('%d %b %Y')} | {get_freshness_label(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='section-header'>⚖️ RAIDS & ENFORCEMENT INTEL</h3>", unsafe_allow_html=True)
    for e in intel_data[start:end]:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>ACTION | {dt.strftime('%d %b %Y')} | {get_freshness_label(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

# Page Control
if max_p > 1:
    if st.button("Next Page →"):
        st.session_state.page = (st.session_state.page % max_p) + 1
        st.rerun()
