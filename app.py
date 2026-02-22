import streamlit as st
import feedparser
from datetime import datetime, timedelta
import math

# --- 1. EXECUTIVE UI CONFIGURATION (MOSS & GOLD) ---
st.set_page_config(page_title="Executive Compliance Deck", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { 
        font-family: 'EB Garamond', serif !important; 
    }
    .stApp { background-color: #1a2421; color: #f1f3f2; }
    .bento-card { 
        background-color: #26322e; border-radius: 4px; padding: 15px; 
        border: 1px solid #c5a059; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .headline-link { text-decoration: none; color: #e9ecef !important; font-size: 16.5px; font-weight: 600; }
    .meta-line { color: #d4af37; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 1px; }
    .section-header { border-bottom: 2px solid #c5a059; color: #c5a059; text-align: center; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { background-color: #26322e; color: #c5a059; border: 1px solid #c5a059; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE & FILTERS ---
COMMODITIES = ["Wheat", "Chana", "Maize", "Cashew", "Isabgol", "Edible Oil", "Milk", "Rice", "Sugar", "Spices", "Pulses"]
COMM_STR = " OR ".join([f"'{c}'" for c in COMMODITIES])

@st.cache_data(ttl=600)
def fetch_compliance_data(query, days=180, limit=200):
    try:
        # Strict exclusions to keep it focused
        excluded = "-atmanirbhar -market -sensex -stocks -budget -invest -price"
        full_query = f"{query} {excluded}"
        # Setting time range to roughly 180 days (6 months)
        url = f"https://news.google.com/rss/search?q={full_query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:m6"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def format_freshness(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    if hours > 0: return f"{hours} hrs ago"
    return f"{(diff.seconds // 60) % 60} mins ago"

def detect_commodity(title):
    for c in COMMODITIES:
        if c.lower() in title.lower(): return c.upper()
    return "AGRI-GEN"

# --- 3. DATA ACQUISITION ---
left_query = f"site:fssai.gov.in ({COMM_STR}) (circular OR notification OR gazette OR order)"
right_query = f"({COMM_STR}) (food safety adulteration govt safety measures actions regulator fssai mandate label nutrition)"

vault_data = fetch_compliance_data(left_query)
intel_data = [e for e in fetch_compliance_data(right_query) if "fssai.gov.in" not in e.link]

# --- 4. PAGINATION LOGIC (75 PER PAGE) ---
PAGE_SIZE = 75
if 'page' not in st.session_state: st.session_state.page = 1

def paginate(data):
    total_pages = math.ceil(len(data) / PAGE_SIZE) if data else 1
    start = (st.session_state.page - 1) * PAGE_SIZE
    return data[start:start + PAGE_SIZE], total_pages

vault_page, vault_total = paginate(vault_data)
intel_page, intel_total = paginate(intel_data)
max_pages = max(vault_total, intel_total)

# --- 5. RENDER ---
st.markdown("<h2 style='text-align: center; color:#c5a059;'>🛡️ AGRI-COMPLIANCE EXECUTIVE DECK</h2>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>🏛️ FSSAI OFFICIAL VAULT</h3>", unsafe_allow_html=True)
    for e in vault_page:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>{detect_commodity(e.title)} | OFFICIAL | {dt.strftime('%d %b %Y')} | {format_freshness(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='section-header'>⚖️ SAFETY & ENFORCEMENT</h3>", unsafe_allow_html=True)
    for e in intel_page:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>{detect_commodity(e.title)} | ACTION | {dt.strftime('%d %b %Y')} | {format_freshness(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

# Footer Pagination Controls
st.write("---")
page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
with page_col2:
    st.write(f"Page {st.session_state.page} of {max_pages}")
    btn_col1, btn_col2 = st.columns(2)
    if st.session_state.page > 1:
        if btn_col1.button("← Previous Page"):
            st.session_state.page -= 1
            st.rerun()
    if st.session_state.page < max_pages:
        if btn_col2.button("Next Page →"):
            st.session_state.page += 1
            st.rerun()
