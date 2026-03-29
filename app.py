import streamlit as st
import pandas as pd
from datetime import date

# 1. Page Configuration
st.set_page_config(
    page_title="TRD Digital Good Projects Library",
    page_icon="🏙️",
    layout="wide"
)

# --- TECH-SAVVY CSS INJECTION ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid #334155;
    }
    .mono-text {
        font-family: 'Roboto Mono', monospace;
        font-size: 0.85rem;
        color: #94A3B8;
    }
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px);
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }
    .stButton>button {
        border-radius: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- COLOR MAPPING ---
def get_l1_color(l1_name):
    mapping = {
        "Bulk_Waivers": "#38BDF8",
        "Use_Waivers": "#4ADE80",
        "Parking_Waivers": "#FB923C",
        "Housing_Actions": "#F87171",
        "Open_Space": "#FACC15"
    }
    return mapping.get(l1_name, "#94A3B8")

# --- PASSWORD PROTECTION ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    
    st.title("🔒 TRD Project Library")
    placeholder = st.empty()
    with placeholder.form("login_form"):
        st.caption("AUTHENTICATION REQUIRED")
        password = st.text_input("Access Token", type="password")
        if st.form_submit_button("UNLOCK DASHBOARD"):
            if password == "1234567890":
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("Invalid credentials.")
    return False

# 2. Data Loading
@st.cache_data
def load_data():
    file_path = 'projects.csv'
    try:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1252')
        df.columns = [str(c).strip() for c in df.columns]
        df = df[df['Project'].notna()]
        df = df[~df['Project'].str.contains("Insert your project name", na=False)]
        return df
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame()

# --- MAIN APP LOGIC ---
if check_password():
    
    if "reset_key" not in st.session_state: st.session_state.reset_key = 0
    if "search_active" not in st.session_state: st.session_state.search_active = False
    if "submitted_projects" not in st.session_state: st.session_state.submitted_projects = []
    if "temp_cats" not in st.session_state: st.session_state.temp_cats = []

    df_raw = load_data()

    # 3. Sidebar Filters
    st.sidebar.markdown("### 🛠️ SYSTEM FILTERS")
    search_mode = st.sidebar.radio("MODE", ["Single-Action Search", "Multi-Action Search"], key=f"m_{st.session_state.reset_key}")

    final_l1, final_l2, final_l3 = [], [], []

    if search_mode == "Single-Action Search":
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        c1 = st.sidebar.selectbox("CATEGORY (L1)", l1_opts, key=f"s1_{st.session_state.reset_key}")
        if c1 != "All":
            final_l1 = [c1]
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique()])
            c2 = st.sidebar.selectbox("SUB-CATEGORY (L2)", l2_opts, key=f"s2_{st.session_state.reset_key}")
            if c2 != "All":
                final_l2 = [c2]
                l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
                raw_l3 = df_raw[df_raw['Level2'] == c2][l3_cols].values.ravel('K')
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                if len(l3_opts) > 1:
                    c3 = st.sidebar.selectbox("FOCUS (L3)", l3_opts, key=f"s3_{st.session_state.reset_key}")
                    if c3 != "All": final_l3 = [c3]
    else:
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        final_l1 = st.sidebar.multiselect("L1 CATEGORIES", all_l1, key=f"m1_{st.session_state.reset_key}")
        all_l2 = sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
        final_l2 = st.sidebar.multiselect("L2 SUB-CATEGORIES", all_l2, key=f"m2_{st.session_state.reset_key}")
        raw_l3_m = df_raw[['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']].values.ravel('K')
        all_l3 = sorted([str(x) for x in pd.unique(raw_l3_m) if pd.notna(x)])
        final_l3 = st.sidebar.multiselect("L3 FOCUS AREAS", all_l3, key=f"m3_{st.session_state.reset_key}")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 EXECUTE SEARCH", use_container_width=True, type="primary"):
        st.session_state.search_active = True
    if st.sidebar.button("🧹 RESET", use_container_width=True):
        st.session_state.reset_key += 1
        st.session_state.search_active = False
        st.rerun()

    # 4. Results Gallery
    st.title("🏙️ GOOD PROJECTS LIBRARY")
    q_search = st.text_input("📝 KEYWORD SEARCH", key=f"q_{st.session_state.reset_key}", placeholder="Search project name or ID...")

    if st.session_state.search_active or q_search:
        df = df_raw.copy()
        
        if search_mode == "Single-Action Search":
            if final_l1: df = df[df['Level1'].isin(final_l1)]
            if final_l2: df = df[df['Level2'].isin(final_l2)]
            if final_l3:
                df = df[df['Level3-1'].isin(final_l3) | df['Level3-2'].isin(final_l3) | 
                        df['Level3-3'].isin(final_l3) | df['Level3-4'].isin(final_l3)]
        else:
            if final_l1 or final_l2 or final_l3:
                def check_match(group):
                    p_l1 = set(group['Level1'].dropna())
                    p_l2 = set(group['Level2'].dropna())
                    p_l3 = {str(x) for x in group[['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']].values.flatten() if pd.notna(x)}
                    return all(i in p_l1 for i in final_l1) and all(i in p_l2 for i in final_l2) and all(i in p_l3 for i in final_l3)
                m_ids = df_raw.groupby('Project ID').filter(check_match)['Project ID'].unique()
                df = df_raw[df_raw['Project ID'].isin(m_ids)]

        if q_search:
            df = df[df['Project'].str.contains(q_search, case=False, na=False) | 
                    df['Project ID'].astype(