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
    .remarks-box {{ 
        background: rgba(56, 189, 248, 0.15); 
        border-left: 4px solid #38BDF8; 
        padding: 12px; 
        border-radius: 4px; 
        font-size: 0.9rem; 
        color: #E2E8F0; 
        margin: 10px 0 20px 10px;
        line-height: 1.4;
    }}
    .standardized-l1-image {{
        display: block; margin-left: auto; margin-right: auto;
        max-height: 300px; width: 100%; object-fit: contain;
        border-radius: 12px; margin-bottom: 25px; border: 2px solid #38BDF8;
    }}
    div[data-testid="stSidebarNav"] + div stButton button {{ height: 45px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- TREE STRUCTURE DATA ---
TREE_DATA = {
    "Use_Waivers": {"image_file": "Use_waiver.jpg", "Spatially Controlled": [], "ZL-Wide": [], "Streetscape Controls/Location Waivers": []},
    "Bulk_Waivers": {
        "image_file": "Bulk_waivers.jpg",
        "Height_Setbacks": ["Sky Exposure Plane", "Midtown Daylight Rules", "Height Limit Waivers", "Setback Waivers"],
        "Yards": [], "Lot Coverage": [], "Street Wall Location": [], "Courts": [], "Floor Area": [],
        "Tower Rules": [], "Distance Between Buildings & Distance Window - Lot Line": [], "Existing Non-Compliances": []
    },
    "Parking_Curbcuts": {"image_file": "Parking.jpg", "Manhattan Core": [], "Parking Garages": [], "Required Parking Reductions": [], "Curb-Cuts": []},
    "Open_Space": {
        "image_file": "Open Space.jpg",
        "POPs": ["New POPs", "Design change to Existing POPs", "MOD"],
        "Waterfronts": ["WPAA Certifications", "WPAA Certifications with DEC Wetlands", "No-WPAA Certifications", "Zoning Lot Subdivision Certifications"],
        "Open Space Site Plans": []
    },
    "Miscellaneous": {
        "image_file": "Miscellaneous.jpg",
        "LSGD": ["Single Zoning Lot", "Multi Zoning Lot", "Existing Buildings"],
        "FRESH": ["Fresh Certification", "Fresh with Authorization"],
        "Transit Easement Certs": [], "Houses of Worships": [], "RRROW": [], "Greater East Midtown": []
    }
}

def load_csv_safe(file_path):
    if not os.path.exists(file_path): return pd.DataFrame()
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', dtype=str)
    except:
        try: df = pd.read_csv(file_path, encoding='cp1252', dtype=str)
        except: return pd.DataFrame()
    df.columns = [str(c).strip() for c in df.columns]
    return df.fillna("").map(lambda x: str(x).strip())

def save_row(file_path, data_dict):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4', 'Project', 'Project ID', 'Cert Date', 'Approval Pack/NOC', 'Remarks', 'Status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists: writer.writeheader()
        writer.writerow({k: str(data_dict.get(k, "")).strip() for k in fieldnames})

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
if "multi_iterations" not in st.session_state: st.session_state.multi_iterations = [{"l1": "--", "l2": "--", "l3": "--"}]
if "search_clicked" not in st.session_state: st.session_state.search_clicked = False

df_raw = load_csv_safe('projects.csv')

st.markdown("<div class='hero-section'><h1>🏙️ TRD GOOD PROJECTS LIBRARY</h1><p style='color:#38BDF8;'>NYC ZONING ANALYTICS TERMINAL</p></div>", unsafe_allow_html=True)

# 1. SIDEBAR
st.sidebar.markdown("### 🛠️ CONFIGURATION")
search_mode = st.sidebar.radio("MODE", ["Single-Action Search", "Multi-Action Search"], key=f"mode_{st.session_state.search_reset_key}")

if search_mode == "Single-Action Search":
    s_type = st.sidebar.segmented_control("SCOPE", ["General", "Unique"], default="General", key=f"scope_{st.session_state.search_reset_key}")
    unique_strict = (s_type == "Unique")
else:
    unique_strict = True 

st.sidebar.markdown("---")
side_col1, side_col2 = st.sidebar.columns(2)
with side_col1:
    if st.button("🚀 SEARCH", type="primary", use_container_width=True):
        st.session_state.search_clicked = True
with side_col2:
    if st.button("🧹 CLEAR", use_container_width=True):
        st.session_state.search_reset_key += 1
        st.session_state.multi_iterations = [{"l1": "--", "l2": "--", "l3": "--"}]
        st.session_state.search_clicked = False
        st.rerun()

# 2. WORKSPACE
st.subheader("🌳 Project Search Filter")
workspace_cols = st.columns(len(st.session_state.multi_iterations))

for i, iteration in enumerate(st.session_state.multi_iterations):
    with workspace_cols[i]:
        sel_l1 = st.session_state.multi_iterations[i]["l1"]
        if sel_l1 != "--":
            img_b64 = get_base64_image(TREE_DATA[sel_l1]["image_file"])
            if img_b64: st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="standardized-l1-image">', unsafe_allow_html=True)
        else: st.markdown("<div style='height:300px;'></div>", unsafe_allow_html=True)
        
        st.session_state.multi_iterations[i]["l1"] = st.selectbox(f"L1 Selection", ["--"] + list(TREE_DATA.keys()), key=f"l1_{i}_{st.session_state.search_reset_key}")
        
        cur_l1 = st.session_state.multi_iterations[i]["l1"]
        if cur_l1 != "--":
            daddy_list = [k for k in TREE_DATA[cur_l1].keys() if k != "image_file"]
            st.session_state.multi_iterations[i]["l2"] = st.radio(f"L2 - {cur_l1}", ["--"] + daddy_list, key=f"l2_{i}_{st.session_state.search_reset_key}")
            
            cur_l2 = st.session_state.multi_iterations[i]["l2"]
            if cur_l2 != "--":
                son_list = TREE_DATA[cur_l1][cur_l2]
                if son_list:
                    st.session_state.multi_iterations[i]["l3"] = st.radio(f"L3 - {cur_l2}", ["--"] + son_list, key=f"l3_{i}_{st.session_state.search_reset_key}")
                else: st.session_state.multi_iterations[i]["l3"] = "--"

# --- REINSTATED NAVIGATION BUTTONS ---
st.markdown("<br>", unsafe_allow_html=True)
nav1, nav2, _ = st.columns([0.15, 0.15, 0.7])
if search_mode == "Multi-Action Search" and len(st.session_state.multi_iterations) < 5:
    if nav1.button("➕ CONTINUE", use_container_width=True):
        st.session_state.multi_iterations.append({"l1": "--", "l2": "--", "l3": "--"})
        st.rerun()

if search_mode == "Multi-Action Search" and len(st.session_state.multi_iterations) > 1:
    if nav2.button("🏁 FINISH", use_container_width=True):
        st.success("Search Filter locked.")

# 3. RESULTS ENGINE
st.divider()
q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name or ID...", key=f"q_{st.session_state.search_reset_key}")

if st.session_state.search_clicked or q_search:
    df = df_raw.copy()
    valid_filters = [s for s in st.session_state.multi_iterations if s['l1'] != "--"]

    if valid_filters:
        def filter_engine(group):
            project_values = set()
            cols_to_check = ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']
            for col in cols_to_check:
                for val in group[col].unique():
                    v = str(val).strip().lower()
                    if v and v not in ["", "nan", "--"]: project_values.add(v)
            
            search_values = set()
            for f in valid_filters:
                search_values.add(f['l1'].lower())
                if f['l2'] != "--": search_values.add(f['l2'].lower())
                if f['l3'] != "--": search_values.add(f['l3'].lower())
            
            is_match = search_values.issubset(project_values)
            if not is_match: return False
            if unique_strict: return len(project_values) == len(search_values)
            return True

        m_ids = df_raw.groupby('Project ID').filter(filter_engine)['Project ID'].unique()
        df = df_raw[df_raw['Project ID'].isin(m_ids)]

    if q_search:
        df = df[df['Project'].str.contains(q_search, case=False, na=False) | df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

    st.subheader(f"FOUND {len(df.groupby('Project ID'))} PROJECTS")
    res_grid = st.columns(3)
    for idx, (p_id, gp) in enumerate(df.groupby('Project ID')):
        with res_grid[idx % 3]:
            with st.container(border=True):
                r1 = gp.iloc[0]
                st.markdown(f"### {r1['Project']}")
                st.markdown(f"<p class='mono-text'><b>ID:</b> {p_id} | <b>Date:</b> {r1.get('Cert Date', '')}</p>", unsafe_allow_html=True)
                for _, r in gp.iterrows():
                    l3s = [str(r[c]) for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if str(r[c]).strip() and str(r[c]).lower() not in ["", "nan"]]
                    chain = f"• {r['Level1']} > {r['Level2']}" + (f" > {', '.join(l3s)}" if l3s else "")
                    st.markdown(f"<p class='mono-text'>{chain}</p>", unsafe_allow_html=True)
                    rem_val = str(r.get('Remarks', '')).strip()
                    if rem_val and rem_val.lower() not in ["", "nan", "none"]:
                        st.markdown(f"<div class='remarks-box'><b>Remarks:</b><br>{rem_val}</div>", unsafe_allow_html=True)
                if str(r1.get('Approval Pack/NOC', '')).strip():
                    st.link_button("ZAP", r1['Approval Pack/NOC'], use_container_width=True)

# 4. ADMIN QUEUE
st.divider()
c1, c2 = st.columns([1, 1.2])
with c1:
    st.markdown("<p class='small-header'>📩 New Submission</p>", unsafe_allow_html=True)
    with st.form("sub", clear_on_submit=True):
        n_name, n_id = st.text_input("Name"), st.text_input("ID")
        n_l1 = st.selectbox("L1 Selection", list(TREE_DATA.keys()))
        if st.form_submit_button("SUBMIT") and n_name:
            save_row('review_queue.csv', {'Level1': n_l1, 'Project': n_name, 'Project ID': n_id, 'Status': 'Pending'})
            st.rerun()
with c2:
    st.markdown("<p class='small-header'>🕵️ Admin Queue</p>", unsafe_allow_html=True)
    q_df = load_csv_safe('review_queue.csv')
    if not q_df.empty:
        for i, row in q_df.iterrows():
            with st.container(border=True):
                st.write(f"**{row['Project']}** (ID: {row['Project ID']})")
                if st.button("🗑️", key=f"del_{i}"):
                    df_q = q_df.drop(i); df_q.to_csv('review_queue.csv', index=False); st.rerun()