import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pytz
import math

# --- 1. EXECUTIVE THEME: REFINED MOSS & GOLD ---
st.set_page_config(page_title="Agri-Compliance Command Center", layout="wide")

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
    .stButton>button { background-color: #d4af37; color: #1a2421; font-weight: 700; border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL LOGIC: PORTAL & KEYWORD LOCK ---
# Industry-specific portals for the Right Side
INDUSTRY_PORTALS = "(site:fnbnews.com OR site:agrofoodprocessing.com OR site:foodnavigator-asia.com)"

# High-impact regulatory keywords
REG_KEYWORDS = "(FSSAI OR 'FSSAI CEO' OR 'food safety' OR enforcement OR inspection OR review OR campaign OR obesity OR healthy OR 'Front-of-Pack Label' OR ban OR labelling OR measures OR efforts)"

# Mandatory Blocklist for Price/Market noise
NOISE_BLOCKER = "-rupee -spike -imports -volume -price -market -trade -atmanirbhar -economy -stocks -sensex -nifty"

@st.cache_data(ttl=600)
def fetch_compliance_intel(query, limit=150):
    try:
        # Strictly India-focused surgical search
        full_query = f"{query} {NOISE_BLOCKER} location:India"
        url = f"https://news.google.com/rss/search?q={full_query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:m6"
        feed = feedparser.parse(url)
        # Secondary logic check to kill any lingering macro-news
        filtered = [e for e in feed.entries if not any(x in e.title.lower() for x in ["price", "market", "import", "trade", "stock"])]
        return sorted(filtered, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def format_freshness(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    if hours > 0: return f"{hours} hrs ago"
    return f"{(diff.seconds // 60) % 60} mins ago"

# --- 3. PERSISTENT HEADER ---
ist = pytz.timezone('Asia/Kolkata')
last_sync = datetime.now(ist).strftime('%d %b %Y | %I:%M %p IST')

h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("<h2 style='color:#d4af37; margin:0;'>🛡️ AGRI-QUALITY COMMAND CENTER</h2>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"<div class='sync-text'>Sync: {last_sync}</div>", unsafe_allow_html=True)
    if st.button("🔄 Force Refresh Data"):
        st.cache_data.clear()
        st.rerun()
st.write("---")

# --- 4. DATA ACQUISITION ---
# LEFT SIDE: Deep Scan of FSSAI Website for all Agri/Food Advisories
left_query = "site:fssai.gov.in (Agri OR Food OR Product OR Standards OR Advisory OR Gazette OR Order OR Notification OR Laboratory OR Sampling OR 'Section 16')"
vault_data = fetch_compliance_intel(left_query)

# RIGHT SIDE: Portal-Specific Intelligence (FnB News / Agrofood Processing)
# Hunting for CEO directives, Campaigns, and Labeling Bans
right_query = f"{INDUSTRY_PORTALS} {REG_KEYWORDS}"
intel_data = [e for e in fetch_compliance_intel(right_query) if "fssai.gov.in" not in e.link]

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
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>OFFICIAL | {dt.strftime('%d %b %Y')} | {format_freshness(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='section-header'>⚖️ INDUSTRY & ENFORCEMENT INTEL</h3>", unsafe_allow_html=True)
    for e in intel_data[start:end]:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>CAMPAIGN | {dt.strftime('%d %b %Y')} | {format_freshness(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

# Page Control
if max_p > 1:
    if st.button("Next Page →"):
        st.session_state.page = (st.session_state.page % max_p) + 1
        st.rerun()
