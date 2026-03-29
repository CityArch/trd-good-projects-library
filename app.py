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

# 2. Data Loading
@st.cache_data
def load_data():
    file_path = 'projects.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except:
            df = pd.read_csv(file_path, encoding='cp1252')
        df.columns = [str(c).strip().replace('ï»¿', '') for c in df.columns]
        df = df[df['Project'].notna()]
        return df
    except Exception as e:
        st.error(f"Load Error: {e}")
        return pd.DataFrame()

# --- MAIN APP ---
if check_password():
    if "reset_key" not in st.session_state: st.session_state.reset_key = 0
    df_raw = load_data()

    if df_raw.empty:
        st.warning("⚠️ Database 'projects.csv' not found. Please ensure it is in your GitHub folder.")
        st.stop()

    st.markdown("<div class='hero-section'><h1>🏙️ GOOD PROJECTS LIBRARY</h1><p style='color:#38BDF8;'>NYC ZONING ANALYTICS TERMINAL</p></div>", unsafe_allow_html=True)

    # 3. Sidebar Filters
    st.sidebar.markdown("### 🛠️ SYSTEM FILTERS")
    search_mode = st.sidebar.radio("MODE", ["Single-Action Search", "Multi-Action Search"], key=f"m_mode_{st.session_state.reset_key}")

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
        
        l3_cols_m = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
        raw_l3_m = df_raw[l3_cols_m].values.ravel('K')
        all_l3 = sorted([str(x) for x in pd.unique(raw_l3_m) if pd.notna(x)])
        final_l3 = st.sidebar.multiselect("L3 FOCUS AREAS", all_l3, key=f"m3_{st.session_state.reset_key}")

    run_search = st.sidebar.button("🚀 EXECUTE SEARCH", use_container_width=True, type="primary")
    if st.sidebar.button("🧹 RESET", use_container_width=True):
        st.session_state.reset_key += 1
        st.rerun()

    # 4. Results Processing
    q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name or ID...", key=f"q_search_{st.session_state.reset_key}")

    if run_search or q_search or (search_mode == "Single-Action Search" and final_l1):
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
                    p_l1 = set(group['Level1'].dropna()); p_l2 = set(group['Level2'].dropna())
                    p_l3 = {str(x) for x in group[['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']].values.flatten() if pd.notna(x)}
                    m1 = all(i in p_l1 for i in final_l1) if final_l1 else True
                    m2 = all(i in p_l2 for i in final_l2) if final_l2 else True
                    m3 = all(i in p_l3 for i in final_l3) if final_l3 else True
                    return m1 and m2 and m3
                m_ids = df_raw.groupby('Project ID').filter(check_match)['Project ID'].unique()
                df = df_raw[df_raw['Project ID'].isin(m_ids)]

        if q_search:
            df = df[df['Project'].str.contains(q_search, case=False, na=False) | 
                    df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

        grouped = df.groupby('Project ID')
        st.subheader(f"SYSTEM FOUND {len(grouped)} PROJECTS")
        
        if not df.empty:
            grid = st.columns(3)
            for idx, (proj_id, group) in enumerate(grouped):
                first_row = group.iloc[0]
                hex_color = get_l1_color(str(first_row['Level1']))
                with grid[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"<div style='height:4px; width:40px; background-color:{hex_color}; margin-bottom:10px;'></div>", unsafe_allow_html=True)
                        st.markdown(f"### {first_row['Project']}")
                        st.markdown(f"<p class='mono-text'>ID: {proj_id} // CERT: {first_row['Cert Year']}</p>", unsafe_allow_html=True)
                        for _, row in group.iterrows():
                            l1 = str(row['Level1']); l2 = str(row['Level2'])
                            l3_v = [str(row[c]) for c in ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4'] if pd.notna(row[c])]
                            chain = f"{l1} > {l2}" + (f" > {', '.join(l3_v)}" if l3_v else "")
                            st.markdown(f"<p class='mono-text' style='color:{hex_color};'>• {chain}</p>", unsafe_allow_html=True)
                        zap = str(first_row['Approval Pack/NOC'])
                        if zap.startswith("http"): st.link_button("OPEN ZAP", zap, use_container_width=True)
        else:
            st.warning("No records match your query.")
    else:
        st.info("SYSTEM ONLINE. SELECT FILTERS TO BEGIN.")

    # 5. Submission Terminal
    st.divider()
    st.header("📩 DATA CONTRIBUTION")
    with st.expander("OPEN TERMINAL"):
        with st.form("f_sub", clear_on_submit=True):
            f_name = st.text_input("PROJECT NAME"); f_id = st.text_input("PROJECT ID")
            if st.form_submit_button("SUBMIT"):
                if f_name and f_id: st.success("Packet queued.")
                else: st.error("Incomplete packet.")
else:
    st.stop()