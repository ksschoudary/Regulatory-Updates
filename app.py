import streamlit as st
import feedparser
from datetime import datetime, timedelta
import math

# --- 1. EXECUTIVE THEME (MOSS & GOLD) ---
st.set_page_config(page_title="Food Safety Enforcement Deck", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { 
        font-family: 'EB Garamond', serif !important; 
    }
    .stApp { background-color: #1a2421; color: #f1f3f2; }
    .bento-card { 
        background-color: #26322e; border-radius: 4px; padding: 14px; 
        border: 1px solid #c5a059; margin-bottom: 10px;
    }
    .headline-link { text-decoration: none; color: #e9ecef !important; font-size: 16px; font-weight: 600; }
    .meta-line { color: #d4af37; font-size: 10.5px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 1px; }
    .section-header { border-bottom: 2px solid #c5a059; color: #c5a059; text-align: center; text-transform: uppercase; padding-bottom: 5px; }
    .stButton>button { background-color: #26322e; color: #c5a059; border: 1px solid #c5a059; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL SEARCH PARAMETERS ---
COMMODITIES = ["Wheat", "Chana", "Maize", "Cashew", "Isabgol", "Edible Oil", "Milk", "Rice", "Sugar", "Spices"]
COMM_STR = " OR ".join([f"'{c}'" for c in COMMODITIES])

# These keywords maximize reach for "Inspection & Prevention"
ENFORCEMENT_KEYWORDS = "inspection prevention sampling audit 'quality check' surveillance 'adulteration drive' 'sampling system'"

@st.cache_data(ttl=600)
def fetch_enforcement_data(query, limit=200):
    try:
        # Looking back 180 days (m6) for maximum context
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:m6"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def format_freshness(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    return f"{hours} hrs ago" if hours > 0 else f"{(diff.seconds // 60) % 60} mins ago"

# --- 3. DATA ACQUISITION ---
# LEFT: Official Vault (Direct FSSAI orders for inspections/sampling)
left_query = f"site:fssai.gov.in ({COMM_STR}) ({ENFORCEMENT_KEYWORDS} OR circular OR notification)"
vault_data = fetch_enforcement_data(left_query)

# RIGHT: Enforcement News (Raids, Sampling drives, Adulteration prevention)
right_query = f"({COMM_STR}) ({ENFORCEMENT_KEYWORDS}) -atmanirbhar -market -price"
intel_data = [e for e in fetch_enforcement_data(right_query) if "fssai.gov.in" not in e.link]

# --- 4. PAGINATION (75 ITEMS) ---
PAGE_SIZE = 75
if 'page' not in st.session_state: st.session_state.page = 1

def get_page_items(data):
    total = math.ceil(len(data) / PAGE_SIZE) if data else 1
    start = (st.session_state.page - 1) * PAGE_SIZE
    return data[start:start + PAGE_SIZE], total

v_items, v_total = get_page_items(vault_data)
i_items, i_total = get_page_items(intel_data)
max_p = max(v_total, i_total)

# --- 5. RENDER ---
st.markdown("<h2 style='text-align: center; color:#c5a059;'>🛡️ AGRI-QUALITY ENFORCEMENT DECK</h2>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>🏛️ FSSAI SAMPLING & AUDIT ORDERS</h3>", unsafe_allow_html=True)
    for e in v_items:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>OFFICIAL | {dt.strftime('%d %b %Y')} | {format_freshness(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='section-header'>⚖️ INSPECTION & PREVENTION INTEL</h3>", unsafe_allow_html=True)
    for e in i_items:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>DRIVE | {dt.strftime('%d %b %Y')} | {format_freshness(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

# Pagination Controls
st.write("---")
p_col1, p_col2, p_col3 = st.columns([1, 1, 1])
with p_col2:
    st.write(f"Displaying Page {st.session_state.page} of {max_p}")
    b1, b2 = st.columns(2)
    if st.session_state.page > 1:
        if b1.button("← Previous"): st.session_state.page -= 1; st.rerun()
    if st.session_state.page < max_p:
        if b2.button("Next →"): st.session_state.page += 1; st.rerun()
