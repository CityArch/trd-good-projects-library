import streamlit as st
import pandas as pd
import os
import csv
import base64
from datetime import date

# 1. Page Configuration
st.set_page_config(page_title="TRD Good Projects Library", page_icon="🏙️", layout="wide")

# --- HELPER: IMAGE TO BASE64 ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return ""
    return ""

img_base64 = get_base64_image("image.jpg")

# --- CSS STYLING ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; color: #F8FAFC; }}
    .hero-section {{
        background-image: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url("data:image/jpg;base64,{img_base64}");
        background-size: cover; background-position: center;
        padding: 60px 20px; border-radius: 15px; border: 1px solid #334155;
        text-align: center; margin-bottom: 30px;
    }}
    .mono-text {{ font-family: 'Roboto Mono', monospace; font-size: 0.85rem; color: #94A3B8; margin-bottom: 5px; }}
    .remarks-box {{ background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38BDF8; padding: 10px; border-radius: 4px; font-size: 0.85rem; color: #CBD5E1; margin-bottom: 5px; }}
    
    /* Tree Styling */
    .tree-branch {{ padding-left: 20px; border-left: 1px solid #334155; margin-bottom: 10px; }}
    .disabled-label {{ color: #475569 !important; font-style: italic; }}
    
    div[data-testid="stSidebarNav"] + div stButton button {{ height: 45px !important; padding: 0px !important; }}
    div[data-testid="stVerticalBlock"] > div[style*="border"] {{
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px); border: 1px solid #334155 !important; border-radius: 12px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- DATA HELPERS ---
FIELDNAMES = ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4', 'Project', 'Project ID', 'Cert Date', 'Approval Pack/NOC', 'Remarks', 'Status']

def load_csv_safe(file_path):
    if not os.path.exists(file_path): return pd.DataFrame()
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except:
        try: df = pd.read_csv(file_path, encoding='cp1252')
        except: return pd.DataFrame()
    df.columns = [str(c).strip().replace('ï»¿', '') for c in df.columns]
    return df.fillna("")

def save_row(file_path, data_dict):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists: writer.writeheader()
        clean_dict = {k: str(data_dict.get(k, "")).replace("nan", "").strip() for k in FIELDNAMES}
        writer.writerow(clean_dict)

# --- AUTHENTICATION ---
if "password_correct" not in st.session_state: st.session_state.password_correct = False
if not st.session_state.password_correct:
    st.markdown("<div class='hero-section'><h1>🔒 TRD Good Projects Library</h1></div>", unsafe_allow_html=True)
    with st.form("login"):
        pw = st.text_input("Passcode", type="password")
        if st.form_submit_button("UNLOCK"):
            if pw == "1234567890":
                st.session_state.password_correct = True
                st.rerun()
            else: st.error("Invalid passcode.")
    st.stop()

# --- INITIALIZE STATE ---
if "search_reset_key" not in st.session_state: st.session_state.search_reset_key = 0
if "multi_selections" not in st.session_state: st.session_state.multi_selections = []
df_raw = load_csv_safe('projects.csv')

# Pre-calculate existing action chains for gray-out logic
existing_chains = set()
if not df_raw.empty:
    for _, row in df_raw.iterrows():
        l1, l2 = str(row['Level1']).strip(), str(row['Level2']).strip()
        l3_cols = [str(row[f'Level3-{i}']).strip() for i in range(1, 5) if str(row[f'Level3-{i}']).strip()]
        existing_chains.add((l1, None, None))
        existing_chains.add((l1, l2, None))
        for l3 in l3_cols:
            existing_chains.add((l1, l2, l3))

st.markdown("<div class='hero-section'><h1>🏙️ TRD GOOD PROJECTS LIBRARY</h1><p style='color:#38BDF8;'>NYC ZONING ANALYTICS TERMINAL</p></div>", unsafe_allow_html=True)

# 1. Sidebar Search
st.sidebar.markdown("### 🛠️ SYSTEM FILTERS")
search_mode = st.sidebar.radio("MODE", ["Single-Action Search", "Multi-Action Search"], key=f"mode_{st.session_state.search_reset_key}")

unique_strict = False
if search_mode == "Single-Action Search":
    s_type = st.sidebar.segmented_control("SCOPE", ["General", "Unique"], default="General", key=f"scope_{st.session_state.search_reset_key}")
    unique_strict = (s_type == "Unique")

def render_tree_selector(key_prefix):
    """Renders the vertical tree selection logic."""
    sel_l1, sel_l2, sel_l3 = None, None, None
    
    # L1 Selection
    l1_list = ["Use_Waivers", "Bulk_Waivers", "Parking_Curbcuts", "Open_Space", "Miscellaneous"]
    sel_l1 = st.sidebar.selectbox("Select L1 Category", ["--"] + l1_list, key=f"{key_prefix}_l1")
    
    if sel_l1 != "--":
        # Extract L2s from database related to L1
        l2_options = sorted(df_raw[df_raw['Level1'] == sel_l1]['Level2'].unique())
        st.sidebar.markdown(f"**Branches for {sel_l1}:**")
        sel_l2 = st.sidebar.radio("Select L2 Branch", ["--"] + list(l2_options), key=f"{key_prefix}_l2")
        
        if sel_l2 != "--":
            # Extract L3s from database related to L2
            l3_cols = ['Level3-1','Level3-2','Level3-3','Level3-4']
            l3_vals = pd.unique(df_raw[df_raw['Level2'] == sel_l2][l3_cols].values.ravel('K'))
            l3_options = sorted([str(x).strip() for x in l3_vals if str(x).strip() and str(x).lower() != 'nan'])
            
            st.sidebar.markdown(f"**Sub-categories for {sel_l2}:**")
            # Logic: If chain (L1, L2, L3) exists in set, it's clickable.
            for opt in l3_options:
                is_available = (sel_l1, sel_l2, opt) in existing_chains
                if is_available:
                    if st.sidebar.checkbox(opt, key=f"{key_prefix}_l3_{opt}"):
                        sel_l3 = opt
                else:
                    st.sidebar.markdown(f"<span class='disabled-label'>- {opt} (No Projects)</span>", unsafe_allow_html=True)
    
    return sel_l1, sel_l2, sel_l3

# --- Search Execution Logic ---
current_selections = []

if search_mode == "Single-Action Search":
    l1, l2, l3 = render_tree_selector("single")
    if l1 != "--" and l2 != "--":
        current_selections = [{"l1": l1, "l2": l2, "l3": l3}]
else:
    # Multi-Action Search Logic
    st.sidebar.markdown(f"**Selections Made: {len(st.session_state.multi_selections)}/5**")
    for i, prev in enumerate(st.session_state.multi_selections):
        st.sidebar.info(f"{i+1}: {prev['l1']} > {prev['l2']} > {prev['l3'] if prev['l3'] else 'All'}")
    
    if len(st.session_state.multi_selections) < 5:
        l1, l2, l3 = render_tree_selector(f"multi_{len(st.session_state.multi_selections)}")
        if st.sidebar.button("➕ CONTINUE") and l1 != "--" and l2 != "--":
            st.session_state.multi_selections.append({"l1": l1, "l2": l2, "l3": l3})
            st.rerun()
    current_selections = st.session_state.multi_selections

st.sidebar.markdown("---")
side_col1, side_col2 = st.sidebar.columns(2)
with side_col1:
    if st.button("🚀 SEARCH", type="primary", use_container_width=True):
        st.session_state.search_clicked = True
with side_col2:
    if st.button("🧹 CLEAR", use_container_width=True):
        st.session_state.search_reset_key += 1
        st.session_state.multi_selections = []
        st.session_state.search_clicked = False
        st.rerun()

# 2. Results Area
q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name or ID...", key=f"q_{st.session_state.search_reset_key}")
if getattr(st.session_state, 'search_clicked', False) or q_search:
    df = df_raw.copy()
    if current_selections:
        def filter_logic(group):
            assigned = set()
            for col in ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']:
                assigned.update(group[col].dropna().astype(str).str.strip().unique())
            assigned.discard("")
            
            # Check all selections
            match_count = 0
            for sel in current_selections:
                targets = {sel['l1'], sel['l2']}
                if sel['l3']: targets.add(sel['l3'])
                
                if unique_strict and search_mode == "Single-Action Search":
                    if assigned == targets: match_count += 1
                elif targets.issubset(assigned):
                    match_count += 1
            
            return match_count > 0

        m_ids = df_raw.groupby('Project ID').filter(filter_logic)['Project ID'].unique()
        df = df_raw[df_raw['Project ID'].isin(m_ids)]

    if q_search:
        df = df[df['Project'].str.contains(q_search, case=False, na=False) | df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]
    
    grouped = df.groupby('Project ID')
    st.subheader(f"FOUND {len(grouped)} PROJECTS")
    grid = st.columns(3)
    for idx, (p_id, gp) in enumerate(grouped):
        with grid[idx % 3]:
            with st.container(border=True):
                row1 = gp.iloc[0]
                st.markdown(f"### {row1['Project']}")
                st.markdown(f"<p class='mono-text'><b>Project ID:</b> {p_id} | <b>Cert Date:</b> {row1.get('Cert Date', row1.get('Cert Year', ''))}</p>", unsafe_allow_html=True)
                st.markdown("<p class='mono-text'><b>Categorized Actions & Remarks:</b></p>", unsafe_allow_html=True)
                for _, r in gp.iterrows():
                    l3_list = [str(r[c]) for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if str(r[c]).strip() and str(r[c]).lower() != 'nan']
                    chain = f"• {r['Level1']} > {r['Level2']}" + (f" > {', '.join(l3_list)}" if l3_list else "")
                    st.markdown(f"<p class='mono-text'>{chain}</p>", unsafe_allow_html=True)
                    rem_val = str(r.get('Remarks', '')).strip()
                    if rem_val and rem_val.lower() != 'nan':
                        st.markdown(f"<div class='remarks-box'><b>Remark:</b> {rem_val}</div>", unsafe_allow_html=True)
                zap_url = str(row1.get('Approval Pack/NOC', '')).strip()
                if zap_url and zap_url.lower() != 'nan':
                    st.link_button("ZAP", zap_url, use_container_width=True)

# 3. Submission & Admin (Restored and Kept Intact)
st.divider()
c_entry, c_admin = st.columns([1, 1.2])
queue_df = load_csv_safe('review_queue.csv')
num_app = len(queue_df[queue_df['Status'] == 'Approved']) if not queue_df.empty else 0

with c_entry:
    st.markdown("<p class='small-header'>📩 New Submission</p>", unsafe_allow_html=True)
    if len(queue_df) < 20:
        with st.form("sub_form", clear_on_submit=True):
            n_name, n_id, n_link = st.text_input("Project Name"), st.text_input("Project ID"), st.text_input("ZAP Link")
            n_date = st.date_input("Cert Date", min_value=date(2000, 1, 1))
            l1_list = ["Use_Waivers", "Bulk_Waivers", "Parking_Curbcuts", "Open_Space", "Miscellaneous"]
            n_l1 = st.multiselect("L1", l1_list)
            n_l2 = st.text_input("L2 Sub-Category")
            n_l3 = st.text_input("L3 Action (Optional)")
            n_rem = st.text_area("Remarks")
            if st.form_submit_button("SUBMIT") and n_name and n_id and n_l1:
                clean_link = n_link.strip()
                if clean_link and not clean_link.startswith("http"): clean_link = "https://" + clean_link
                new_row = {'Level1': n_l1[0], 'Level2': n_l2, 'Level3-1': n_l3, 'Project': n_name, 'Project ID': n_id, 'Cert Date': n_date.strftime("%m-%d-%Y"), 'Approval Pack/NOC': clean_link, 'Remarks': n_rem, 'Status': 'Pending'}
                save_row('review_queue.csv', new_row); st.rerun()
    else: st.warning("Queue Full.")

with c_admin:
    st.markdown("<p class='small-header'>🕵️ Admin Review Queue</p>", unsafe_allow_html=True)
    for i, item in enumerate(queue_df.to_dict('records')):
        clean = {k: ("" if str(v).lower() == "nan" else str(v)).strip() for k, v in item.items()}
        is_app = (clean['Status'] == 'Approved')
        with st.container(border=True):
            h_col, a_col = st.columns([0.8, 0.2])
            with h_col:
                st.markdown(f"**{i+1}- {'🟢 ' if is_app else ''}{clean['Project']}**")
                st.markdown(f"<div class='mono-text'>ID: {clean['Project ID']} | {clean['Level1']} > {clean['Level2']}</div>", unsafe_allow_html=True)
                if clean['Approval Pack/NOC']: st.link_button("ZAP", clean['Approval Pack/NOC'])
            with a_col:
                if st.button("🗑️", key=f"tr{i}"):
                    df_q = load_csv_safe('review_queue.csv')
                    df_q = df_q[df_q['Project ID'].astype(str) != str(clean['Project ID'])]
                    df_q.to_csv('review_queue.csv', index=False); st.rerun()