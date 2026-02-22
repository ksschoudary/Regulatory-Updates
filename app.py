import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pytz
import math

# --- 1. THE EXECUTIVE THEME (MOSS & GOLD) ---
st.set_page_config(page_title="Agri-Compliance Command Center", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { font-family: 'EB Garamond', serif !important; }
    .stApp { background-color: #1a2421; color: #f1f3f2; }
    
    .bento-card { 
        background-color: #26322e; border-radius: 4px; padding: 16px; 
        border: 1px solid #c5a059; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .headline-link { text-decoration: none; color: #f8fafc !important; font-size: 16.5px; font-weight: 600; }
    .meta-line { color: #d4af37; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 1px; }
    .section-header { border-bottom: 2px solid #c5a059; color: #c5a059; text-align: center; text-transform: uppercase; letter-spacing: 2px; }
    .sync-text { font-size: 14px; color: #c5a059; font-weight: 600; text-align: right; }
    .stButton>button { background-color: #c5a059; color: #1a2421; font-weight: 700; border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL DATA ENGINE (FEB 2026 FOCUS) ---
COMMODITIES = [
    "Wheat", "Maize", "Paddy", "Chana", "Palm Oil", "Potato", "Sugar", "Ethanol",
    "Rice bran oil", "Soyabean oil", "Sunflower oil", "Cotton seed oil", "Cashew", 
    "Almond", "Raisins", "Oats", "Psyllium", "Milk", "Paneer", "Khoya", "Cocoa", 
    "Chilli", "Turmeric", "Black pepper", "Cardamom", "Cabbage", "Ring beans", "Onion", 
    "Groundnut", "Ghee"
]
COMM_STR = " OR ".join([f"'{c}'" for c in COMMODITIES])

# These keywords ensure we catch the 'Nationwide Crackdown' style news
ENFORCEMENT_DRIVE = "(crackdown OR 'Section 16' OR 'nationwide drive' OR adulteration OR misbranding OR analogue OR seizure OR 'licence cancellation' OR FoSCoS OR FoSCORIS)"

@st.cache_data(ttl=600)
def fetch_surgical_news(query, limit=150):
    try:
        # Strictly India focused, excludes Atmanirbhar/Markets/Stocks
        excluded = "-atmanirbhar -sensex -stocks -budget -invest -price"
        full_query = f"{query} {excluded} location:India"
        url = f"https://news.google.com/rss/search?q={full_query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:m6"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def format_freshness(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    return f"{hours} hrs ago" if hours > 0 else f"{(diff.seconds // 60) % 60} mins ago"

# --- 3. PERSISTENT HEADER ---
ist = pytz.timezone('Asia/Kolkata')
last_sync = datetime.now(ist).strftime('%d %b %Y | %I:%M %p IST')

h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("<h2 style='color:#c5a059; margin:0;'>🛡️ AGRI-QUALITY COMMAND CENTER</h2>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"<div class='sync-text'>Sync: {last_sync}</div>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

st.write("---")

# --- 4. DATA ACQUISITION ---
vault_data = fetch_surgical_news(f"site:fssai.gov.in ({COMM_STR}) ({ENFORCEMENT_DRIVE})")
intel_data = [e for e in fetch_surgical_news(f"({COMM_STR}) ({ENFORCEMENT_DRIVE})") if "fssai.gov.in" not in e.link]

# --- 5. RENDER (PAGINATION: 75) ---
PAGE_SIZE = 75
if 'page' not in st.session_state: st.session_state.page = 1
total_max = max(len(vault_data), len(intel_data))
max_pages = math.ceil(total_max / PAGE_SIZE) if total_max > 0 else 1
start_idx = (st.session_state.page - 1) * PAGE_SIZE
end_idx = start_idx + PAGE_SIZE

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>🏛️ FSSAI OFFICIAL DIRECTIVES</h3>", unsafe_allow_html=True)
    for e in vault_data[start_idx:end_idx]:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>OFFICIAL | {dt.strftime('%d %b %Y')} | {format_freshness(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='section-header'>⚖️ CRACKDOWNS & ENFORCEMENT NEWS</h3>", unsafe_allow_html=True)
    for e in intel_data[start_idx:end_idx]:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>ENFORCEMENT | {dt.strftime('%d %b %Y')} | {format_freshness(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

# Footer Pagination
if max_pages > 1:
    p_col1, p_col2, p_col3 = st.columns([1, 1, 1])
    with p_col2:
        st.write(f"Page {st.session_state.page} of {max_pages}")
        if st.session_state.page < max_pages and st.button("Next Page →"):
            st.session_state.page += 1
            st.rerun()
