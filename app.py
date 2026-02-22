import streamlit as st
import feedparser
from datetime import datetime, timedelta

# --- 1. EXECUTIVE UI CONFIGURATION (MOSS & GOLD THEME) ---
st.set_page_config(page_title="Regu-Agri Command Center", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { 
        font-family: 'EB Garamond', serif !important; 
    }
    
    /* Background: Deep Executive Moss Green */
    .stApp { 
        background-color: #1a2421; 
        color: #f1f3f2; 
    }
    
    /* Cards: Muted Sage with Gold Border */
    .bento-card { 
        background-color: #26322e; 
        border-radius: 4px; 
        padding: 15px; 
        border: 1px solid #c5a059; /* Gold accent */
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .headline-link { 
        text-decoration: none; color: #e9ecef !important; 
        font-size: 16.5px; font-weight: 600; 
    }
    
    /* Metadata: Soft Gold/Yellow */
    .meta-line { 
        color: #d4af37; 
        font-size: 11px; 
        font-weight: 700; 
        text-transform: uppercase; 
        margin-bottom: 5px;
        letter-spacing: 1px;
    }
    
    .section-header {
        border-bottom: 2px solid #c5a059; 
        padding-bottom: 10px;
        color: #c5a059; 
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SURGICAL FILTER ENGINE ---
COMMODITIES = ["Wheat", "Chana", "Maize", "Cashew", "Isabgol", "Edible Oil", "Milk", "Rice", "Sugar", "Spices", "Pulses"]
COMM_STR = " OR ".join([f"'{c}'" for c in COMMODITIES])

@st.cache_data(ttl=300)
def fetch_compliance_data(query, time_range="m1", limit=25):
    try:
        # Added strict exclusions: -atmanirbhar -market -sensex -stocks -budget
        excluded = "-atmanirbhar -market -sensex -stocks -budget -invest -price"
        full_query = f"{query} {excluded}"
        url = f"https://news.google.com/rss/search?q={full_query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:{time_range}"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

def get_freshness(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days}D"
    hours = diff.seconds // 3600
    return f"{hours}H" if hours > 0 else "NEW"

def detect_commodity(title):
    for c in COMMODITIES:
        if c.lower() in title.lower(): return c.upper()
    return "AGRI-GEN"

# --- 3. DATA PULLS ---
# LEFT: Strictly FSSAI.gov.in (Gazettes/Notifications)
left_query = f"site:fssai.gov.in ({COMM_STR}) (circular OR notification OR gazette OR order)"
fssai_vault = fetch_compliance_data(left_query, "m6", 15)

# RIGHT: Safety & Adulteration Mandates
safety_keywords = "food safety adulteration govt safety measures actions regulator fssai mandate label nutrition"
right_query = f"({COMM_STR}) ({safety_keywords})"
safety_intel = fetch_compliance_data(right_query, "m1", 20)

# --- 4. DASHBOARD RENDER ---
st.markdown("<h2 style='text-align: center; color:#c5a059;'>🛡️ FSSAI REGULATORY COMPLIANCE DECK</h2>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>🏛️ OFFICIAL FSSAI NOTIFICATIONS</h3>", unsafe_allow_html=True)
    if fssai_vault:
        for e in fssai_vault:
            dt = datetime(*e.published_parsed[:6])
            comm = detect_commodity(e.title)
            st.markdown(f"""
            <div class='bento-card'>
                <div class='meta-line'>{comm} | OFFICIAL | {dt.strftime('%d %b %Y')} | {get_freshness(dt)}</div>
                <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No new official circulars found in the FSSAI vault.")

with col2:
    st.markdown("<h3 class='section-header'>⚖️ SAFETY & ADULTERATION INTEL</h3>", unsafe_allow_html=True)
    if safety_intel:
        for e in safety_intel:
            # Avoid duplicating FSSAI.gov results in the news column
            if "fssai.gov.in" not in e.link:
                dt = datetime(*e.published_parsed[:6])
                comm = detect_commodity(e.title)
                st.markdown(f"""
                <div class='bento-card'>
                    <div class='meta-line'>{comm} | SAFETY ACTION | {dt.strftime('%d %b %Y')} | {get_freshness(dt)}</div>
                    <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No safety actions detected for the selected commodities.")

st.markdown(f"<p style='text-align:center; color: #7a8a84; font-size: 11px;'>SYNCHRONIZED: {datetime.now().strftime('%H:%M:%S')} IST</p>", unsafe_allow_html=True)
