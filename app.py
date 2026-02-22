import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pytz
import math

# --- 1. EXECUTIVE THEME: MOSS & GOLD ---
st.set_page_config(page_title="Agri-Safety Enforcement Deck", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { font-family: 'EB Garamond', serif !important; }
    .stApp { background-color: #1a2421; color: #f1f3f2; }
    
    .bento-card { 
        background-color: #26322e; border-radius: 4px; padding: 16px; 
        border: 1px solid #c5a059; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .headline-link { text-decoration: none; color: #f8fafc !important; font-size: 17px; font-weight: 600; line-height: 1.3; }
    .meta-line { color: #d4af37; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 1px; }
    .section-header { border-bottom: 2px solid #c5a059; color: #c5a059; text-align: center; text-transform: uppercase; letter-spacing: 2px; }
    .sync-text { font-size: 14px; color: #c5a059; font-weight: 600; text-align: right; }
    .stButton>button { background-color: #c5a059; color: #1a2421; font-weight: 700; border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL PARAMETERS ---
COMMODITIES = [
    "Milk", "Paneer", "Ghee", "Khoya", "Edible Oil", "Mustard Oil", "Pulses", "Chana", 
    "Wheat", "Maize", "Spices", "Chilli", "Turmeric", "Cashew", "Isabgol", "Sugar", "Honey"
]
# Focus purely on Enforcement, Safety Violations, and Raids
SAFETY_TRIGGERS = "(raid OR seized OR confiscated OR crackdown OR 'fake unit' OR adulteration OR 'tainted food' OR 'expired stock' OR 'safety violation')"
# Strictly block unwanted noise
NOISE_BLOCKER = "-US -global -'national mission' -atmanirbhar -PIB -price -market -stocks -investment -export -import"

@st.cache_data(ttl=600)
def fetch_enforcement_intel(query, limit=150):
    try:
        # location:India ensures we don't get US/Global data
        full_query = f"{query} {NOISE_BLOCKER} location:India"
        url = f"https://news.google.com/rss/search?q={full_query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:m6"
        feed = feedparser.parse(url)
        # Filter again to ensure no 'National Mission' or 'US' results survived the RSS query
        filtered_entries = [e for e in feed.entries if not any(x in e.title.lower() for x in ["national mission", "atmanirbhar", "global", "us fda"])]
        return sorted(filtered_entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def format_freshness(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    return f"{hours} hrs ago" if hours > 0 else f"{(diff.seconds // 60) % 60} mins ago"

# --- 3. HEADER & SYNC ---
ist = pytz.timezone('Asia/Kolkata')
last_sync = datetime.now(ist).strftime('%d %b %Y | %I:%M %p IST')

h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("<h2 style='color:#c5a059; margin:0;'>🛡️ AGRI-QUALITY & ADULTERATION WATCH</h2>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"<div class='sync-text'>Live Sync: {last_sync}</div>", unsafe_allow_html=True)
    if st.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()
st.write("---")

# --- 4. DATA PULLS ---
comm_query = " OR ".join([f"'{c}'" for c in COMMODITIES])
# LEFT: Official FSSAI Orders specifically about Enforcement/Sampling
vault_data = fetch_enforcement_intel(f"site:fssai.gov.in ({comm_query}) ({SAFETY_TRIGGERS} OR 'Section 16' OR sampling)")
# RIGHT: Enforcement News (Raids and Seizures from TOI, Devdiscourse, etc.)
intel_data = [e for e in fetch_enforcement_intel(f"({comm_query}) ({SAFETY_TRIGGERS})") if "fssai.gov.in" not in e.link]

# --- 5. RENDER (PAGINATION: 75) ---
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
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>OFFICIAL | {dt.strftime('%d %b %Y')} | {format_freshness(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='section-header'>⚖️ RAIDS, SEIZURES & CRACKDOWNS</h3>", unsafe_allow_html=True)
    for e in intel_data[start_idx:end_idx]:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>ACTION | {dt.strftime('%d %b %Y')} | {format_freshness(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

# Footer
if max_pages > 1:
    st.write("---")
    p_col1, p_col2, p_col3 = st.columns([1, 1, 1])
    with p_col2:
        st.write(f"Page {st.session_state.page} of {max_pages}")
        if st.session_state.page < max_pages and st.button("Next Page →"):
            st.session_state.page += 1
            st.rerun()
