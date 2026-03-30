import streamlit as st
import pandas as pd
import os
import csv
import base64

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
    .small-header {{
        font-size: 1.2rem !important;
        font-weight: 600;
        margin-bottom: 15px;
        color: #38BDF8;
        text-transform: uppercase;
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

# --- CSV FIELDNAMES ---
FIELDNAMES = ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4', 'Project', 'Project ID', 'Cert Year', 'Approval Pack/NOC']

# --- FILE OPERATIONS ---
def save_row(file_path, data_dict):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists: writer.writeheader()
        writer.writerow(data_dict)

def load_csv_safe(file_path):
    if not os.path.exists(file_path): return pd.DataFrame()
    try:
        return pd.read_csv(file_path, encoding='utf-8-sig')
    except:
        try: return pd.read_csv(file_path, encoding='cp1252')
        except: return pd.DataFrame()

def delete_from_review(proj_id):
    df = load_csv_safe('review_queue.csv')
    if df.empty: return
    df = df[df['Project ID'].astype(str) != str(proj_id)]
    df.to_csv('review_queue.csv', index=False, encoding='utf-8-sig')

@st.cache_data
def load_main_data():
    df = load_csv_safe('projects.csv')
    if df.empty: return pd.DataFrame()
    df.columns = [str(c).strip().replace('ï»¿', '') for c in df.columns]
    return df[df['Project'].notna()]

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

    if search_mode == "Single-Action Search":
        l1_opts = ["All"] + sorted([str(x) for x in df_raw['Level1'].dropna().unique()]) if not df_raw.empty else ["All"]
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
        all_l1 = sorted(df_raw['Level1'].dropna().unique()) if not df_raw.empty else []
        final_l1 = st.sidebar.multiselect("L1", all_l1, key=f"m1_{st.session_state.reset_key}")
        all_l2 = sorted(df_raw['Level2'].dropna().unique()) if not df_raw.empty else []
        final_l2 = st.sidebar.multiselect("L2", all_l2, key=f"m2_{st.session_state.reset_key}")
        l3_cols_m = ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
        all_l3 = sorted([str(x) for x in pd.unique(df_raw[l3_cols_m].values.ravel('K')) if pd.notna(x)]) if not df_raw.empty else []
        final_l3 = st.sidebar.multiselect("L3", all_l3, key=f"m3_{st.session_state.reset_key}")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 EXECUTE SEARCH", use_container_width=True, type="primary"):
        st.session_state.search_clicked = True
    if st.sidebar.button("🧹 RESET SYSTEM", use_container_width=True):
        st.session_state.reset_key += 1
        st.session_state.search_clicked = False
        st.rerun()

    # 4. Results Section
    q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name or ID...", key=f"q_{st.session_state.reset_key}")

    if getattr(st.session_state, 'search_clicked', False) or q_search:
        df = df_raw.copy()
        def check_match(group):
            pool = set()
            for col in ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']:
                pool.update(group[col].dropna().astype(str).unique())
            search_items = set(final_l1) | set(final_l2) | set(final_l3)
            return search_items.issubset(pool)
        
        if final_l1 or final_l2 or final_l3:
            m_ids = df_raw.groupby('Project ID').filter(check_match)['Project ID'].unique()
            df = df_raw[df_raw['Project ID'].isin(m_ids)]
        
        if q_search:
            df = df[df['Project'].str.contains(q_search, case=False, na=False) | df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

        grouped = df.groupby('Project ID')
        st.subheader(f"SYSTEM FOUND {len(grouped)} PROJECTS")
        
        if not df.empty:
            grid = st.columns(3)
            for idx, (proj_id, group) in enumerate(grouped):
                first_row = group.iloc[0]
                with grid[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {first_row['Project']}")
                        st.markdown(f"<p class='mono-text'>ID: {proj_id} | {first_row['Cert Year']}</p>", unsafe_allow_html=True)
                        # ALWAYS SHOW CHAINS
                        for _, row in group.iterrows():
                            l3_v = [str(row[c]) for c in ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4'] if pd.notna(row[c])]
                            chain = f"{row['Level1']} > {row['Level2']}" + (f" > {', '.join(l3_v)}" if l3_v else "")
                            st.markdown(f"<p class='mono-text'>• {chain}</p>", unsafe_allow_html=True)
                        zap = str(first_row['Approval Pack/NOC'])
                        if zap.startswith("http"): st.link_button("OPEN ZAP", zap, use_container_width=True)

    # 5. DATA CONTRIBUTION & ADMIN REVIEW (Always Visible)
    st.divider()
    col_entry, col_admin = st.columns([1, 1.2])

    with col_entry:
        st.markdown("<p class='small-header'>📩 New Submission</p>", unsafe_allow_html=True)
        with st.form("sub_form", clear_on_submit=True):
            n_name = st.text_input("Project Name")
            n_id = st.text_input("Project ID")
            n_year = st.selectbox("Cert Year", range(2000, 2028), index=26)
            
            l1_list = sorted(df_raw['Level1'].dropna().unique()) if not df_raw.empty else []
            n_l1 = st.selectbox("L1", l1_list)
            
            l2_list = sorted(df_raw[df_raw['Level1'] == n_l1]['Level2'].dropna().unique()) if not df_raw.empty else []
            n_l2 = st.selectbox("L2", l2_list)
            
            l3_list = sorted([str(x) for x in pd.unique(df_raw[df_raw['Level2'] == n_l2][['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']].values.ravel('K')) if pd.notna(x)]) if not df_raw.empty else []
            n_l3 = st.multiselect("L3 Focus Areas", l3_list)
            
            if st.form_submit_button("SUBMIT THE PROJECT"):
                if n_name and n_id:
                    new_row = {
                        'Level1': n_l1, 'Level2': n_l2, 
                        'Level3-1': n_l3[0] if len(n_l3)>0 else None,
                        'Level3-2': n_l3[1] if len(n_l3)>1 else None,
                        'Level3-3': n_l3[2] if len(n_l3)>2 else None,
                        'Level3-4': n_l3[3] if len(n_l3)>3 else None,
                        'Project': n_name, 'Project ID': n_id, 'Cert Year': n_year, 'Approval Pack/NOC': ''
                    }
                    save_row('review_queue.csv', new_row)
                    st.success("Saved to local review queue.")
                    st.rerun()
                else:
                    st.error("Name and ID are required.")

    with col_admin:
        st.markdown("<p class='small-header'>🕵️ Admin Review Queue</p>", unsafe_allow_html=True)
        queue_df = load_csv_safe('review_queue.csv')
        if queue_df.empty:
            st.info("Queue is empty.")
        else:
            for i, item in enumerate(queue_df.to_dict('records')):
                with st.container(border=True):
                    c_info, c_actions = st.columns([0.7, 0.3])
                    with c_info:
                        st.markdown(f"**{i+1}- {item['Project']}**")
                        st.markdown(f"<p class='mono-text'>ID: {item['Project ID']} | {item['Level1']} > {item['Level2']}</p>", unsafe_allow_html=True)
                    with c_actions:
                        if st.button("✅", key=f"app_{item['Project ID']}_{i}"):
                            save_row('projects.csv', item)
                            delete_from_review(item['Project ID'])
                            st.cache_data.clear()
                            st.rerun()
                        if st.button("🗑️", key=f"del_{item['Project ID']}_{i}"):
                            delete_from_review(item['Project ID'])
                            st.rerun()
else:
    st.stop()