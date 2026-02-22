import streamlit as st
import feedparser
from datetime import datetime, timedelta

# --- 1. EXECUTIVE UI CONFIGURATION ---
st.set_page_config(page_title="Regulatory Intelligence Hub", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');
    
    /* Global Font & Background */
    html, body, [class*="css"], .stMarkdown, p, div, h1, h2, h3, h4, h5, h6 { 
        font-family: 'EB Garamond', serif !important; 
    }
    .stApp { 
        background-color: #0a0e1a; 
        color: #ffffff; 
    }
    
    /* Executive Dashboard Cards */
    .bento-card { 
        background-color: #16213e; 
        border-radius: 8px; 
        padding: 18px; 
        border: 1px solid #1f2937; 
        margin-bottom: 15px;
        transition: transform 0.2s ease;
    }
    .bento-card:hover {
        border-color: #4dabff;
    }
    
    /* Typography Styling */
    .headline-link { 
        text-decoration: none; 
        color: #e2e8f0 !important; 
        font-size: 18px; 
        font-weight: 600; 
        line-height: 1.4;
    }
    .meta-badge { 
        background-color: #0f3460; 
        color: #ff9d5c; 
        padding: 3px 10px; 
        border-radius: 4px; 
        font-size: 11px; 
        font-weight: 700; 
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: inline-block;
    }
    .section-header {
        border-bottom: 1px solid #1f2937;
        padding-bottom: 10px;
        margin-bottom: 20px;
        color: #4dabff;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. INTELLIGENCE ENGINE ---
@st.cache_data(ttl=600)
def fetch_vault_data(query, time_range="m6", limit=20):
    try:
        # Precision routing to news.google RSS for specific site scraping
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en&tbs=qdr:{time_range}"
        feed = feedparser.parse(url)
        return sorted(feed.entries, key=lambda x: x.published_parsed, reverse=True)[:limit]
    except: 
        return []

def get_time_label(pub_date):
    diff = datetime.utcnow() - pub_date
    if diff.days > 0: return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    return f"{hours}h ago" if hours > 0 else "Just now"

# --- 3. DATA STRUCTURE ---
COMMODITIES = ["Wheat", "Chana", "Maize", "Cashew", "Isabgol", "Palm Oil", "Edible Oil"]
target_crop = st.sidebar.selectbox("Focus Commodity", COMMODITIES)

# --- 4. DASHBOARD LAYOUT ---
st.markdown(f"<h1 style='text-align: center;'>🛡️ {target_crop} Regulatory Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Official FSSAI Updates & Strategic Regulatory News</p>", unsafe_allow_html=True)
st.write("---")

col_left, col_right = st.columns(2)

# LEFT COLUMN: OFFICIAL FSSAI CIRCULARS
with col_left:
    st.markdown("<h3 class='section-header'>🏛️ Official FSSAI Circulars</h3>", unsafe_allow_html=True)
    
    # Surgical search: Restricts results to the official fssai.gov.in domain
    fssai_query = f"site:fssai.gov.in {target_crop}"
    circulars = fetch_vault_data(fssai_query, "y1", 15) # Scanning up to a year for circulars
    
    if circulars:
        for e in circulars:
            dt = datetime(*e.published_parsed[:6])
            st.markdown(f"""
            <div class='bento-card'>
                <span class='meta-badge'>OFFICIAL GAZETTE | {get_time_label(dt)}</span><br>
                <a href='{e.link}' target='_blank' class='headline-link'>{e.title.split(' - ')[0]}</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"No recent official FSSAI circulars found for {target_crop}.")

# RIGHT COLUMN: REGULATORY NEWS
with col_right:
    st.markdown("<h3 class='section-header'>⚖️ Regulatory & Policy News</h3>", unsafe_allow_html=True)
    
    # Broader search: Combines commodity with high-impact regulatory keywords
    reg_news_query = f"{target_crop} (FSSAI OR 'Import Duty' OR 'Export Ban' OR 'Stock Limit' OR 'DGFT Policy')"
    news_items = fetch_vault_data(reg_news_query, "m3", 15)
    
    if news_items:
        for e in news_items:
            dt = datetime(*e.published_parsed[:6])
            # Filter out the official site results to keep news distinct
            if "fssai.gov.in" not in e.link:
                st.markdown(f"""
                <div class='bento-card' style='border-left: 3px solid #4dabff;'>
                    <span class='meta-badge'>MARKET IMPACT | {get_time_label(dt)}</span><br>
                    <a href='{e.link}' target='_blank' class='headline-link'>{e.title}</a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(f"No regulatory news detected for {target_crop} in the last 90 days.")

# --- 5. EMERGENCY REFRESH ---
if st.sidebar.button("Force Sync Data"):
    st.cache_data.clear()
    st.rerun()
