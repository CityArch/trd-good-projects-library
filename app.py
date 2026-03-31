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
FIELDNAMES = ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4', 'Project', 'Project ID', 'Cert Year', 'Approval Pack/NOC', 'Status']

# --- FILE OPERATIONS ---
def save_row(file_path, data_dict):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists: writer.writeheader()
        clean_dict = {k: str(data_dict.get(k, "")).strip() for k in FIELDNAMES}
        writer.writerow(clean_dict)

def load_csv_safe(file_path):
    if not os.path.exists(file_path): return pd.DataFrame()
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except:
        try: df = pd.read_csv(file_path, encoding='cp1252')
        except: return pd.DataFrame()
    df.columns = [str(c).strip().replace('ï»¿', '') for c in df.columns]
    return df

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
    if not df_raw.empty:
        if search_mode == "Single-Action Search":
            l1_opts = ["All"] + sorted([str(x).strip() for x in df_raw['Level1'].dropna().unique()])
            c1 = st.sidebar.selectbox("L1", l1_opts, key=f"s1_{st.session_state.reset_key}")
            if c1 != "All":
                final_l1 = [c1]
                l2_opts = ["All"] + sorted([str(x).strip() for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique()])
                c2 = st.sidebar.selectbox("L2", l2_opts, key=f"s2_{st.session_state.reset_key}")
                if c2 != "All":
                    final_l2 = [c2]
                    raw_l3 = df_raw[df_raw['Level2'] == c2][['Level3-1','Level3-2','Level3-3','Level3-4']].values.ravel('K')
                    l3_opts = ["All"] + sorted([str(x).strip() for x in pd.unique(raw_l3) if pd.notna(x)])
                    if len(l3_opts) > 1:
                        c3 = st.sidebar.selectbox("L3", l3_opts, key=f"s3_{st.session_state.reset_key}")
                        if c3 != "All": final_l3 = [c3]
        else:
            final_l1 = st.sidebar.multiselect("L1", sorted(df_raw['Level1'].dropna().unique()), key=f"m1_{st.session_state.reset_key}")
            final_l2 = st.sidebar.multiselect("L2", sorted(df_raw['Level2'].dropna().unique()), key=f"m2_{st.session_state.reset_key}")
            raw_l3_all = df_raw[['Level3-1','Level3-2','Level3-3','Level3-4']].values.ravel('K')
            final_l3 = st.sidebar.multiselect("L3", sorted([str(x).strip() for x in pd.unique(raw_l3_all) if pd.notna(x)]), key=f"m3_{st.session_state.reset_key}")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 EXECUTE SEARCH", use_container_width=True, type="primary"):
        st.session_state.search_clicked = True
    if st.sidebar.button("🧹 RESET SYSTEM", use_container_width=True):
        st.session_state.reset_key += 1
        st.session_state.search_clicked = False
        st.rerun()

    # Keyword search bar
    q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name or ID...", key=f"q_{st.session_state.reset_key}")

    # 5. DATA CONTRIBUTION & ADMIN REVIEW (STAGING WORKFLOW)
    st.divider()
    col_entry, col_admin = st.columns([1, 1.2])

    queue_df = load_csv_safe('review_queue.csv')
    num_submissions = len(queue_df)
    num_approved = len(queue_df[queue_df['Status'] == 'Approved']) if not queue_df.empty else 0

    with col_entry:
        st.markdown("<p class='small-header'>📩 New Submission</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='mono-text'>Queue: {num_submissions}/20</p>", unsafe_allow_html=True)
        
        if num_submissions >= 20:
            st.warning("Queue Full (20). Delete entries to submit more.")
        else:
            with st.form("sub_form", clear_on_submit=True):
                n_name = st.text_input("Project Name")
                n_id = st.text_input("Project ID")
                n_link = st.text_input("ZAP Link")
                n_year = st.selectbox("Cert Year", range(2000, 2028), index=26)
                
                l1_f = sorted([str(x).strip() for x in df_raw['Level1'].dropna().unique()]) if not df_raw.empty else []
                n_l1 = st.multiselect("L1 Categories", l1_f)
                
                l2_f = sorted([str(x).strip() for x in df_raw['Level2'].dropna().unique()]) if not df_raw.empty else []
                n_l2 = st.multiselect("L2 Sub-Categories", l2_f)
                
                l3_raw_pool = df_raw[['Level3-1','Level3-2','Level3-3','Level3-4']].values.ravel('K') if not df_raw.empty else []
                l3_f = sorted([str(x).strip() for x in pd.unique(l3_raw_pool) if pd.notna(x)])
                n_l3 = st.multiselect("L3 Focus Areas", l3_f)
                
                if st.form_submit_button("SUBMIT THE PROJECT"):
                    if n_name and n_id and n_l1 and n_l2:
                        new_row = {
                            'Level1': n_l1[0], 'Level2': n_l2[0], 
                            'Level3-1': n_l3[0] if len(n_l3)>0 else None,
                            'Level3-2': n_l3[1] if len(n_l3)>1 else None,
                            'Level3-3': n_l3[2] if len(n_l3)>2 else None,
                            'Level3-4': n_l3[3] if len(n_l3)>3 else None,
                            'Project': n_name, 'Project ID': n_id, 'Cert Year': n_year, 
                            'Approval Pack/NOC': n_link, 'Status': 'Pending'
                        }
                        save_row('review_queue.csv', new_row)
                        st.rerun()
                    else:
                        st.error("Missing mandatory fields.")

    with col_admin:
        st.markdown("<p class='small-header'>🕵️ Admin Review Queue</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='mono-text'>Approved Staging: {num_approved}/10</p>", unsafe_allow_html=True)
        
        if queue_df.empty:
            st.info("Queue is empty.")
        else:
            for i, item in enumerate(queue_df.to_dict('records')):
                is_app = (str(item.get('Status')).strip() == 'Approved')
                with st.container(border=True):
                    c_txt, c_btn = st.columns([0.7, 0.3])
                    with c_txt:
                        circle = "🟢 " if is_app else ""
                        st.markdown(f"**{i+1}- {circle}{item['Project']}**")
                        st.markdown(f"<p class='mono-text'>ID: {item['Project ID']} | {item['Level1']} > {item['Level2']}</p>", unsafe_allow_html=True)
                    with c_btn:
                        if not is_app and num_approved < 10:
                            if st.button("✅", key=f"ok_{i}"):
                                update_queue_status(item['Project ID'], "Approved")
                                st.rerun()
                        if st.button("🗑️", key=f"tr_{i}"):
                            delete_from_review(item['Project ID'])
                            st.rerun()
else:
    st.stop()