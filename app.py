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
    .submission-card {{ background: #1E293B; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #334155; }}
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

# 2. Data Loading with Header Cleaning
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
        
        required = ['Level1', 'Level2', 'Project', 'Project ID']
        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"Missing headers: {missing}. Found: {list(df.columns)}")
            st.stop()
            
        return df[df['Project'].notna()]
    except Exception as e:
        st.error(f"CSV Load Error: {e}")
        return pd.DataFrame()

# --- MAIN APP ---
if check_password():
    if "reset_key" not in st.session_state: st.session_state.reset_key = 0
    if "search_clicked" not in st.session_state: st.session_state.search_clicked = False
    if "submissions" not in st.session_state: st.session_state.submissions = []
    
    df_raw = load_data()
    st.markdown("<div class='hero-section'><h1>🏙️ GOOD PROJECTS LIBRARY</h1><p style='color:#38BDF8;'>NYC ZONING ANALYTICS TERMINAL</p></div>", unsafe_allow_html=True)

    # 3. Sidebar Filters
    st.sidebar.markdown("### 🛠️ SYSTEM FILTERS")
    search_mode = st.sidebar.radio("MODE", ["Single-Action Search", "Multi-Action Search"], key=f"m_mode_{st.session_state.reset_key}")

    final_l1, final_l2, final_l3 = [], [], []

    if search_mode == "Single-Action Search":
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        c1 = st.sidebar.selectbox("L1", l1_opts, key=f"s1_{st.session_state.reset_key}")
        if c1 != "All":
            final_l1 = [c1]
            l2_opts = ["All"] + sorted([str(x) for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique()])
            c2 = st.sidebar.selectbox("L2", l2_opts, key=f"s2_{st.session_state.reset_key}")
            if c2 != "All":
                final_l2 = [c2]
                l3_cols = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
                raw_l3 = df_raw[df_raw['Level2'] == c2][l3_cols].values.ravel('K')
                l3_opts = ["All"] + sorted([str(x) for x in pd.unique(raw_l3) if pd.notna(x)])
                if len(l3_opts) > 1:
                    c3 = st.sidebar.selectbox("L3", l3_opts, key=f"s3_{st.session_state.reset_key}")
                    if c3 != "All": final_l3 = [c3]
    else:
        all_l1 = sorted([str(x) for x in df_raw['Level1'].dropna().unique()])
        final_l1 = st.sidebar.multiselect("L1", all_l1, key=f"m1_{st.session_state.reset_key}")
        all_l2 = sorted([str(x) for x in df_raw['Level2'].dropna().unique()])
        final_l2 = st.sidebar.multiselect("L2", all_l2, key=f"m2_{st.session_state.reset_key}")
        l3_cols_m = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
        raw_l3_m = df_raw[l3_cols_m].values.ravel('K')
        all_l3 = sorted([str(x) for x in pd.unique(raw_l3_m) if pd.notna(x)])
        final_l3 = st.sidebar.multiselect("L3", all_l3, key=f"m3_{st.session_state.reset_key}")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 EXECUTE SEARCH", use_container_width=True, type="primary"):
        st.session_state.search_clicked = True
    if st.sidebar.button("🧹 RESET SYSTEM", use_container_width=True):
        st.session_state.reset_key += 1
        st.session_state.search_clicked = False
        st.rerun()

    # 4. Results Processing
    q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name or ID...", key=f"q_{st.session_state.reset_key}")

    if st.session_state.search_clicked or q_search:
        df = df_raw.copy()
        def check_global_and_match(group):
            project_pool = set()
            for col in ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']:
                project_pool.update(group[col].dropna().astype(str).str.strip().unique())
            search_items = set(final_l1) | set(final_l2) | set(final_l3)
            return search_items.issubset(project_pool)

        if final_l1 or final_l2 or final_l3:
            m_ids = df_raw.groupby('Project ID').filter(check_global_and_match)['Project ID'].unique()
            df = df_raw[df_raw['Project ID'].isin(m_ids)]

        if q_search:
            df = df[df['Project'].str.contains(q_search, case=False, na=False) | df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

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
                            l1, l2 = str(row['Level1']), str(row['Level2'])
                            l3_v = [str(row[c]) for c in ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4'] if pd.notna(row[c])]
                            chain = f"{l1} > {l2}" + (f" > {', '.join(l3_v)}" if l3_v else "")
                            st.markdown(f"<p class='mono-text' style='color:{hex_color};'>• {chain}</p>", unsafe_allow_html=True)
                        zap = str(first_row['Approval Pack/NOC'])
                        if zap.startswith("http"): st.link_button("OPEN ZAP", zap, use_container_width=True)

    # 5. DATA CONTRIBUTION TERMINAL
    st.divider()
    st.header("📩 DATA CONTRIBUTION")
    
    col_form, col_review = st.columns([1, 1])

    with col_form:
        st.markdown("### PROJECT ENTRY")
        with st.form("contribution_form", clear_on_submit=True):
            f_name = st.text_input("Project Name")
            f_id = st.text_input("Project ID")
            f_link = st.text_input("ZAP Link")
            f_year = st.selectbox("Cert Year", range(2000, 2027), index=26)
            f_month = st.selectbox("Cert Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
            
            # MULTI-ACTION STYLE CATEGORIZATION IN FORM
            all_f_l1 = sorted(df_raw['Level1'].dropna().unique())
            f_l1 = st.multiselect("L1 Categories", all_f_l1)
            
            all_f_l2 = sorted(df_raw['Level2'].dropna().unique())
            f_l2 = st.multiselect("L2 Sub-Categories", all_f_l2)
            
            l3_cols_f = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
            raw_l3_f = df_raw[l3_cols_f].values.ravel('K')
            all_f_l3 = sorted([str(x) for x in pd.unique(raw_l3_f) if pd.notna(x)])
            f_l3 = st.multiselect("L3 Focus Areas", all_f_l3)

            if st.form_submit_button("SUBMIT THE PROJECT"):
                if f_name and f_id:
                    new_entry = {
                        "id": len(st.session_state.submissions) + 1,
                        "name": f_name,
                        "proj_id": f_id,
                        "meta": f"{f_month} {f_year}",
                        "l1": f_l1,
                        "l2": f_l2,
                        "l3": f_l3
                    }
                    st.session_state.submissions.append(new_entry)
                    st.success("Entry added to review queue.")
                    st.rerun()
                else:
                    st.error("Name and ID are required.")

    with col_review:
        st.markdown("### REVIEW QUEUE")
        if not st.session_state.submissions:
            st.info("No pending entries.")
        else:
            for i, entry in enumerate(st.session_state.submissions):
                c_data, c_del = st.columns([0.85, 0.15])
                with c_data:
                    st.markdown(f"**{i+1}- {entry['name']}** (ID: {entry['proj_id']})")
                    st.markdown(f"<p class='mono-text'>{entry['meta']}</p>", unsafe_allow_html=True)
                    # Display categories with clean formatting
                    l1_s = f"L1: {', '.join(entry['l1'])}" if entry['l1'] else "L1: None"
                    l2_s = f"L2: {', '.join(entry['l2'])}" if entry['l2'] else "L2: None"
                    l3_s = f"L3: {', '.join(entry['l3'])}" if entry['l3'] else "L3: None"
                    st.markdown(f"<p class='mono-text' style='font-size:0.75rem;'>{l1_s} | {l2_s} | {l3_s}</p>", unsafe_allow_html=True)
                with c_del:
                    if st.button("🗑️", key=f"del_{entry['id']}"):
                        st.session_state.submissions.pop(i)
                        st.rerun()
                st.markdown("---")
else:
    st.stop()