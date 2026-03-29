import streamlit as st
import pandas as pd
from datetime import date
import base64
import os

# 1. Page Configuration
st.set_page_config(
    page_title="TRD Digital Good Projects Library",
    page_icon="🏙️",
    layout="wide"
)

# --- HELPER: IMAGE TO BASE64 ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_base64 = get_base64_image("image.jpg")

# --- TECH-SAVVY CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; color: #F8FAFC; }}
    .hero-section {{
        background-image: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url("data:image/jpg;base64,{img_base64}");
        background-size: cover; background-position: center;
        padding: 60px 20px; border-radius: 15px; border: 1px solid #334155;
        text-align: center; margin-bottom: 30px;
    }}
    section[data-testid="stSidebar"] {{ background-color: #1E293B !important; border-right: 1px solid #334155; }}
    .mono-text {{ font-family: 'Roboto Mono', monospace; font-size: 0.85rem; color: #94A3B8; }}
    div[data-testid="stVerticalBlock"] > div[style*="border"] {{
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px); border: 1px solid #334155 !important; border-radius: 12px !important;
    }}
    .stButton>button {{ border-radius: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }}
    </style>
    """, unsafe_allow_html=True)

# --- COLOR MAPPING ---
def get_l1_color(l1_name):
    mapping = {
        "Bulk_Waivers": "#38BDF8", "Use_Waivers": "#4ADE80",
        "Parking_Waivers": "#FB923C", "Housing_Actions": "#F87171", "Open_Space": "#FACC15"
    }
    return mapping.get(l1_name, "#94A3B8")

# --- PASSWORD PROTECTION ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    st.markdown("<div class='hero-section'><h1>🔒 TRD Project Library</h1><p>RESTRICTED ACCESS TERMINAL</p></div>", unsafe_allow_html=True)
    with st.form("login_form"):
        password = st.text_input("Access Token", type="password")
        if st.form_submit_button("UNLOCK DASHBOARD"):
            if password == "1234567890":
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("Invalid credentials.")
    return False

# 2. Data Loading with KEYERROR FIX
@st.cache_data
def load_data():
    file_path = 'projects.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        # Use utf-8-sig to automatically handle hidden Excel characters (BOM)
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except:
            df = pd.read_csv(file_path, encoding='cp1252')
        
        # Clean headers: remove spaces, force strings, remove invisible markers
        df.columns = [str(c).strip().replace('ï»¿', '') for c in df.columns]
        
        # Safety check for Level1
        if 'Level1' not in df.columns:
            st.error(f"Critical Error: 'Level1' column not detected. Headers found: {list(df.columns)}")
            st.stop()
            
        return df[df['Project'].notna()]
    except Exception as e:
        st.error(f"Data Loading Error: {e}")
        return pd.DataFrame()

# --- MAIN APP ---
if check_password():
    if "reset_key" not in st.session_state: st.session_state.reset_key = 0
    if "search_clicked" not in st.session_state: st.session_state.search_clicked = False
    df_raw = load_data()

    if df_raw.empty:
        st.warning("⚠️ Database 'projects.csv' is empty or missing.")
        st.stop()

    st.markdown("<div class='hero-section'><h1>🏙️ GOOD PROJECTS LIBRARY</h1><p style='color:#38BDF8;'>NYC ZONING ANALYTICS TERMINAL</p></div>", unsafe_allow_html=True)

    # 3. Sidebar Filters
    st.sidebar.markdown("### 🛠️ SYSTEM FILTERS")
    search_mode = st.sidebar.radio("MODE", ["Single-Action Search", "Multi-Action Search"], key=f"m_mode_{st.session_state.reset_key}")

    final_l1, final_l2, final_l3 = [], [], []
    sub_logic = None

    if search_mode == "Single-Action Search":
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        c1 = st.sidebar.selectbox("L1 (Grandpa)", l1_opts, key=f"s1_{st.session_state.reset_key}")
        if c1 != "All":
            final_l1 = [c1]
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique()])
            c2 = st.sidebar.selectbox("L2 (Daddy)", l2_opts, key=f"s2_{st.session_state.reset_key}")
            if c2 != "All":
                final_l2 = [c2]
                l3_cols = ['Level3-1', 'Level