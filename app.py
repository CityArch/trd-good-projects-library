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
                    df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

        grouped = df.groupby('Project ID')
        st.subheader(f"FOUND {len(grouped)} PROJECTS")
        
        if not df.empty:
            grid = st.columns(3)
            for idx, (proj_id, group) in enumerate(grouped):
                first_row = group.iloc[0]
                l1_val = str(first_row['Level1'])
                hex_color = get_l1_color(l1_val)
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
        st.subheader("1. Categorize Project")
        ca, cb, cc = st.columns(3)
        with ca: s1 = st.selectbox("L1", sorted(df_raw['Level1'].dropna().unique()), key="sl1")
        with cb: 
            s2_opts = sorted(df_raw[df_raw['Level1'] == s1]['Level2'].dropna().unique())
            s2_sel = st.selectbox("L2", s2_opts, key="sl2")
        with cc:
            raw_l3_sub = df_raw[df_raw['Level2'] == s2_sel][['Level3-1','Level3-2','Level3-3','Level3-4']].values.ravel('K')
            s3_list = sorted([str(x) for x in pd.unique(raw_l3_sub) if pd.notna(x)])
            s3_sel = st.multiselect("L3", s3_list, key="sl3")

        if st.button("➕ ADD CATEGORY"):
            cat_label = f"{s1} > {s2_sel}" + (f" ({', '.join(s3_sel)})" if s3_sel else "")
            if cat_label not in st.session_state.temp_cats:
                st.session_state.temp_cats.append(cat_label)
                st.toast("Category Added!")

        if st.session_state.temp_cats:
            st.write("**Selections:**")
            for cat in st.session_state.temp_cats: st.write(f"- {cat}")
            if st.button("🗑️ RESET CATEGORIES"):
                st.session_state.temp_cats = []
                st.rerun()

        st.markdown("---")
        st.subheader("2. Project Details")
        with st.form("f_sub", clear_on_submit=True):
            f_name = st.text_input("PROJECT NAME")
            f_id = st.text_input("PROJECT ID")
            f_desc = st.text_area("DESCRIPTION")
            f_link = st.text_input("ZAP LINK")
            f_date = st.date_input("CERT DATE", date.today())
            if st.form_submit_button("SUBMIT"):
                if f_name and f_id:
                    st.session_state.submitted_projects.append({
                        "name": f_name, "id": f_id, "desc": f_desc,
                        "link": f_link, "date": str(f_date),
                        "cats": st.session_state.temp_cats.copy()
                    })
                    st.session_state.temp_cats = []
                    st.success("Packet queued.")
                    st.rerun()
                else: st.error("Incomplete.")

    st.divider()
    st.caption("🔒 DATA PRIVACY: Professional pilot tool. Restricted access.")

else:
    st.stop()