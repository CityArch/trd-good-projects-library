import streamlit as st
import pandas as pd
import os
import csv
import base64
from datetime import date

# 1. Page Configuration
st.set_page_config(page_title="TRD Digital Good Projects Library", page_icon="🏙️", layout="wide")

# --- HELPER: IMAGE TO BASE64 ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return ""
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
    .small-header {{ font-size: 1.1rem !important; font-weight: 600; color: #38BDF8; text-transform: uppercase; margin-bottom: 10px; }}
    section[data-testid="stSidebar"] {{ background-color: #1E293B !important; border-right: 1px solid #334155; }}
    .mono-text {{ font-family: 'Roboto Mono', monospace; font-size: 0.85rem; color: #94A3B8; }}
    div[data-testid="stVerticalBlock"] > div[style*="border"] {{
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px); border: 1px solid #334155 !important; border-radius: 12px !important;
    }}
    .stButton>button {{ border-radius: 8px; text-transform: uppercase; font-weight: 600; }}
    </style>
    """, unsafe_allow_html=True)

# --- CSV FIELDNAMES ---
FIELDNAMES = ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4', 'Project', 'Project ID', 'Cert Date', 'Approval Pack/NOC', 'Status']

# --- FILE OPERATIONS ---
def save_row(file_path, data_dict):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists: writer.writeheader()
        clean_dict = {k: str(data_dict.get(k, "")).replace("nan", "").strip() for k in FIELDNAMES}
        writer.writerow(clean_dict)

def load_csv_safe(file_path):
    if not os.path.exists(file_path): return pd.DataFrame()
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except:
        try: df = pd.read_csv(file_path, encoding='cp1252')
        except: return pd.DataFrame()
    df.columns = [str(c).strip().replace('ï»¿', '') for c in df.columns]
    return df.fillna("")

def update_queue_status(proj_id, status_val):
    df = load_csv_safe('review_queue.csv')
    if df.empty: return
    df.loc[df['Project ID'].astype(str).str.strip() == str(proj_id).strip(), 'Status'] = status_val
    df.to_csv('review_queue.csv', index=False, encoding='utf-8-sig')

def delete_from_review(proj_id):
    df = load_csv_safe('review_queue.csv')
    if df.empty: return
    df = df[df['Project ID'].astype(str).str.strip() != str(proj_id).strip()]
    df.to_csv('review_queue.csv', index=False, encoding='utf-8-sig')

@st.cache_data
def load_main_data():
    df = load_csv_safe('projects.csv')
    if df.empty: return pd.DataFrame()
    return df[df['Project'] != ""]

def check_password():
    if "password_correct" not in st.session_state: st.session_state.password_correct = False
    if st.session_state.password_correct: return True
    st.markdown("<div class='hero-section'><h1>🔒 TRD Project Library</h1></div>", unsafe_allow_html=True)
    with st.form("login"):
        pw = st.text_input("Access Token", type="password")
        if st.form_submit_button("UNLOCK"):
            if pw == "1234567890":
                st.session_state.password_correct = True
                st.rerun()
            else: st.error("Invalid credentials.")
    return False

# --- MAIN APP ---
if check_password():
    if "reset_key" not in st.session_state: st.session_state.reset_key = 0
    df_raw = load_main_data()
    
    st.markdown("<div class='hero-section'><h1>🏙️ GOOD PROJECTS LIBRARY</h1><p style='color:#38BDF8;'>NYC ZONING ANALYTICS TERMINAL</p></div>", unsafe_allow_html=True)

    # 3. Sidebar Filters
    st.sidebar.markdown("### 🛠️ SYSTEM FILTERS")
    search_mode = st.sidebar.radio("MODE", ["Single-Action Search", "Multi-Action Search"], key=f"mode_{st.session_state.reset_key}")
    
    final_l1, final_l2, final_l3 = [], [], []
    if not df_raw.empty:
        if search_mode == "Single-Action Search":
            l1_opts = ["All"] + sorted([str(x).strip() for x in df_raw['Level1'].dropna().unique() if str(x).strip()])
            c1 = st.sidebar.selectbox("L1", l1_opts, key=f"s1_{st.session_state.reset_key}")
            if c1 != "All":
                final_l1 = [c1]
                l2_opts = ["All"] + sorted([str(x).strip() for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique() if str(x).strip()])
                c2 = st.sidebar.selectbox("L2", l2_opts, key=f"s2_{st.session_state.reset_key}")
                if c2 != "All":
                    final_l2 = [c2]
                    l3_cols = ['Level3-1','Level3-2','Level3-3','Level3-4']
                    raw_l3 = df_raw[df_raw['Level2'] == c2][l3_cols].values.ravel('K')
                    l3_opts = ["All"] + sorted([str(x).strip() for x in pd.unique(raw_l3) if pd.notna(x) and str(x).strip()])
                    if len(l3_opts) > 1:
                        c3 = st.sidebar.selectbox("L3", l3_opts, key=f"s3_{st.session_state.reset_key}")
                        if c3 != "All": final_l3 = [c3]
        else:
            final_l1 = st.sidebar.multiselect("L1", sorted([str(x).strip() for x in df_raw['Level1'].dropna().unique() if str(x).strip()]), key=f"m1_{st.session_state.reset_key}")
            final_l2 = st.sidebar.multiselect("L2", sorted([str(x).strip() for x in df_raw['Level2'].dropna().unique() if str(x).strip()]), key=f"m2_{st.session_state.reset_key}")
            l3_cols_m = ['Level3-1','Level3-2','Level3-3','Level3-4']
            raw_l3_all = df_raw[l3_cols_m].values.ravel('K')
            final_l3 = st.sidebar.multiselect("L3", sorted([str(x).strip() for x in pd.unique(raw_l3_all) if pd.notna(x) and str(x).strip()]), key=f"m3_{st.session_state.reset_key}")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 EXECUTE SEARCH", use_container_width=True, type="primary"):
        st.session_state.search_clicked = True
    if st.sidebar.button("🧹 RESET SYSTEM", use_container_width=True):
        st.session_state.reset_key += 1
        st.session_state.search_clicked = False
        st.rerun()

    # 4. Search Results Display
    q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name or ID...", key=f"q_{st.session_state.reset_key}")
    
    if getattr(st.session_state, 'search_clicked', False) or q_search:
        df = df_raw.copy()
        
        # Standard filter logic