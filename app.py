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
    .remarks-box {{ background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38BDF8; padding: 10px; border-radius: 4px; font-size: 0.85rem; color: #CBD5E1; margin-top: 5px; }}
    
    /* Family Tree Selection Container */
    .tree-family-container {{
        background: rgba(30, 41, 59, 0.7);
        border: 2px solid #38BDF8;
        border-radius: 12px;
        padding: 20px;
        min-height: 600px;
        display: flex;
        flex-direction: column;
    }}
    .family-header {{ 
        color: #38BDF8; 
        font-weight: bold; 
        text-transform: uppercase; 
        border-bottom: 1px solid #334155; 
        padding-bottom: 8px; 
        margin-bottom: 15px; 
        text-align: center;
    }}
    
    /* Standardized L1 Image Styling - Positioned at top */
    .standardized-l1-image {{
        display: block;
        margin-left: auto;
        margin-right: auto;
        max-height: 150px;
        width: 100%;
        object-fit: cover;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid #334155;
    }}
    
    div[data-testid="stSidebarNav"] + div stButton button {{ height: 45px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- TREE STRUCTURE DATA ---
TREE_DATA = {
    "Use_Waivers": {
        "image_file": "Use_waiver.jpg",
        "Spatially Controlled": [], "ZL-Wide": [], "Streetscape Controls/Location Waivers": []
    },
    "Bulk_Waivers": {
        "image_file": "Bulk_waivers.jpg",
        "Height_Setbacks": ["Sky Exposure Plane", "Midtown Daylight Rules", "Height Limit Waivers", "Setback Waivers"],
        "Yards": [], "Lot Coverage": [], "Street Wall Location": [], "Courts": [], "Floor Area": [],
        "Tower Rules": [], "Distance Between Buildings & Distance Window - Lot Line": [], "Existing Non-Compliances": []
    },
    "Parking_Curbcuts": {
        "image_file": "Parking.jpg",
        "Manhattan Core": [], "Parking Garages": [], "Required Parking Reductions": [], "Curb-Cuts": []
    },
    "Open_Space": {
        "image_file": "Open Space.jpg",
        "POPs": ["New POPs", "Design change to Existing POPs", "MOD"],
        "Waterfronts": ["WPAA Certifications", "WPAA Certifications with DEC Wetlands", "No-WPAA Certifications", "Zoning Lot Subdivision Certifications"],
        "Open Space Site Plans": []
    },
    "Miscellaneous": {
        "image_file": "Miscellaneous.jpg",
        "LSGD": ["Single Zoning Lot", "Multi Zoning Lot", "Existing Buildings"],
        "FRESH": ["Fresh Certifications", "Fresh with Authorizations"],
        "Transit Easement Certs": [], "Houses of Worships": [], "RRROW": [], "Greater East Midtown": []
    }
}

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

def delete_from_review(proj_id):
    df = load_csv_safe('review_queue.csv')
    if df.empty: return
    df = df[df['Project ID'].astype(str).str.strip() != str(proj_id).strip()]
    df.to_csv('review_queue.csv', index=False, encoding='utf-8-sig')

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

# 1. SIDEBAR CONFIG
st.sidebar.markdown("### 🛠️ CONFIGURATION")
search_mode = st.sidebar.radio("MODE", ["Single-Action Search", "Multi-Action Search"], key=f"mode_{st.session_state.search_reset_key}")

unique_strict = True 
if search_mode == "Single-Action Search":
    s_type = st.sidebar.segmented_control("SCOPE", ["General", "Unique"], default="General", key=f"scope_{st.session_state.search_reset_key}")
    unique_strict = (s_type == "Unique")

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

# 2. HIERARCHY WORKSPACE
st.subheader("🌳 Grandpa-Daddy-Son Workspace")

workspace_cols = st.columns(len(st.session_state.multi_iterations))

for i, iteration in enumerate(st.session_state.multi_iterations):
    with workspace_cols[i]:
        st.markdown(f"<div class='tree-family-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='family-header'>FAMILY #{i+1}</div>", unsafe_allow_html=True)
        
        # CATEGORY IMAGE (Placed at the very top of the container)
        sel_l1_temp = st.session_state.multi_iterations[i]["l1"]
        if sel_l1_temp != "--":
            img_path = TREE_DATA[sel_l1_temp]["image_file"]
            img_b64 = get_base64_image(img_path)
            if img_b64:
                st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="standardized-l1-image">', unsafe_allow_html=True)
        
        # Grandpa (L1) Dropdown
        l1_opts = ["--"] + list(TREE_DATA.keys())
        st.session_state.multi_iterations[i]["l1"] = st.selectbox(f"Grandpa (L1)", l1_opts, key=f"l1_{i}_{st.session_state.search_reset_key}")
        
        sel_l1 = st.session_state.multi_iterations[i]["l1"]
        if sel_l1 != "--":
            # Daddy (L2) Radio
            daddy_list = [k for k in TREE_DATA[sel_l1].keys() if k != "image_file"]
            l2_opts = ["--"] + list(daddy_list)
            st.session_state.multi_iterations[i]["l2"] = st.radio(f"Daddy (L2) - {sel_l1}", l2_opts, key=f"l2_{i}_{st.session_state.search_reset_key}")
            
            sel_l2 = st.session_state.multi_iterations[i]["l2"]
            if sel_l2 != "--":
                # Son (L3) Radio
                son_list = TREE_DATA[sel_l1][sel_l2]
                if son_list:
                    st.session_state.multi_iterations[i]["l3"] = st.radio(f"Son (L3) - {sel_l2}", ["--"] + son_list, key=f"l3_{i}_{st.session_state.search_reset_key}")
                else:
                    st.session_state.multi_iterations[i]["l3"] = "--"
        st.markdown("</div>", unsafe_allow_html=True)

# Navigation Buttons
st.markdown("<br>", unsafe_allow_html=True)
nav1, nav2, _ = st.columns([0.15, 0.15, 0.7])
if search_mode == "Multi-Action Search" and len(st.session_state.multi_iterations) < 5:
    if nav1.button("➕ CONTINUE", use_container_width=True):
        st.session_state.multi_iterations.append({"l1": "--", "l2": "--", "l3": "--"})
        st.rerun()

if len(st.session_state.multi_iterations) > 1:
    if nav2.button("🏁 FINISH", use_container_width=True):
        st.success("Hierarchy locked.")

# 3. RESULTS ENGINE
st.divider()
q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name or ID...", key=f"q_{st.session_state.search_reset_key}")

if st.session_state.search_clicked or q_search:
    df = df_raw.copy()
    valid_filters = [s for s in st.session_state.multi_iterations if s['l1'] != "--"]

    if valid_filters:
        def filter_engine(group):
            project_actions = set()
            for col in ['Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4']:
                vals = group[col].dropna().astype(str).str.strip().unique()
                project_actions.update([v for v in vals if v and v.lower() != 'nan' and v != "--"])
            
            search_actions = set()
            for f in valid_filters:
                search_actions.add(f['l1'])
                if f['l2'] != "--": search_actions.add(f['l2'])
                if f['l3'] != "--": search_actions.add(f['l3'])
            
            return project_actions == search_actions if unique_strict else search_actions.issubset(project_actions)

        m_ids = df_raw.groupby('Project ID').filter(filter_engine)['Project ID'].unique()
        df = df_raw[df_raw['Project ID'].isin(m_ids)]

    if q_search:
        df = df[df['Project'].str.contains(q_search, case=False, na=False) | df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]

    grouped = df.groupby('Project ID')
    st.subheader(f"FOUND {len(grouped)} PROJECTS")
    res_grid = st.columns(3)
    for idx, (p_id, gp) in enumerate(grouped):
        with res_grid[idx % 3]:
            with st.container(border=True):
                r1 = gp.iloc[0]
                st.markdown(f"### {r1['Project']}")
                st.markdown(f"<p class='mono-text'><b>Project ID:</b> {p_id} | <b>Cert Date:</b> {r1.get('Cert Date', r1.get('Cert Year', ''))}</p>", unsafe_allow_html=True)
                for _, r in gp.iterrows():
                    l3s = [str(r[c]) for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if str(r[c]).strip() and str(r[c]).lower() != 'nan']
                    chain = f"• {r['Level1']} > {r['Level2']}" + (f" > {', '.join(l3s)}" if l3s else "")
                    st.markdown(f"<p class='mono-text'>{chain}</p>", unsafe_allow_html=True)
                    if str(r.get('Remarks','')).strip() not in ["","nan"]:
                        st.markdown(f"<div class='remarks-box'><b>Remarks:</b> {r['Remarks']}</div>", unsafe_allow_html=True)
                z_url = str(r1.get('Approval Pack/NOC', '')).strip()
                if z_url and z_url.lower() != 'nan':
                    st.link_button("ZAP", z_url, use_container_width=True)

# 4. ADMIN QUEUE (Restored)
st.divider()
c1, c2 = st.columns([1, 1.2])
with c1:
    st.markdown("<p class='small-header'>📩 New Submission</p>", unsafe_allow_html=True)
    with st.form("sub", clear_on_submit=True):
        n_name, n_id = st.text_input("Name"), st.text_input("ID")
        n_l1 = st.selectbox("L1", list(TREE_DATA.keys()))
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
                    delete_from_review(row['Project ID']); st.rerun()