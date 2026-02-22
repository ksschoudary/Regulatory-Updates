import streamlit as st
import feedparser
from datetime import datetime, timedelta

# --- 1. EXECUTIVE UI CONFIGURATION ---
st.set_page_config(page_title="Agri-Regulatory Command Center", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { 
        font-family: 'EB Garamond', serif !important; 
    }
    .stApp { background-color: #0a0e1a; color: #ffffff; }
    
    .bento-card { 
        background-color: #16213e; 
        border-radius: 8px; 
        padding: 15px; 
        border: 1px solid #1f2937; 
        margin-bottom: 12px;
    }
    .headline-link { 
        text-decoration: none; color: #e2e8f0 !important; 
        font-size: 16px; font-weight: 600; 
    }
    .meta-badge { 
        background-color: #0f3460; color: #ff9d5c; 
        padding: 2px 8px; border-radius: 4px; 
        font-size: 10px; font-weight: 700; 
        text-transform: uppercase; margin-bottom: 5px; display: inline-block;
    }
    .section-header {
        border-bottom: 2px solid #1f2937; padding-bottom: 8px;
        color: #4dabff; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. COMMODITY & SEARCH ENGINE ---
COMMODITIES = [
    "Wheat", "Maize", "Paddy", "Chana", "Palm Oil", "Potato", "Sugar", "Ethanol",
    "Rice bran oil", "Soyabean oil", "Sunflower oil", "Cotton seed oil", "Cashew", 
    "Almond", "Raisins", "Oats", "Psyllium", "Milk", "Cocoa", "Chilli", 
    "Turmeric", "Black pepper", "Cardamom", "Cabbage", "Ring beans", "Onion", 
    "Potato Mandi", "Groundnut"
]

@st.cache_data(ttl=600)
def fetch_compliance_data(query, time_range="m3", limit=30):
    try:
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:{time_range}"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: return []

# --- 3. SCRAPING LOGIC ---
# Create a mega-query for all 28 commodities to save API time
bulk_query = f"({' OR '.join(COMMODITIES)})"

# Left Side: Official FSSAI Circulars only
fssai_official = fetch_compliance_data(f"site:fssai.gov.in {bulk_query}", "y1", 25)

# Right Side: Regulatory Compliance & Safety News
safety_news = fetch_compliance_data(f"{bulk_query} (FSSAI compliance OR 'food safety' OR 'adulteration' OR 'mRL' OR 'labelling')", "m1", 25)

# --- 4. DASHBOARD RENDER ---
st.markdown("<h1 style='text-align: center;'>🏛️ Agri-Regulatory & FSSAI Compliance Deck</h1>", unsafe_allow_html=True)
st.write("---")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("<h3 class='section-header'>📜 Official FSSAI Circulars & Gazette</h3>", unsafe_allow_html=True)
    if fssai_official:
        for e in fssai_official:
            dt = datetime(*e.published_parsed[:6])
            st.markdown(f"""
            <div class='bento-card' style='border-left: 4px solid #ff9d5c;'>
                <span class='meta-badge'>FSSAI OFFICIAL | {dt.strftime('%d %b %Y')}</span><br>
                <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No new official circulars found for these commodities.")

with col_right:
    st.markdown("<h3 class='section-header'>⚖️ Safety & Compliance Intelligence</h3>", unsafe_allow_html=True)
    if safety_news:
        for e in safety_news:
            # Filter to ensure we don't duplicate official site results here
            if "fssai.gov.in" not in e.link:
                dt = datetime(*e.published_parsed[:6])
                st.markdown(f"""
                <div class='bento-card' style='border-left: 4px solid #4dabff;'>
                    <span class='meta-badge'>SAFETY NEWS | {dt.strftime('%d %b %Y')}</span><br>
                    <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No safety or compliance news detected for these commodities.")

# Persistent Footer for freshness check
st.markdown(f"<div style='text-align:center; color: #4b5563; margin-top: 50px;'>Data Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)
