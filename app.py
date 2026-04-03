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
    .small-header {{ font-size: 1.1rem !important; font-weight: 600; color: #38BDF8; text-transform: uppercase; margin-bottom: 10px; }}
    .mono-text {{ font-family: 'Roboto Mono', monospace; font-size: 0.85rem; color: #94A3B8; margin-bottom: 5px; }}
    .remarks-box {{ background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38BDF8; padding: 10px; border-radius: 4px; font-size: 0.85rem; color: #CBD5E1; margin-top: 5px; margin-bottom: 10px; }}
    
    /* Ensure Sidebar Buttons are uniform */
    div[data-testid="stSidebarNav"] + div stButton button {{
        height: 45px !important;
        padding: 0px !important;
    }}
    
    div[data-testid="stVerticalBlock"] > div[style*="border"] {{
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px); border: 1px solid #334155 !important; border-radius: 12px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CSV & DATA HELPERS ---
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

# --- APP START ---
if "search_reset_key" not in st.session_state: st.session_state.search_reset_key = 0
df_raw = load_csv_safe('projects.csv')

st.markdown("<div class='hero-section'><h1>🏙️ TRD GOOD PROJECTS LIBRARY</h1><p style='color:#38BDF8;'>NYC ZONING ANALYTICS TERMINAL</p></div>", unsafe_allow_html=True)

# 1. Sidebar Search
st.sidebar.markdown("### 🛠️ SYSTEM FILTERS")
search_mode = st.sidebar.radio("MODE", ["Single-Action Search", "Multi-Action Search"], key=f"mode_{st.session_state.search_reset_key}")
unique_strict = False
final_l1, final_l2, final_l3 = [], [], []

if not df_raw.empty:
    if search_mode == "Single-Action Search":
        s_type = st.sidebar.segmented_control("SCOPE", ["General", "Unique"], default="General", key=f"scope_{st.session_state.search_reset_key}")
        unique_strict = (s_type == "Unique")
        l1_opts = ["All"] + sorted([str(x).strip() for x in df_raw['Level1'].unique() if str(x).strip()])
        c1 = st.sidebar.selectbox("L1", l1_opts, key=f"s1_{st.session_state.search_reset_key}")
        if c1 != "All":
            final_l1 = [c1]
            l2_opts = ["All"] + sorted([str(x).strip() for x in df_raw[df_raw['Level1'] == c1]['Level2'].unique() if str(x).strip()])
            c2 = st.sidebar.selectbox("L2", l2_opts, key=f"s2_{st.session_state.search_reset_key}")
            if c2 != "All":
                final_l2 = [c2]
                l3_all_vals = pd.unique(df_raw[df_raw['Level2'] == c2][['Level3-1','Level3-2','Level3-3','Level3-4']].values.ravel('K'))
                l3_opts = ["All"] + sorted([str(x).strip() for x in l3_all_vals if str(x).strip()])
                if len(l3_opts) > 1:
                    c3 = st.sidebar.selectbox("L3", l3_opts, key=f"s3_{st.session_state.search_reset_key}")
                    if c3 != "All": final_l3 = [c3]
    else:
        final_l1 = st.sidebar.multiselect("L1", sorted(df_raw['Level1'].unique()), key=f"m1_{st.session_state.search_reset_key}")
        final_l2 = st.sidebar.multiselect("L2", sorted(df_raw['Level2'].unique()), key=f"m2_{st.session_state.search_reset_key}")
        l3_all = pd.unique(df_raw[['Level3-1','Level3-2','Level3-3','Level3-4']].values.ravel('K'))
        final_l3 = st.sidebar.multiselect("L3", sorted([str(x).strip() for x in l3_all if str(x).strip()]), key=f"m3_{st.session_state.search_reset_key}")

st.sidebar.markdown("---")
# Side-by-Side Sidebar Buttons
side_col1, side_col2 = st.sidebar.columns(2)
with side_col1:
    if st.button("🚀 SEARCH", type="primary", use_container_width=True):
        st.session_state.search_clicked = True
with side_col2:
    if st.button("🧹 CLEAR", use_container_width=True):
        st.session_state.search_reset_key += 1
        st.session_state.search_clicked = False
        st.rerun()

# 2. Results Area
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
            return assigned == search_targets if unique_strict else search_targets.issubset(assigned)
        m_ids = df_raw.groupby('Project ID').filter(filter_logic)['Project ID'].unique()
        df = df_raw[df_raw['Project ID'].isin(m_ids)]
    if q_search: df = df[df['Project'].str.contains(q_search, case=False, na=False) | df['Project ID'].astype(str).str.contains(q_search, case=False, na=False)]
    
    grouped = df.groupby('Project ID')
    st.subheader(f"FOUND {len(grouped)} PROJECTS")
    grid = st.columns(3)
    for idx, (p_id, gp) in enumerate(grouped):
        with grid[idx % 3]:
            with st.container(border=True):
                row1 = gp.iloc[0]
                st.markdown(f"### {row1['Project']}")
                st.markdown(f"<p class='mono-text'><b>Project ID:</b> {p_id} | <b>Cert Date:</b> {row1.get('Cert Date', row1.get('Cert Year', ''))}</p>", unsafe_allow_html=True)
                
                cat_actions = []
                for _, r in gp.iterrows():
                    l3_list = [str(r[c]) for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if str(r[c]).strip() and str(r[c]).lower() != 'nan']
                    chain = f"{r['Level1']} > {r['Level2']}" + (f" > {', '.join(l3_list)}" if l3_list else "")
                    cat_actions.append(chain)
                st.markdown(f"<p class='mono-text'><b>Categorized Actions:</b><br>{'<br>'.join(['• ' + a for a in cat_actions])}</p>", unsafe_allow_html=True)
                
                rem_val = str(row1.get('Remarks', '')).strip()
                if rem_val and rem_val.lower() != 'nan' and rem_val != "":
                    st.markdown(f"<div class='remarks-box'><b>Remarks:</b> {rem_val}</div>", unsafe_allow_html=True)
                
                zap_url = str(row1.get('Approval Pack/NOC', '')).strip()
                if zap_url and zap_url.lower() != 'nan' and zap_url != "":
                    st.link_button("ZAP", zap_url, use_container_width=True)

# 3. Persistent Staging Area
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
            n_l1 = st.multiselect("L1 Categories", sorted(df_raw['Level1'].unique()) if not df_raw.empty else [])
            n_l2 = st.multiselect("L2 Sub-Categories", sorted(df_raw['Level2'].unique()) if not df_raw.empty else [])
            l3_pool = pd.unique(df_raw[['Level3-1','Level3-2','Level3-3','Level3-4']].values.ravel('K')) if not df_raw.empty else []
            n_l3 = st.multiselect("L3 Focus Areas", sorted([str(x).strip() for x in l3_pool if str(x).strip()]))
            n_rem = st.text_area("Remarks")
            if st.form_submit_button("SUBMIT"):
                if n_name and n_id and n_l1 and n_l2:
                    clean_link = n_link.strip()
                    if clean_link and not (clean_link.startswith("http://") or clean_link.startswith("https://")):
                        clean_link = "https://" + clean_link
                    new_row = {'Level1': n_l1[0], 'Level2': n_l2[0], 'Project': n_name, 'Project ID': n_id, 'Cert Date': n_date.strftime("%m-%d-%Y"), 'Approval Pack/NOC': clean_link, 'Remarks': n_rem, 'Status': 'Pending'}
                    for i in range(4): new_row[f'Level3-{i+1}'] = n_l3[i] if len(n_l3) > i else ""
                    save_row('review_queue.csv', new_row); st.rerun()
                else: st.error("Fill Name, ID, L1, and L2.")
    else: st.warning("Queue Full (20).")

with c_admin:
    st.markdown("<p class='small-header'>🕵️ Admin Review Queue</p>", unsafe_allow_html=True)
    for i, item in enumerate(queue_df.to_dict('records')):
        clean = {k: ("" if str(v).lower() == "nan" else str(v)).strip() for k, v in item.items()}
        is_app = (clean['Status'] == 'Approved')
        with st.container(border=True):
            h_col, a_col = st.columns([0.8, 0.2])
            with h_col:
                st.markdown(f"**{i+1}- {'🟢 ' if is_app else ''}{clean['Project']}**")
            l3s = [clean[c] for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if clean[c]]
            st.markdown(f"<div class='mono-text'><b>Project ID:</b> {clean['Project ID']} | <b>DATE:</b> {item.get('Cert Date', item.get('Cert Year', ''))}<br><b>Categorized Actions:</b> {clean['Level1']} > {clean['Level2']}" + (f" > {', '.join(l3s)}" if l3s else "") + "</div>", unsafe_allow_html=True)
            z_col, r_col = st.columns([0.2, 0.8])
            with z_col:
                z_link = clean.get('Approval Pack/NOC', '').strip()
                if z_link: st.link_button("ZAP", z_link, use_container_width=True)
            with r_col:
                if clean['Remarks']: st.markdown(f"<div class='remarks-box'><b>Remarks:</b> {clean['Remarks']}</div>", unsafe_allow_html=True)
            with a_col:
                b1, b2 = st.columns(2)
                if not is_app and num_app < 10:
                    if b1.button("✅", key=f"ok{i}"): update_queue_status(clean['Project ID'], "Approved"); st.rerun()
                if b2.button("🗑️", key=f"tr{i}"): delete_from_review(clean['Project ID']); st.rerun()