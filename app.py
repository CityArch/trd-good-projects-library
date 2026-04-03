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
    .remarks-box {{ background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38BDF8; padding: 10px; margin-top: 10px; border-radius: 4px; font-size: 0.85rem; color: #CBD5E1; }}
    div[data-testid="stVerticalBlock"] > div[style*="border"] {{
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px); border: 1px solid #334155 !important; border-radius: 12px !important;
    }}
    .stButton>button {{ border-radius: 8px; text-transform: uppercase; font-weight: 600; }}
    </style>
    """, unsafe_allow_html=True)

# --- CSV FIELDNAMES ---
FIELDNAMES = ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4', 'Project', 'Project ID', 'Cert Date', 'Approval Pack/NOC', 'Remarks', 'Status']

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
        try:
            df = pd.read_csv(file_path, encoding='cp1252')
        except:
            return pd.DataFrame()
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
    st.markdown("<div class='hero-section'><h1>🔒 TRD Good Projects Library</h1></div>", unsafe_allow_html=True)
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
    if "search_reset_key" not in st.session_state: st.session_state.search_reset_key = 0
    df_raw = load_main_data()
    
    st.markdown("<div class='hero-section'><h1>🏙️ TRD GOOD PROJECTS LIBRARY</h1><p style='color:#38BDF8;'>NYC ZONING ANALYTICS TERMINAL</p></div>", unsafe_allow_html=True)

    # 1. Sidebar Search Filters
    st.sidebar.markdown("### 🛠️ SYSTEM FILTERS")
    search_mode = st.sidebar.radio("MODE", ["Single-Action Search", "Multi-Action Search"], key=f"mode_{st.session_state.search_reset_key}")
    
    final_l1, final_l2, final_l3 = [], [], []
    unique_strict = False

    if not df_raw.empty:
        if search_mode == "Single-Action Search":
            s_type = st.sidebar.segmented_control("SCOPE", ["General", "Unique"], default="General", key=f"scope_{st.session_state.search_reset_key}")
            unique_strict = (s_type == "Unique")
            
            l1_opts = ["All"] + sorted([str(x).strip() for x in df_raw['Level1'].dropna().unique() if str(x).strip()])
            c1 = st.sidebar.selectbox("L1", l1_opts, key=f"s1_{st.session_state.search_reset_key}")
            if c1 != "All":
                final_l1 = [c1]
                l2_opts = ["All"] + sorted([str(x).strip() for x in df_raw[df_raw['Level1'] == c1]['Level2'].dropna().unique() if str(x).strip()])
                c2 = st.sidebar.selectbox("L2", l2_opts, key=f"s2_{st.session_state.search_reset_key}")
                if c2 != "All":
                    final_l2 = [c2]
                    l3_cols = ['Level3-1','Level3-2','Level3-3','Level3-4']
                    raw_l3 = df_raw[df_raw['Level2'] == c2][l3_cols].values.ravel('K')
                    l3_opts = ["All"] + sorted([str(x).strip() for x in pd.unique(raw_l3) if pd.notna(x) and str(x).strip()])
                    if len(l3_opts) > 1:
                        c3 = st.sidebar.selectbox("L3", l3_opts, key=f"s3_{st.session_state.search_reset_key}")
                        if c3 != "All": final_l3 = [c3]
        else:
            final_l1 = st.sidebar.multiselect("L1", sorted([str(x).strip() for x in df_raw['Level1'].dropna().unique() if str(x).strip()]), key=f"m1_{st.session_state.search_reset_key}")
            final_l2 = st.sidebar.multiselect("L2", sorted([str(x).strip() for x in df_raw['Level2'].dropna().unique() if str(x).strip()]), key=f"m2_{st.session_state.search_reset_key}")
            l3_raw_all = df_raw[['Level3-1','Level3-2','Level3-3','Level3-4']].values.ravel('K')
            final_l3 = st.sidebar.multiselect("L3", sorted([str(x).strip() for x in pd.unique(l3_raw_all) if pd.notna(x) and str(x).strip()]), key=f"m3_{st.session_state.search_reset_key}")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 SEARCH", use_container_width=True, type="primary"):
        st.session_state.search_clicked = True
    if st.sidebar.button("🧹 CLEAR", use_container_width=True):
        st.session_state.search_reset_key += 1
        st.session_state.search_clicked = False
        st.rerun()

    # 2. Keyword Search
    q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name or ID...", key=f"q_{st.session_state.search_reset_key}")
    
    if getattr(st.session_state, 'search_clicked', False) or q_search:
        df = df_raw.copy()
        if final_l1 or final_l2 or final_l3:
            def filter_logic(group):
                assigned = set()
                for col in ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']:
                    assigned.update(group[col].dropna().astype(str).str.strip().unique())
                assigned.discard("")
                search_targets = set([str(x).strip() for x in (final_l1 + final_l2 + final_l3)])
                if unique_strict: return assigned == search_targets
                return search_targets.issubset(assigned)
            
            m_ids = df_raw.groupby('Project ID').filter(filter_logic)['Project ID'].unique()
            df = df_raw[df_raw['Project ID'].isin(m_ids)]

        if q_search:
            df = df[df['Project'].str.contains(q_search, case=False, na=False) | df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

        grouped_results = df.groupby('Project ID')
        st.subheader(f"FOUND {len(grouped_results)} PROJECTS")
        if not df.empty:
            grid = st.columns(3)
            for idx, (proj_id, group) in enumerate(grouped_results):
                first_row = group.iloc[0]
                with grid[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {first_row['Project']}")
                        item_date = first_row.get('Cert Date', first_row.get('Cert Year', 'N/A'))
                        st.markdown(f"<p class='mono-text'>ID: {proj_id} | {item_date}</p>", unsafe_allow_html=True)
                        for _, row in group.iterrows():
                            l3_v = [str(row[c]) for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if pd.notna(row[c]) and str(row[c]).strip()]
                            chain = f"{row['Level1']} > {row['Level2']}" + (f" > {', '.join(l3_v)}" if l3_v else "")
                            st.markdown(f"<p class='mono-text'>• {chain}</p>", unsafe_allow_html=True)
                        zap = str(first_row['Approval Pack/NOC'])
                        if zap.startswith("http"): st.link_button("OPEN ZAP", zap, use_container_width=True)

    # 3. Staging Area (Persistence)
    st.divider()
    col_entry, col_admin = st.columns([1, 1.2])

    queue_df = load_csv_safe('review_queue.csv')
    num_submissions = len(queue_df)
    num_approved = len(queue_df[queue_df['Status'] == 'Approved']) if not queue_df.empty else 0

    with col_entry:
        st.markdown("<p class='small-header'>📩 New Submission</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='mono-text'>Queue Load: {num_submissions}/20</p>", unsafe_allow_html=True)
        if num_submissions < 20:
            with st.form("sub_form", clear_on_submit=True):
                n_name = st.text_input("Project Name")
                n_id = st.text_input("Project ID")
                n_link = st.text_input("ZAP Link")
                n_date = st.date_input("Cert Date", value=date.today(), min_value=date(2000, 1, 1))
                
                l1_f = sorted([str(x).strip() for x in df_raw['Level1'].dropna().unique() if str(x).strip()]) if not df_raw.empty else []
                n_l1 = st.multiselect("L1 Categories", l1_f)
                l2_f = sorted([str(x).strip() for x in df_raw['Level2'].dropna().unique() if str(x).strip()]) if not df_raw.empty else []
                n_l2 = st.multiselect("L2 Sub-Categories", l2_f)
                l3_f = sorted([str(x).strip() for x in pd.unique(df_raw[['Level3-1','Level3-2','Level3-3','Level3-4']].values.ravel('K')) if pd.notna(x) and str(x).strip()]) if not df_raw.empty else []
                n_l3 = st.multiselect("L3 Focus Areas", l3_f)
                
                n_remarks = st.text_area("Remarks", placeholder="Usage notes, strengths, or weaknesses...")
                
                if st.form_submit_button("SUBMIT"):
                    if n_name and n_id and n_l1 and n_l2:
                        new_row = {
                            'Level1': n_l1[0], 'Level2': n_l2[0], 
                            'Level3-1': n_l3[0] if len(n_l3)>0 else "",
                            'Level3-2': n_l3[1] if len(n_l3)>1 else "",
                            'Level3-3': n_l3[2] if len(n_l3)>2 else "",
                            'Level3-4': n_l3[3] if len(n_l3)>3 else "",
                            'Project': n_name, 'Project ID': n_id, 'Cert Date': n_date.strftime("%m-%d-%Y"), 
                            'Approval Pack/NOC': n_link, 'Remarks': n_remarks, 'Status': 'Pending'
                        }
                        save_row('review_queue.csv', new_row)
                        st.rerun()

    with col_admin:
        st.markdown("<p class='small-header'>🕵️ Admin Review Queue</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='mono-text'>Approved Staging: {num_approved}/10</p>", unsafe_allow_html=True)
        if not queue_df.empty:
            for i, item in enumerate(queue_df.to_dict('records')):
                clean_item = {k: ("" if str(v).lower() == "nan" else str(v)).strip() for k, v in item.items()}
                is_app = (clean_item.get('Status') == 'Approved')
                display_date = item.get('Cert Date', item.get('Cert Year', "No Date"))
                
                with st.container(border=True):
                    c_txt, c_btn = st.columns([0.75, 0.25])
                    with c_txt:
                        circle = "🟢 " if is_app else ""
                        st.markdown(f"**{i+1}- {circle}{clean_item['Project']}**")
                        l3_list = [clean_item[c] for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if clean_item[c]]
                        chain = f"{clean_item['Level1']} > {clean_item['Level2']}" + (f" > {', '.join(l3_list)}" if l3_list else "")
                        st.markdown(f"<div class='mono-text'>ID: {clean_item['Project ID']} | DATE: {display_date}<br>CHAIN: {chain}</div>", unsafe_allow_html=True)
                        if clean_item.get('Remarks'):
                            st.markdown(f"<div class='remarks-box'><b>REMARKS:</b> {clean_item['Remarks']}</div>", unsafe_allow_html=True)
                        if clean_item.get('Approval Pack/NOC', '').startswith('http'):
                            st.link_button("ZAP", clean_item['Approval Pack/NOC'])
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