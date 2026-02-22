import streamlit as st
import feedparser
from datetime import datetime, timedelta
import math

# --- 1. EXECUTIVE THEME: MOSS & GOLD ---
st.set_page_config(page_title="Agri-Regulatory Command Center", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { font-family: 'EB Garamond', serif !important; }
    .stApp { background-color: #1a2421; color: #f1f3f2; }
    
    .bento-card { 
        background-color: #26322e; border-radius: 4px; padding: 15px; 
        border: 1px solid #c5a059; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .headline-link { text-decoration: none; color: #f8fafc !important; font-size: 16.5px; font-weight: 600; }
    .meta-line { color: #d4af37; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 1px; }
    .section-header { border-bottom: 2px solid #c5a059; color: #c5a059; text-align: center; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { background-color: #c5a059; color: #1a2421; font-weight: 700; border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL SEARCH ENGINE ---
COMMODITIES = ["Wheat", "Chana", "Maize", "Cashew", "Isabgol", "Edible Oil", "Milk", "Rice", "Sugar", "Spices", "Pulses", "Paddy", "Potato", "Onion"]
COMM_STR = " OR ".join([f"'{c}'" for c in COMMODITIES])

@st.cache_data(ttl=300)
def fetch_compliance_data(query, time_range="m6", limit=150):
    try:
        # Strict exclusion of general market/political noise
        excluded = "-atmanirbhar -market -sensex -stocks -budget -invest -price -sensex -nifty"
        full_query = f"{query} {excluded}"
        url = f"https://news.google.com/rss/search?q={full_query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:{time_range}"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def get_freshness_label(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    if hours > 0: return f"{hours} hrs ago"
    return f"{(diff.seconds // 60) % 60} mins ago"

def detect_commodity(title):
    for c in COMMODITIES:
        if c.lower() in title.lower(): return c.upper()
    return "AGRI-GEN"

# --- 3. DATA PULLS (FEB 2026 FOCUS) ---
# LEFT: Official Vault (Direct FSSAI site notifications/Gazettes)
left_query = f"site:fssai.gov.in ({COMM_STR}) (circular OR notification OR gazette OR order OR labs)"
vault_data = fetch_compliance_data(left_query, "m6")

# RIGHT: Enforcement Drive (Inspection, Sampling, Audits, Adulteration, Safety Mandates)
# Focusing on FoSCORIS, Quality Inspections, and Surveillance
right_query = f"({COMM_STR}) (inspection OR sampling OR audit OR 'quality check' OR 'adulteration raid' OR 'food safety drive')"
intel_data = [e for e in fetch_compliance_data(right_query, "m6") if "fssai.gov.in" not in e.link]

# --- 4. PAGINATION LOGIC (75 PER PAGE) ---
PAGE_SIZE = 75
if 'page' not in st.session_state: st.session_state.page = 1

total_items = max(len(vault_data), len(intel_data))
max_pages = math.ceil(total_items / PAGE_SIZE) if total_items > 0 else 1
start_idx = (st.session_state.page - 1) * PAGE_SIZE
end_idx = start_idx + PAGE_SIZE

# --- 5. DASHBOARD RENDER ---
st.markdown("<h2 style='text-align: center; color:#c5a059;'>🛡️ AGRI-QUALITY & REGULATORY COMMAND CENTER</h2>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>🏛️ FSSAI OFFICIAL VAULT</h3>", unsafe_allow_html=True)
    page_vault = vault_data[start_idx:end_idx]
    for e in page_vault:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>{detect_commodity(e.title)} | OFFICIAL | {dt.strftime('%d %b %Y')} | {get_freshness_label(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

with col2:
    st.markdown("<h3 class='section-header'>⚖️ ENFORCEMENT & SAFETY INTEL</h3>", unsafe_allow_html=True)
    page_intel = intel_data[start_idx:end_idx]
    for e in page_intel:
        dt = datetime(*e.published_parsed[:6])
        st.markdown(f"""<div class='bento-card'><div class='meta-line'>{detect_commodity(e.title)} | ENFORCEMENT | {dt.strftime('%d %b %Y')} | {get_freshness_label(dt)}</div>
        <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a></div>""", unsafe_allow_html=True)

# Footer Pagination
st.write("---")
p_col1, p_col2, p_col3 = st.columns([1, 1, 1])
with p_col2:
    st.write(f"Displaying Page {st.session_state.page} of {max_pages}")
    b1, b2 = st.columns(2)
    if st.session_state.page > 1:
        if b1.button("← Previous"): st.session_state.page -= 1; st.rerun()
    if st.session_state.page < max_pages:
        if b2.button("Next →"): st.session_state.page += 1; st.rerun()
