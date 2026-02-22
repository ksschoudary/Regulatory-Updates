import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pytz
import math

# --- 1. EXECUTIVE THEME: MOSS & GOLD (YELLOW-GREEN) ---
st.set_page_config(page_title="Agri-Safety Command Center", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { font-family: 'EB Garamond', serif !important; }
    
    /* Executive Moss Green & Soft Yellow Palette */
    .stApp { background-color: #1a2421; color: #fdfae1; }
    
    .bento-card { 
        background-color: #26322e; border-radius: 4px; padding: 16px; 
        border: 1px solid #d4af37; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .headline-link { text-decoration: none; color: #ffffff !important; font-size: 17px; font-weight: 600; line-height: 1.3; }
    .meta-line { color: #d4af37; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 1.5px; }
    .section-header { border-bottom: 3px solid #d4af37; color: #d4af37; text-align: center; text-transform: uppercase; letter-spacing: 2px; padding-bottom: 10px; }
    .sync-text { font-size: 14px; color: #d4af37; font-weight: 600; text-align: right; }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL LOGIC: 28 COMMODITIES & ENFORCEMENT ---
COMMODITIES = [
    "Milk", "Paneer", "Ghee", "Khoya", "Edible Oil", "Mustard Oil", "Chana", "Wheat", "Sugar",
    "Maize", "Spices", "Chilli", "Turmeric", "Cashew", "Isabgol", "Paddy", "Rice Bran Oil",
    "Soyabean Oil", "Sunflower Oil", "Cotton Seed Oil", "Almond", "Raisins", "Oats", "Cocoa",
    "Cardamom", "Black Pepper", "Onion", "Potato"
]
COMM_STR = " OR ".join([f"'{c}'" for c in COMMODITIES])

# These keywords filter for the EXACT "crackdown" news you want
SURGICAL_TRIGGERS = "(seized OR raid OR crackdown OR confiscated OR fake OR 'safety test' OR adulteration OR misbranding OR 'Section 16')"
# Stricter Blocklist: removes US, global, and macro-policy noise
NOISE_BLOCKER = "-US -global -'national mission' -atmanirbhar -price -market -stocks -export -import -GeM -investment"

@st.cache_data(ttl=300)
def fetch_surgical_intel(query, limit=200):
    try:
        # location:India forces result focus
        full_query = f"{query} {NOISE_BLOCKER} location:India"
        url = f"https://news.google.com/rss/search?q={full_query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:m6"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def get_freshness_label(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    return f"{hours} hrs ago" if hours > 0 else f"{(diff.seconds // 60) % 60} mins ago"

# --- 3. HEADER & TIME-SYNC ---
ist = pytz.timezone('Asia/Kolkata')
last_sync = datetime.now(ist).strftime('%d %b %Y | %I:%M %p IST')

h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("<h2 style='color:#d4af37; margin:0;'>🛡️ AGRI-COMPLIANCE COMMAND CENTER</h2>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"<div class='sync-text'>Live Sync: {last_sync}</div>", unsafe_allow_html=True)
    if st.button("🔄 Force Refresh Data"):
        st.cache_data.clear()
        st.rerun()
st.write("---")

# --- 4. DATA ACQUISITION ---
# LEFT: Official FSSAI (Gazettes/Directives)
vault_data = fetch_surgical_intel(f"site:fssai.gov.in ({COMM_STR}) ({SURGICAL_TRIGGERS} OR circular OR sampling)")
# RIGHT: Enforcement News (Raids/Seizures from Times of India, Devdiscourse, etc.)
intel_data = [e for e in fetch_surgical_intel(f"({COMM_STR}) ({SURGICAL_TRIGGERS})") if "fssai.gov.in" not in e.link]

# --- 5. PAGINATION (75 PER PAGE) ---
PAGE_SIZE = 75
if 'page' not in st.session_state: st.session_state.page = 1
total_max = max(len(vault_data), len(intel_data))
max_pages = math.ceil(total_max / PAGE_SIZE) if total_max > 0 else 1
start_idx = (st.session_state.page - 1) * PAGE_SIZE
end_idx = start_idx + PAGE_SIZE

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>🏛️ FSSAI OFFICIAL MANDATES</h3>", unsafe_allow_html=True)
    for e in vault_data[start_idx:end_idx]:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>OFFICIAL | {dt.strftime('%d %b %Y')} | {get_freshness_label(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='section-header'>⚖️ RAIDS & ENFORCEMENT INTEL</h3>", unsafe_allow_html=True)
    for e in intel_data[start_idx:end_idx]:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>ACTION | {dt.strftime('%d %b %Y')} | {get_freshness_label(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

# Footer Pagination
if max_pages > 1:
    st.write("---")
    p_col1, p_col2, p_col3 = st.columns([1, 1, 1])
    with p_col2:
        st.write(f"Page {st.session_state.page} of {max_pages}")
        if st.session_state.page < max_pages and st.button("Next Page →"):
            st.session_state.page += 1; st.rerun()
