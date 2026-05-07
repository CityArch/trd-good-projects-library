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
    .standardized-l1-image {{
        display: block; margin-left: auto; margin-right: auto;
        max-height: 300px; width: 100%; object-fit: contain;
        border-radius: 12px; margin-bottom: 25px; border: 2px solid #38BDF8;
    }}
    .stSelectbox label {{ text-align: center; display: block; }}
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
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except:
        try: df = pd.read_csv(file_path, encoding='cp1252')
        except: return pd.DataFrame()
    df.columns = [str(c).strip().replace('ï»¿', '') for c in df.columns]
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df.replace("nan", "")

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
        sel_l1_temp = st.session_state.multi_iterations[i]["l1"]
        if sel_l1_temp != "--":
            img_b64 = get_base64_image(TREE_DATA[sel_l1_temp]["image_file"])
            if img_b64: st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="standardized-l1-image">', unsafe_allow_html=True)
        else: st.markdown("<div style='height:300px;'></div>", unsafe_allow_html=True)
        
        st.session_state.multi_iterations[i]["l1"] = st.selectbox(f"L1 Selection", ["--"] + list(TREE_DATA.keys()), key=f"l1_{i}_{st.session_state.search_reset_key}")
        
        sel_l1 = st.session_state.multi_iterations[i]["l1"]
        if sel_l1 != "--":
            daddy_list = [k for k in TREE_DATA[sel_l1].keys() if k != "image_file"]
            st.session_state.multi_iterations[i]["l2"] = st.radio(f"L2 - {sel_l1}", ["--"] + daddy_list, key=f"l2_{i}_{st.session_state.search_reset_key}")
            
            sel_l2 = st.session_state.multi_iterations[i]["l2"]
            if sel_l2 != "--":
                son_list = TREE_DATA[sel_l1][sel_l2]
                if son_list:
                    st.session_state.multi_iterations[i]["l3"] = st.radio(f"L3 - {sel_l2}", ["--"] + son_list, key=f"l3_{i}_{st.session_state.search_reset_key}")
                else: st.session_state.multi_iterations[i]["l3"] = "--"

# 3. RESULTS ENGINE
st.divider()
q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name or ID...", key=f"q_{st.session_state.search_reset_key}")

if st.session_state.search_clicked or q_search:
    df = df_raw.copy()
    valid_filters = [s for s in st.session_state.multi_iterations if s['l1'] != "--"]

    if valid_filters:
        def filter_engine(group):
            # 1. Gather all action chains present in the project rows
            project_chains = []
            for _, row in group.iterrows():
                l1, l2 = row['Level1'], row['Level2']
                l3s = [row[c] for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if row[c] and row[c] != ""]
                if not l3s:
                    project_chains.append({l1, l2})
                else:
                    for l3 in l3s:
                        project_chains.append({l1, l2, l3})
            
            # 2. Build the search target chains
            search_targets = []
            for f in valid_filters:
                t = {f['l1']}
                if f['l2'] != "--": t.add(f['l2'])
                if f['l3'] != "--": t.add(f['l3'])
                search_targets.append(t)
            
            # 3. Match logic
            # General: Every search target must be present in project_chains
            found_all_targets = all(any(target.issubset(p_chain) for p_chain in project_chains) for target in search_targets)
            
            if not found_all_targets: return False
            
            # Unique: Project must NOT have any chains that weren't in the search targets
            if unique_strict:
                for p_chain in project_chains:
                    if not any(p_chain.issubset(target) or target.issubset(p_chain) for target in search_targets):
                        return False
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
                    l3s = [str(r[c]) for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if str(r[c]).strip() and str(r[c]).lower() != 'nan']
                    st.markdown(f"<p class='mono-text'>• {r['Level1']} > {r['Level2']}" + (f" > {', '.join(l3s)}" if l3s else "") + "</p>", unsafe_allow_html=True)
                z_url = str(r1.get('Approval Pack/NOC', '')).strip()
                if z_url and z_url.lower() != 'nan': st.link_button("ZAP", z_url, use_container_width=True)