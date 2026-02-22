import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pytz
import math

# --- 1. EXECUTIVE THEME: REFINED MOSS & GOLD ---
st.set_page_config(page_title="High-Frequency Agri-Compliance Deck", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { font-family: 'EB Garamond', serif !important; }
    .stApp { background-color: #1a2421; color: #fdfae1; }
    .bento-card { 
        background-color: #26322e; border-radius: 4px; padding: 16px; 
        border: 1px solid #d4af37; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .headline-link { text-decoration: none; color: #ffffff !important; font-size: 17.5px; font-weight: 600; line-height: 1.3; }
    .meta-line { color: #d4af37; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 1.5px; }
    .section-header { border-bottom: 3px solid #d4af37; color: #d4af37; text-align: center; text-transform: uppercase; letter-spacing: 2px; padding-bottom: 10px; }
    .sync-text { font-size: 14px; color: #d4af37; font-weight: 600; text-align: right; }
    .fresh-tag { background-color: #ff4b4b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 8px; vertical-align: middle; }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL LOGIC: EXPANDED ENFORCEMENT PORTALS ---
# Added Inshorts, Republic, and ANI for high-impact enforcement news
ENFORCEMENT_PORTALS = "(site:fnbnews.com OR site:agrofoodprocessing.com OR site:republicworld.com OR site:inshorts.com OR site:aninews.in OR site:timesofindia.indiatimes.com)"

# Added 'crackdown', 'massive', 'UPFSDA', 'seized', 'raid' for high-impact alerts
REG_KEYWORDS = "(FSSAI OR 'FSSAI CEO' OR UPFSDA OR 'food safety' OR crackdown OR massive OR seizure OR raid OR inspection OR purity OR flags OR 'safety test' OR campaign OR ban OR labelling)"

MACRO_BLOCKER = "-rupee -spike -imports -volume -price -market -trade -atmanirbhar -economy -stocks -sensex -nifty"

@st.cache_data(ttl=60)
def fetch_ultra_fresh_intel(query, limit=150):
    try:
        full_query = f"{query} {MACRO_BLOCKER} location:India"
        url = f"https://news.google.com/rss/search?q={full_query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:m6"
        feed = feedparser.parse(url)
        filtered = [e for e in feed.entries if not any(x in e.title.lower() for x in ["price", "market", "trade", "import", "rupee"])]
        return sorted(filtered, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def format_freshness_detailed(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days}d ago", False
    hours = diff.seconds // 3600
    if hours > 0: return f"{hours}h ago", (hours < 12)
    mins = (diff.seconds // 60) % 60
    return f"{mins}m ago", True

# --- 3. PERSISTENT HEADER ---
ist = pytz.timezone('Asia/Kolkata')
last_sync = datetime.now(ist).strftime('%d %b %Y | %I:%M %p IST')

h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("<h2 style='color:#d4af37; margin:0;'>🛡️ AGRI-QUALITY COMMAND CENTER</h2>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"<div class='sync-text'>Live Sync: {last_sync}</div>", unsafe_allow_html=True)
    if st.button("🚀 Emergency Force Refresh"):
        st.cache_data.clear()
        st.rerun()
st.write("---")

# --- 4. DATA ACQUISITION ---
# LEFT SIDE: FSSAI Official Advisories
left_query = "site:fssai.gov.in (Agri OR Food OR Product OR Standards OR Advisory OR Gazette OR Order OR Notification OR Laboratory OR Sampling OR 'Section 16')"
vault_data = fetch_ultra_fresh_intel(left_query)

# RIGHT SIDE: Industry Portals + Enforcement Alerts (Republic/Inshorts/ANI)
right_query = f"{ENFORCEMENT_PORTALS} {REG_KEYWORDS}"
intel_data = [e for e in fetch_ultra_fresh_intel(right_query) if "fssai.gov.in" not in e.link]

# --- 5. RENDER (PAGINATION: 75) ---
PAGE_SIZE = 75
if 'page' not in st.session_state: st.session_state.page = 1
total_max = max(len(vault_data), len(intel_data))
max_p = math.ceil(total_max / PAGE_SIZE) if total_max > 0 else 1
start, end = (st.session_state.page - 1) * PAGE_SIZE, st.session_state.page * PAGE_SIZE

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>🏛️ FSSAI OFFICIAL ADVISORIES</h3>", unsafe_allow_html=True)
    for e in vault_data[start:end]:
        dt = datetime(*e.published_parsed[:6])
        label, is_hot = format_freshness_detailed(dt)
        fresh_tag = "<span class='fresh-tag'>HOT</span>" if is_hot else ""
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>OFFICIAL | {dt.strftime('%d %b %Y')} | {label} {fresh_tag}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='section-header'>⚖️ ENFORCEMENT & SAFETY INTEL</h3>", unsafe_allow_html=True)
    for e in intel_data[start:end]:
        dt = datetime(*e.published_parsed[:6])
        label, is_hot = format_freshness_detailed(dt)
        fresh_tag = "<span class='fresh-tag'>HOT</span>" if is_hot else ""
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>INTEL | {dt.strftime('%d %b %Y')} | {label} {fresh_tag}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

# Page Control
if max_p > 1:
    if st.button("Next Page →"):
        st.session_state.page = (st.session_state.page % max_p) + 1
        st.rerun()
