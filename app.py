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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

    .stApp {{ 
        background: radial-gradient(circle at top right, #0F172A, #070B14); 
        color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Headings styling */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }}
    
    .hero-section {{
        background-image: linear-gradient(rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.88)), url("data:image/jpg;base64,{img_base64}");
        background-size: cover; 
        background-position: center;
        padding: 50px 20px; 
        border-radius: 16px; 
        border: 1px solid rgba(255, 255, 255, 0.08);
        text-align: center; 
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }}
    
    .mono-text {{ 
        font-family: 'Fira Code', 'Roboto Mono', monospace; 
        font-size: 0.8rem; 
        color: #94A3B8; 
    }}
    
    .remarks-box {{ 
        background: rgba(14, 116, 144, 0.12); 
        border-left: 4px solid #38BDF8; 
        padding: 12px 16px; 
        border-radius: 6px; 
        font-size: 0.95rem; 
        color: #E2E8F0; 
        margin-top: 14px;
        margin-bottom: 14px;
        line-height: 1.4;
    }}
    
    .standardized-l1-image {{
        display: block; 
        margin-left: auto; 
        margin-right: auto;
        height: 220px; 
        width: 100%; 
        object-fit: cover;
        border-radius: 12px; 
        margin-bottom: 20px; 
        border: 2px solid rgba(56, 189, 248, 0.35);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }}
    
    div[data-testid="stSidebarNav"] + div stButton button {{ height: 45px !important; }}

    /* Custom Solid Dark Project Card matching Reference screenshot */
    .glass-card {{
        background: #0B132B;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 24px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 260px;
        height: 100%;
    }}
    
    .glass-card:hover {{
        transform: translateY(-2px);
        border-color: #38BDF8;
        box-shadow: 0 12px 40px rgba(56, 189, 248, 0.15);
    }}

    /* Badges */
    .badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-right: 4px;
        margin-bottom: 4px;
        font-family: 'Inter', sans-serif;
    }}
    .badge-l1-use {{ background: rgba(16, 185, 129, 0.12); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.25); }}
    .badge-l1-bulk {{ background: rgba(99, 102, 241, 0.12); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.25); }}
    .badge-l1-parking {{ background: rgba(245, 158, 11, 0.12); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.25); }}
    .badge-l1-open {{ background: rgba(14, 165, 233, 0.12); color: #38BDF8; border: 1px solid rgba(14, 165, 233, 0.25); }}
    .badge-l1-misc {{ background: rgba(236, 72, 153, 0.12); color: #F472B6; border: 1px solid rgba(236, 72, 153, 0.25); }}

    .badge-l2 {{ background: rgba(255, 255, 255, 0.05); color: #E2E8F0; border: 1px solid rgba(255, 255, 255, 0.08); }}
    .badge-l3 {{ background: rgba(99, 102, 241, 0.06); color: #A5B4FC; border: 1px solid rgba(99, 102, 241, 0.15); font-style: italic; }}

    /* Login Panel */
    .login-container {{
        max-width: 420px;
        margin: 60px auto;
        padding: 40px;
        background: rgba(22, 28, 45, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        text-align: center;
    }}

    /* Metrics Dashboard */
    .metrics-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 16px;
        margin-bottom: 25px;
    }}
    
    .metric-card {{
        background: rgba(30, 41, 59, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 18px 12px;
        border-radius: 12px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }}
    
    .metric-card:hover {{
        border-color: rgba(99, 102, 241, 0.35);
        background: rgba(30, 41, 59, 0.55);
        transform: translateY(-2px);
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: #818CF8;
        font-family: 'Outfit', sans-serif;
        margin-bottom: 4px;
    }}
    
    .metric-label {{
        font-size: 0.72rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }}

    /* Zap Document Button */
    .zap-btn {{
        display: block;
        text-align: center;
        background: transparent;
        color: #FFFFFF !important;
        text-decoration: none !important;
        padding: 12px 20px;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        border: 1px solid #374151;
        margin-top: 15px;
        letter-spacing: 0.05em;
    }}
    .zap-btn:hover {{
        background: rgba(255, 255, 255, 0.05);
        border-color: #38BDF8;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.15);
    }}

    /* Custom styles for Streamlit widgets to elevate their look */
    .stSelectbox div[data-baseweb="select"] {{
        background-color: rgba(15, 23, 42, 0.5) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    .stTextInput input {{
        background-color: rgba(15, 23, 42, 0.5) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }}
    
    .stTextArea textarea {{
        background-color: rgba(15, 23, 42, 0.5) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }}

    /* Streamlit native tab tweaks */
    button[data-baseweb="tab"] {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #94A3B8 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #818CF8 !important;
        border-bottom-color: #818CF8 !important;
    }}

    /* Default Multiselect styling to prevent default red boxes */
    span[data-baseweb="tag"],
    div[data-baseweb="tag"] {{
        background-color: rgba(129, 140, 248, 0.08) !important;
        color: #A5B4FC !important;
        border: 1px solid rgba(129, 140, 248, 0.2) !important;
    }}
    div[data-baseweb="select"] {{
        border-color: rgba(255, 255, 255, 0.1) !important;
    }}

    /* Normalize label links to look like standard text */
    div[data-testid="stWidgetLabel"] a {{
        text-decoration: none !important;
        color: inherit !important;
        pointer-events: none !important;
    }}

    /* USE WAIVERS: GREEN */
    div[data-testid="stMultiSelect"]:has(a[href="https://use-waivers"]) div[data-baseweb="select"],
    div[data-testid="stSelectbox"]:has(a[href="https://use-waivers"]) div[data-baseweb="select"] {{
        border-color: rgba(52, 211, 153, 0.35) !important;
    }}
    div[data-testid="stMultiSelect"]:has(a[href="https://use-waivers"]) div[data-baseweb="select"]:focus-within,
    div[data-testid="stSelectbox"]:has(a[href="https://use-waivers"]) div[data-baseweb="select"]:focus-within {{
        border-color: #34D399 !important;
        box-shadow: 0 0 0 1px #34D399 !important;
    }}
    div[data-testid="stMultiSelect"]:has(a[href="https://use-waivers"]) span[data-baseweb="tag"],
    div[data-testid="stMultiSelect"]:has(a[href="https://use-waivers"]) div[data-baseweb="tag"] {{
        background-color: rgba(52, 211, 153, 0.15) !important;
        color: #34D399 !important;
        border: 1px solid rgba(52, 211, 153, 0.35) !important;
    }}

    /* BULK WAIVERS: VIOLET */
    div[data-testid="stMultiSelect"]:has(a[href="https://bulk-waivers"]) div[data-baseweb="select"],
    div[data-testid="stSelectbox"]:has(a[href="https://bulk-waivers"]) div[data-baseweb="select"] {{
        border-color: rgba(129, 140, 248, 0.35) !important;
    }}
    div[data-testid="stMultiSelect"]:has(a[href="https://bulk-waivers"]) div[data-baseweb="select"]:focus-within,
    div[data-testid="stSelectbox"]:has(a[href="https://bulk-waivers"]) div[data-baseweb="select"]:focus-within {{
        border-color: #818CF8 !important;
        box-shadow: 0 0 0 1px #818CF8 !important;
    }}
    div[data-testid="stMultiSelect"]:has(a[href="https://bulk-waivers"]) span[data-baseweb="tag"],
    div[data-testid="stMultiSelect"]:has(a[href="https://bulk-waivers"]) div[data-baseweb="tag"] {{
        background-color: rgba(129, 140, 248, 0.15) !important;
        color: #818CF8 !important;
        border: 1px solid rgba(129, 140, 248, 0.35) !important;
    }}

    /* PARKING & CURBCUTS: ORANGE/AMBER */
    div[data-testid="stMultiSelect"]:has(a[href="https://parking-curbcuts"]) div[data-baseweb="select"],
    div[data-testid="stSelectbox"]:has(a[href="https://parking-curbcuts"]) div[data-baseweb="select"] {{
        border-color: rgba(251, 191, 36, 0.35) !important;
    }}
    div[data-testid="stMultiSelect"]:has(a[href="https://parking-curbcuts"]) div[data-baseweb="select"]:focus-within,
    div[data-testid="stSelectbox"]:has(a[href="https://parking-curbcuts"]) div[data-baseweb="select"]:focus-within {{
        border-color: #FBBF24 !important;
        box-shadow: 0 0 0 1px #FBBF24 !important;
    }}
    div[data-testid="stMultiSelect"]:has(a[href="https://parking-curbcuts"]) span[data-baseweb="tag"],
    div[data-testid="stMultiSelect"]:has(a[href="https://parking-curbcuts"]) div[data-baseweb="tag"] {{
        background-color: rgba(251, 191, 36, 0.15) !important;
        color: #FBBF24 !important;
        border: 1px solid rgba(251, 191, 36, 0.35) !important;
    }}

    /* OPEN SPACE: BLUE */
    div[data-testid="stMultiSelect"]:has(a[href="https://open-space"]) div[data-baseweb="select"],
    div[data-testid="stSelectbox"]:has(a[href="https://open-space"]) div[data-baseweb="select"] {{
        border-color: rgba(56, 189, 248, 0.35) !important;
    }}
    div[data-testid="stMultiSelect"]:has(a[href="https://open-space"]) div[data-baseweb="select"]:focus-within,
    div[data-testid="stSelectbox"]:has(a[href="https://open-space"]) div[data-baseweb="select"]:focus-within {{
        border-color: #38BDF8 !important;
        box-shadow: 0 0 0 1px #38BDF8 !important;
    }}
    div[data-testid="stMultiSelect"]:has(a[href="https://open-space"]) span[data-baseweb="tag"],
    div[data-testid="stMultiSelect"]:has(a[href="https://open-space"]) div[data-baseweb="tag"] {{
        background-color: rgba(56, 189, 248, 0.15) !important;
        color: #38BDF8 !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
    }}

    /* MISCELLANEOUS: RED */
    div[data-testid="stMultiSelect"]:has(a[href="https://miscellaneous"]) div[data-baseweb="select"],
    div[data-testid="stSelectbox"]:has(a[href="https://miscellaneous"]) div[data-baseweb="select"] {{
        border-color: rgba(244, 114, 182, 0.35) !important;
    }}
    div[data-testid="stMultiSelect"]:has(a[href="https://miscellaneous"]) div[data-baseweb="select"]:focus-within,
    div[data-testid="stSelectbox"]:has(a[href="https://miscellaneous"]) div[data-baseweb="select"]:focus-within {{
        border-color: #F472B6 !important;
        box-shadow: 0 0 0 1px #F472B6 !important;
    }}
    div[data-testid="stMultiSelect"]:has(a[href="https://miscellaneous"]) span[data-baseweb="tag"],
    div[data-testid="stMultiSelect"]:has(a[href="https://miscellaneous"]) div[data-baseweb="tag"] {{
        background-color: rgba(244, 114, 182, 0.15) !important;
        color: #F472B6 !important;
        border: 1px solid rgba(244, 114, 182, 0.35) !important;
    }}

    /* LEVEL 1 SELECTED PILLS COLOR TARGETING BY EMOJI/TITLE */
    /* USE WAIVERS: GREEN */
    span[data-baseweb="tag"]:has([title*="Use Waivers"]),
    div[data-baseweb="tag"]:has([title*="Use Waivers"]),
    span[data-baseweb="tag"]:has([title*="🟢"]),
    div[data-baseweb="tag"]:has([title*="🟢"]) {{
        background-color: rgba(52, 211, 153, 0.15) !important;
        color: #34D399 !important;
        border: 1px solid rgba(52, 211, 153, 0.35) !important;
    }}

    /* BULK WAIVERS: VIOLET */
    span[data-baseweb="tag"]:has([title*="Bulk Waivers"]),
    div[data-baseweb="tag"]:has([title*="Bulk Waivers"]),
    span[data-baseweb="tag"]:has([title*="🟣"]),
    div[data-baseweb="tag"]:has([title*="🟣"]) {{
        background-color: rgba(129, 140, 248, 0.15) !important;
        color: #818CF8 !important;
        border: 1px solid rgba(129, 140, 248, 0.35) !important;
    }}

    /* PARKING & CURBCUTS: ORANGE */
    span[data-baseweb="tag"]:has([title*="Parking"]),
    div[data-baseweb="tag"]:has([title*="Parking"]),
    span[data-baseweb="tag"]:has([title*="🟡"]),
    div[data-baseweb="tag"]:has([title*="🟡"]) {{
        background-color: rgba(251, 191, 36, 0.15) !important;
        color: #FBBF24 !important;
        border: 1px solid rgba(251, 191, 36, 0.35) !important;
    }}

    /* OPEN SPACE: BLUE */
    span[data-baseweb="tag"]:has([title*="Open Space"]),
    div[data-baseweb="tag"]:has([title*="Open Space"]),
    span[data-baseweb="tag"]:has([title*="🔵"]),
    div[data-baseweb="tag"]:has([title*="🔵"]) {{
        background-color: rgba(56, 189, 248, 0.15) !important;
        color: #38BDF8 !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
    }}

    /* MISCELLANEOUS: RED */
    span[data-baseweb="tag"]:has([title*="Miscellaneous"]),
    div[data-baseweb="tag"]:has([title*="Miscellaneous"]),
    span[data-baseweb="tag"]:has([title*="🔴"]),
    div[data-baseweb="tag"]:has([title*="🔴"]) {{
        background-color: rgba(244, 114, 182, 0.15) !important;
        color: #F472B6 !important;
        border: 1px solid rgba(244, 114, 182, 0.35) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def make_unicode_bold(text):
    bold_chars = ""
    for char in text:
        codepoint = ord(char)
        if 65 <= codepoint <= 90:
            bold_chars += chr(codepoint - 65 + 0x1D400)
        elif 97 <= codepoint <= 122:
            bold_chars += chr(codepoint - 97 + 0x1D41A)
        elif 48 <= codepoint <= 57:
            bold_chars += chr(codepoint - 48 + 0x1D7CE)
        else:
            bold_chars += char
    return bold_chars

def format_l1(option):
    mapping = {
        "Use_Waivers": "🟢 Use Waivers",
        "Bulk_Waivers": "🟣 Bulk Waivers",
        "Parking_Curbcuts": "🟡 Parking & Curbcuts",
        "Open_Space": "🔵 Open Space",
        "Miscellaneous": "🔴 Miscellaneous"
    }
    return mapping.get(option, option)

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
        "Waterfronts": ["WPAA Certification", "WPAA Certification with DEC Wetlands", "No-WPAA Certification", "Zoning Lot Subdivision Certifications"],
        "Open Space Site Plans": []
    },
    "Miscellaneous": {
        "image_file": "Miscellaneous.jpg",
        "LSGD": ["Single Zoning Lot", "Multi Zoning Lot", "Existing Buildings"],
        "FRESH": ["Fresh Certification", "Fresh with Authorization"],
        "Transit Easement Certs": [], "Transit Improvement Bonus": [], "Houses of Worships": [], "RRROW": [], "Greater East Midtown": []
    }
}

L1_STYLE = {
    "Use_Waivers": {"color": "green", "hex": "#34D399", "emoji": "🟢", "name": "Use Waivers", "url": "https://use-waivers"},
    "Bulk_Waivers": {"color": "violet", "hex": "#818CF8", "emoji": "🟣", "name": "Bulk Waivers", "url": "https://bulk-waivers"},
    "Parking_Curbcuts": {"color": "orange", "hex": "#FBBF24", "emoji": "🟡", "name": "Parking & Curbcuts", "url": "https://parking-curbcuts"},
    "Open_Space": {"color": "blue", "hex": "#38BDF8", "emoji": "🔵", "name": "Open Space", "url": "https://open-space"},
    "Miscellaneous": {"color": "red", "hex": "#F472B6", "emoji": "🔴", "name": "Miscellaneous", "url": "https://miscellaneous"}
}

def load_csv_safe(file_path):
    if not os.path.exists(file_path): return pd.DataFrame()
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', encoding_errors='replace', dtype=str)
    except Exception:
        try:
            df = pd.read_csv(file_path, encoding='cp1252', encoding_errors='replace', dtype=str)
        except Exception:
            try:
                df = pd.read_csv(file_path, encoding='latin1', dtype=str)
            except Exception:
                return pd.DataFrame()
                
    df.columns = [str(c).strip() for c in df.columns]
    
    # Check if first row is the actual header row (due to comment line at the top)
    if not df.empty and 'Project ID' not in df.columns:
        if 'Project' in df.iloc[0].values and 'Project ID' in df.iloc[0].values:
            df.columns = [str(c).strip() for c in df.iloc[0]]
            df = df[1:].reset_index(drop=True)
            
    # Normalize headers for uniform access
    if 'Cert Date' in df.columns and 'Cert Year' not in df.columns:
        df['Cert Year'] = df['Cert Date']
    if 'ZR Sections' in df.columns and 'ZR Section' not in df.columns:
        df['ZR Section'] = df['ZR Sections']
    elif 'ZR Section' in df.columns and 'ZR Sections' not in df.columns:
        df['ZR Sections'] = df['ZR Section']
        
    return df.fillna("").map(lambda x: str(x).strip())

def save_row(file_path, data_dict):
    file_exists = os.path.isfile(file_path)
    if "review_queue" in file_path:
        fieldnames = [
            'Project', 'Project ID', 'Approval Pack/NOC', 'Project Desc.', 
            'ZR Section', 'Sample Categories', 'Remarks', 'Cert Year', 
            'Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4', 'Status'
        ]
    else:
        fieldnames = [
            'Project', 'Project ID', 'Approval Pack/NOC', 'Project Desc.', 
            'ZR Sections', 'Sample Categories', 'Remarks', 'Cert Year', 
            'Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4'
        ]
        
    with open(file_path, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists: 
            writer.writeheader()
        
        row_data = {}
        for k in fieldnames:
            val = data_dict.get(k)
            if val is None:
                if k == 'ZR Sections':
                    val = data_dict.get('ZR Section', '')
                elif k == 'ZR Section':
                    val = data_dict.get('ZR Sections', '')
                elif k == 'Cert Year':
                    val = data_dict.get('Cert Date', '')
                elif k == 'Cert Date':
                    val = data_dict.get('Cert Year', '')
                else:
                    val = ''
            row_data[k] = str(val).strip()
            
        writer.writerow(row_data)

# --- AUTHENTICATION ---
if "password_correct" not in st.session_state: st.session_state.password_correct = False
if not st.session_state.password_correct:
    st.markdown("""<div class="login-container">
<div style="font-size: 3.5rem; margin-bottom: 10px;">🏙️</div>
<h2 style="margin: 0; color: #FFFFFF; font-size: 1.8rem; font-family: 'Outfit';">TRD GOOD PROJECTS</h2>
<p style="color: #94A3B8; margin-top: 5px; margin-bottom: 25px; font-size: 0.9rem;">Digital Database Portal</p>""", unsafe_allow_html=True)
    
    with st.form("login"):
        pw = st.text_input("Access Passcode", type="password", help="Enter portal security passcode.")
        if st.form_submit_button("UNLOCK DATABASE", use_container_width=True):
            if pw == "1234567890":
                st.session_state.password_correct = True
                st.rerun()
            else: 
                st.error("Invalid passcode. Access Denied.")
                
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- INITIALIZE STATE ---
if "search_reset_key" not in st.session_state: st.session_state.search_reset_key = 0
if "multi_iterations" not in st.session_state: st.session_state.multi_iterations = [{"l1": "--", "l2": "--", "l3": "--"}]
if "search_clicked" not in st.session_state: st.session_state.search_clicked = False
if "edit_reset_key" not in st.session_state: st.session_state.edit_reset_key = 0

df_raw = load_csv_safe('projects.csv')

# --- HERO SECTION ---
st.markdown(f"""
<div class='hero-section'>
    <h1 style='margin: 0; font-size: 2.5rem; color: #FFFFFF; font-family: "Outfit", sans-serif;'>
        🏙️ TRD GOOD PROJECTS DIGITAL DATABASE
    </h1>
</div>
""", unsafe_allow_html=True)

# --- STATS DASHBOARD METRICS ---
if not df_raw.empty:
    total_projects = len(df_raw['Project ID'].unique())
    total_records = len(df_raw)
    l1_counts = df_raw['Level1'].value_counts()
    use_waivers_cnt = l1_counts.get('Use_Waivers', 0)
    bulk_waivers_cnt = l1_counts.get('Bulk_Waivers', 0)
    open_space_cnt = l1_counts.get('Open_Space', 0)
else:
    total_projects = 0
    total_records = 0
    use_waivers_cnt = 0
    bulk_waivers_cnt = 0
    open_space_cnt = 0

q_df_cnt = 0
if os.path.exists('review_queue.csv'):
    try:
        q_df_cnt = len(load_csv_safe('review_queue.csv'))
    except:
        pass

st.markdown(f"""
<div class="metrics-grid">
    <div class="metric-card">
        <div class="metric-value">{total_projects}</div>
        <div class="metric-label">Total Projects</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #34D399;">{use_waivers_cnt}</div>
        <div class="metric-label">Use Waivers</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #818CF8;">{bulk_waivers_cnt}</div>
        <div class="metric-label">Bulk Waivers</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #38BDF8;">{open_space_cnt}</div>
        <div class="metric-label">Open Spaces</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #FBBF24;">{q_df_cnt}</div>
        <div class="metric-label">Pending Queue</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 1. SIDEBAR CONFIG ---
st.sidebar.markdown("### 🛠️ CONFIGURATION")
search_mode = st.sidebar.radio("SEARCH MODE", ["Single-Action Search", "Multi-Action Search"], key=f"mode_{st.session_state.search_reset_key}")

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

# --- 2. WORKSPACE / SEARCH FILTERS ---
col_hdr, col_reset = st.columns([0.75, 0.25])
with col_hdr:
    st.subheader("🌳 Project Search Filter")
with col_reset:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Reset Filtering", key="workspace_reset_btn", use_container_width=True):
        st.session_state.search_reset_key += 1
        st.session_state.multi_iterations = [{"l1": "--", "l2": "--", "l3": "--"}]
        st.session_state.search_clicked = False
        st.rerun()

workspace_cols = st.columns(len(st.session_state.multi_iterations))

for i, iteration in enumerate(st.session_state.multi_iterations):
    with workspace_cols[i]:
        sel_l1 = st.session_state.multi_iterations[i]["l1"]
        if sel_l1 != "--":
            img_b64 = get_base64_image(TREE_DATA[sel_l1]["image_file"])
            if img_b64: 
                st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="standardized-l1-image">', unsafe_allow_html=True)
            else:
                st.markdown("<div style='height:220px;'></div>", unsafe_allow_html=True)
        else: 
            st.markdown("""<div style='height:220px; display: flex; align-items: center; justify-content: center; border: 2px dashed rgba(255, 255, 255, 0.06); border-radius: 12px; margin-bottom: 20px; background: rgba(255,255,255,0.01);'>
<div style='text-align: center; color: #64748B;'>
<svg style='width: 40px; height: 40px; margin: 0 auto 10px auto; opacity: 0.35;' fill='none' stroke='currentColor' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'>
<path stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z'></path>
</svg>
<span style='font-size: 0.8rem; font-weight: 500;'>No L1 Category Selected</span>
</div>
</div>""", unsafe_allow_html=True)
        
        # Define style values if L1 is selected
        style = L1_STYLE.get(sel_l1, {"color": "green", "hex": "#34D399", "emoji": "🟢", "name": sel_l1, "url": "https://use-waivers"})
        c_color = style["color"]
        c_hex = style["hex"]
        c_emoji = style["emoji"]
        c_name = style["name"]
        c_url = style["url"]
        
        if sel_l1 != "--":
            # Add a colored left border header above the L1 select box
            st.markdown(f"""
            <div style="border-left: 4px solid {c_hex}; padding-left: 10px; margin-bottom: 8px;">
                <span style="color: {c_hex}; font-weight: 600; font-size: 0.95rem; font-family: 'Outfit';">
                    {c_emoji} {c_name.upper()}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            l1_label = f"[{c_emoji}]({c_url}) :{c_color}[L1 Selection (Col {i+1})]"
        else:
            l1_label = f"L1 Selection (Col {i+1})"
            
        st.session_state.multi_iterations[i]["l1"] = st.selectbox(l1_label, ["--"] + list(TREE_DATA.keys()), key=f"l1_{i}_{st.session_state.search_reset_key}", format_func=format_l1)
        
        cur_l1 = st.session_state.multi_iterations[i]["l1"]
        if cur_l1 != "--":
            daddy_list = [k for k in TREE_DATA[cur_l1].keys() if k != "image_file"]
            
            # Formatter for Level 2 options (bold if they have subcategories)
            def format_l2_search(option):
                if option == "--":
                    return option
                has_l3 = bool(TREE_DATA.get(cur_l1, {}).get(option))
                if has_l3:
                    return make_unicode_bold(option)
                return option
                
            l2_label = f":{c_color}[{c_emoji} L2 - {c_name}]"
            st.session_state.multi_iterations[i]["l2"] = st.radio(l2_label, ["--"] + daddy_list, key=f"l2_{i}_{st.session_state.search_reset_key}", format_func=format_l2_search)
            
            cur_l2 = st.session_state.multi_iterations[i]["l2"]
            if cur_l2 != "--":
                son_list = TREE_DATA[cur_l1][cur_l2]
                if son_list:
                    l3_label = f":{c_color}[{c_emoji} L3 - {cur_l2}]"
                    st.session_state.multi_iterations[i]["l3"] = st.radio(l3_label, ["--"] + son_list, key=f"l3_{i}_{st.session_state.search_reset_key}")
                else: st.session_state.multi_iterations[i]["l3"] = "--"
            else:
                st.session_state.multi_iterations[i]["l3"] = "--"
        else:
            st.session_state.multi_iterations[i]["l2"] = "--"
            st.session_state.multi_iterations[i]["l3"] = "--"

# Navigation
st.markdown("<br>", unsafe_allow_html=True)
nav1, nav2, _ = st.columns([0.15, 0.15, 0.7])
if search_mode == "Multi-Action Search" and len(st.session_state.multi_iterations) < 5:
    if nav1.button("➕ CONTINUE FILTER", use_container_width=True):
        st.session_state.multi_iterations.append({"l1": "--", "l2": "--", "l3": "--"})
        st.rerun()

if search_mode == "Multi-Action Search" and len(st.session_state.multi_iterations) > 1:
    if nav2.button("🏁 FINISH", use_container_width=True):
        st.success("Search Filter locked.")

# --- 3. RESULTS ENGINE ---
st.divider()
q_search = st.text_input("📝 KEYWORD SEARCH", placeholder="Search project name, ID, or description...", key=f"q_{st.session_state.search_reset_key}")

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
        df = df[
            df['Project'].str.contains(q_search, case=False, na=False) | 
            df['Project ID'].astype(str).str.contains(q_search, case=False, na=False) | 
            df.get('Remarks', pd.Series(dtype=str)).str.contains(q_search, case=False, na=False) |
            df.get('Project Desc.', pd.Series(dtype=str)).str.contains(q_search, case=False, na=False) |
            df.get('ZR Section', pd.Series(dtype=str)).str.contains(q_search, case=False, na=False) |
            df.get('ZR Sections', pd.Series(dtype=str)).str.contains(q_search, case=False, na=False) |
            df.get('Sample Categories', pd.Series(dtype=str)).str.contains(q_search, case=False, na=False)
        ]

    grouped_projects = df.groupby('Project ID')
    st.subheader(f"FOUND {len(grouped_projects)} PROJECTS MATCHING SELECTION")
    
    res_grid = st.columns(3)
    for idx, (p_id, gp) in enumerate(grouped_projects):
        with res_grid[idx % 3]:
            r1 = gp.iloc[0]
            
            # Formulating a custom HTML/CSS card exactly matching the reference design layout
            # Note: We must not include leading whitespace/indentation in the multiline HTML strings,
            # otherwise Streamlit's markdown parser will interpret them as code blocks.
            cert_yr = r1.get('Cert Year', r1.get('Cert Date', ''))
            card_html = f"""<div class="glass-card">
<div>
<h3 style="margin: 0; font-size: 1.6rem; color: #FFFFFF; font-family: 'Inter', sans-serif; font-weight: 600; line-height: 1.25;">{r1['Project']}</h3>
<div style="font-family: 'Fira Code', 'Roboto Mono', monospace; font-size: 0.85rem; color: #94A3B8; margin-top: 12px; margin-bottom: 12px; font-weight: 500;">
ID: {p_id} &nbsp;|&nbsp; Year: {cert_yr}
</div>"""

            desc_val = str(r1.get('Project Desc.', '')).strip()
            if desc_val and desc_val.lower() not in ["", "nan", "none"]:
                card_html += f"""
<p style="font-size: 0.9rem; color: #CBD5E1; line-height: 1.4; margin-top: 8px; margin-bottom: 12px; font-family: 'Inter', sans-serif;">{desc_val}</p>"""

            zr_val = str(r1.get('ZR Section', r1.get('ZR Sections', ''))).strip()
            sample_val = str(r1.get('Sample Categories', '')).strip()
            if zr_val and zr_val.lower() not in ["", "nan", "none"]:
                card_html += f"""
<div style="font-family: 'Fira Code', 'Roboto Mono', monospace; font-size: 0.8rem; color: #94A3B8; margin-bottom: 6px;">
<strong>ZR Section:</strong> {zr_val}
</div>"""
            if sample_val and sample_val.lower() not in ["", "nan", "none"]:
                card_html += f"""
<div style="font-family: 'Fira Code', 'Roboto Mono', monospace; font-size: 0.8rem; color: #94A3B8; margin-bottom: 12px;">
<strong>Sample Categories:</strong> {sample_val}
</div>"""

            card_html += """
<div style="margin-bottom: 12px;">"""
            
            for _, r in gp.iterrows():
                l1 = r['Level1']
                l2 = r['Level2']
                l3s = [str(r[c]).strip() for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if str(r[c]).strip() and str(r[c]).lower() not in ["", "nan", "--"]]
                
                # Format category chain: Level1 > Level2 > Level3-1, Level3-2...
                chain = f"{l1} > {l2}" + (f" > {', '.join(l3s)}" if l3s else "")
                
                card_html += f"""
<div style="font-family: 'Fira Code', 'Roboto Mono', monospace; font-size: 0.85rem; color: #94A3B8; margin-bottom: 12px; line-height: 1.5;">
• {chain}
</div>"""
                
                rem_val = str(r.get('Remarks', '')).strip()
                if rem_val and rem_val.lower() not in ["", "nan", "none"]:
                    card_html += f"""
<div class="remarks-box">
<strong style="color: #FFFFFF; font-family: 'Inter', sans-serif; display: block; margin-bottom: 4px; font-weight: 600;">Remarks:</strong>
<span style="font-family: 'Fira Code', 'Roboto Mono', monospace; color: #E2E8F0; font-size: 0.85rem;">{rem_val}</span>
</div>"""
            
            card_html += """
</div>
</div>"""
            
            zap_url = str(r1.get('Approval Pack/NOC', '')).strip()
            if zap_url and zap_url.lower() not in ["", "nan", "none"]:
                card_html += f"""
<a href="{zap_url}" target="_blank" class="zap-btn" style="font-family: 'Inter', sans-serif; font-weight: 600;">
ZAP
</a>"""
            
            card_html += "</div>"
            st.markdown(card_html, unsafe_allow_html=True)

# --- 4. ADMIN CONTROL CENTER ---
st.divider()
st.subheader("🔑 Administrative Control Center")
admin_tabs = st.tabs(["📋 Review Queue", "➕ Add New Project", "✏️ Edit / Delete Database", "💾 Backup & CSV Tools"])

# TAB 1: REVIEW QUEUE
with admin_tabs[0]:
    q_df = load_csv_safe('review_queue.csv')
    
    # 1. PENDING REVIEW QUEUE
    st.markdown("### 📋 Pending Review Queue")
    
    pending_df = q_df[q_df['Status'].str.strip().str.lower() == 'pending'] if not q_df.empty else pd.DataFrame()
    approved_df = q_df[q_df['Status'].str.strip().str.lower() == 'approved'] if not q_df.empty else pd.DataFrame()
    
    num_approved = len(approved_df)
    
    if pending_df.empty:
        st.info("No pending submissions in the queue.")
    else:
        for i, row in pending_df.iterrows():
            with st.container(border=True):
                col_info, col_actions = st.columns([3, 1])
                with col_info:
                    st.markdown(f"**Project:** {row['Project']} | **ID:** {row['Project ID']} | **Year:** {row.get('Cert Year', row.get('Cert Date', ''))}")
                    l3s = [str(row[c]).strip() for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if str(row[c]).strip() and str(row[c]).lower() not in ["", "nan", "--"]]
                    chain = f"{row['Level1']} > {row['Level2']}" + (f" > {', '.join(l3s)}" if l3s else "")
                    st.markdown(f"<span class='badge badge-l1-use'>{chain}</span>", unsafe_allow_html=True)
                    
                    desc_val = str(row.get('Project Desc.', '')).strip()
                    if desc_val and desc_val.lower() not in ["", "nan", "none"]:
                        st.markdown(f"**Description:** {desc_val}")
                    
                    zr_val = str(row.get('ZR Section', row.get('ZR Sections', ''))).strip()
                    sample_val = str(row.get('Sample Categories', '')).strip()
                    if zr_val and zr_val.lower() not in ["", "nan", "none"]:
                        st.markdown(f"**ZR Section:** `{zr_val}`")
                    if sample_val and sample_val.lower() not in ["", "nan", "none"]:
                        st.markdown(f"**Sample Categories:** `{sample_val}`")
                        
                    if row.get('Remarks', '').strip():
                        st.markdown(f"<div class='remarks-box'><b>Remarks:</b> {row['Remarks']}</div>", unsafe_allow_html=True)
                with col_actions:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        approve_disabled = (num_approved >= 10)
                        if st.button("✅ Approve", key=f"appr_{i}", use_container_width=True, disabled=approve_disabled, help="Approve this submission (max 10 allowed)"):
                            q_df_live = load_csv_safe('review_queue.csv')
                            q_df_live.at[i, 'Status'] = 'Approved'
                            q_df_live.to_csv('review_queue.csv', index=False, encoding='utf-8-sig')
                            st.success(f"Approved '{row['Project']}'! It is now in the Approved Projects list.")
                            st.rerun()
                    with btn_col2:
                        if st.button("🗑️ Delete", key=f"rej_{i}", use_container_width=True):
                            q_df_live = load_csv_safe('review_queue.csv')
                            q_df_live = q_df_live.drop(i)
                            q_df_live.to_csv('review_queue.csv', index=False, encoding='utf-8-sig')
                            st.warning(f"Removed '{row['Project']}' from queue.")
                            st.rerun()
                            
    # 2. APPROVED PROJECTS LIST (MAX 10)
    st.divider()
    st.markdown("### ✅ Approved Projects List (max 10)")
    if num_approved >= 10:
        st.warning("⚠️ Maximum of 10 approved projects reached. Please add them to the CSV database to make room for more.")
        
    if approved_df.empty:
        st.info("No approved projects in the list.")
    else:
        for i, row in approved_df.iterrows():
            with st.container(border=True):
                col_info, col_actions = st.columns([3, 1])
                with col_info:
                    st.markdown(f"✅ **{row['Project']}** (ID: {row['Project ID']}) | **Year:** {row.get('Cert Year', row.get('Cert Date', ''))}")
                    l3s = [str(row[c]).strip() for c in ['Level3-1','Level3-2','Level3-3','Level3-4'] if str(row[c]).strip() and str(row[c]).lower() not in ["", "nan", "--"]]
                    chain = f"{row['Level1']} > {row['Level2']}" + (f" > {', '.join(l3s)}" if l3s else "")
                    st.markdown(f"<span class='badge badge-l1-bulk'>{chain}</span>", unsafe_allow_html=True)
                    
                    desc_val = str(row.get('Project Desc.', '')).strip()
                    if desc_val and desc_val.lower() not in ["", "nan", "none"]:
                        st.markdown(f"**Description:** {desc_val}")
                    
                    zr_val = str(row.get('ZR Section', row.get('ZR Sections', ''))).strip()
                    sample_val = str(row.get('Sample Categories', '')).strip()
                    if zr_val and zr_val.lower() not in ["", "nan", "none"]:
                        st.markdown(f"**ZR Section:** `{zr_val}`")
                    if sample_val and sample_val.lower() not in ["", "nan", "none"]:
                        st.markdown(f"**Sample Categories:** `{sample_val}`")
                        
                    if row.get('Remarks', '').strip():
                        st.markdown(f"<div class='remarks-box'><b>Remarks:</b> {row['Remarks']}</div>", unsafe_allow_html=True)
                with col_actions:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("📥 Add to CSV", key=f"add_db_{i}", use_container_width=True, help="Save to live database and delete from queue"):
                            new_proj_row = {
                                'Level1': row['Level1'],
                                'Level2': row['Level2'],
                                'Level3-1': row['Level3-1'],
                                'Level3-2': row['Level3-2'],
                                'Level3-3': row['Level3-3'],
                                'Level3-4': row['Level3-4'],
                                'Project': row['Project'],
                                'Project ID': row['Project ID'],
                                'Cert Year': row.get('Cert Year', row.get('Cert Date', '')),
                                'Approval Pack/NOC': row['Approval Pack/NOC'],
                                'Project Desc.': row.get('Project Desc.', ''),
                                'ZR Section': row.get('ZR Section', row.get('ZR Sections', '')),
                                'Sample Categories': row.get('Sample Categories', ''),
                                'Remarks': row['Remarks']
                            }
                            save_row('projects.csv', new_proj_row)
                            q_df_live = load_csv_safe('review_queue.csv')
                            q_df_live = q_df_live.drop(i)
                            q_df_live.to_csv('review_queue.csv', index=False, encoding='utf-8-sig')
                            st.success(f"Added '{row['Project']}' to the live database CSV and removed from queue!")
                            st.rerun()
                    with btn_col2:
                        if st.button("🗑️ Delete", key=f"del_appr_{i}", use_container_width=True, help="Remove from queue without saving to database"):
                            q_df_live = load_csv_safe('review_queue.csv')
                            q_df_live = q_df_live.drop(i)
                            q_df_live.to_csv('review_queue.csv', index=False, encoding='utf-8-sig')
                            st.warning(f"Deleted approved project '{row['Project']}'.")
                            st.rerun()

# TAB 2: ADD NEW ENTRY
with admin_tabs[1]:
    st.markdown("### ➕ Add New Database Entry")
    add_name = st.text_input("Project Name *", placeholder="e.g., Queens Plaza Residential", key="add_name")
    add_id = st.text_input("Project ID / ULURP Number *", placeholder="e.g., N210045ZRK", key="add_id")
    add_year = st.text_input("Certification Year (Cert Year)", placeholder="e.g., 2024 or 21-Sep", key="add_year")
    add_desc = st.text_area("Project Description (Project Desc.)", placeholder="Enter brief overview of the project actions and waivers...", key="add_desc")
    
    col_inputs1, col_inputs2 = st.columns(2)
    with col_inputs1:
        add_zr = st.text_input("ZR Section", placeholder="e.g., 74-48, 33-432", key="add_zr")
    with col_inputs2:
        add_sample = st.text_input("Sample Categories", placeholder="e.g., Sky Exposure Plane", key="add_sample")
        
    add_l1_list = st.multiselect("Level 1 Categories * (Select one or more)", list(TREE_DATA.keys()), key="add_l1_list", format_func=format_l1)

    # Dynamic selection of Level 2 and Level 3 categories for EACH selected Level 1 category
    selected_classifications = {} # keys: (l1, l2), values: list of selected l3 categories
    
    if add_l1_list:
        for l1 in add_l1_list:
            style = L1_STYLE.get(l1, {"color": "green", "hex": "#34D399", "emoji": "🟢", "name": l1, "url": "https://use-waivers"})
            c_color = style["color"]
            c_hex = style["hex"]
            c_emoji = style["emoji"]
            c_name = style["name"]
            c_url = style["url"]
            
            # Render a styled colored left-border header for this family
            st.markdown(f"""
            <div style="border-left: 4px solid {c_hex}; padding-left: 12px; margin-top: 22px; margin-bottom: 12px;">
                <h4 style="color: {c_hex}; margin: 0; font-family: 'Outfit', sans-serif; font-size: 1.1rem; letter-spacing: 0.02em;">
                    {c_emoji} {c_name.upper()} CATEGORY FAMILY
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            daddy_list = [k for k in TREE_DATA[l1].keys() if k != "image_file"]
            
            def format_l2_widget(option):
                has_l3 = bool(TREE_DATA.get(l1, {}).get(option))
                if has_l3:
                    return make_unicode_bold(option)
                return option
                
            l2_label = f"[{c_emoji}]({c_url}) :{c_color}[Select Level 2 Categories under {c_name} *]"
            add_l2_list = st.multiselect(l2_label, daddy_list, key=f"add_l2_{l1}", format_func=format_l2_widget)
            
            if add_l2_list:
                for l2 in add_l2_list:
                    son_list = TREE_DATA[l1][l2]
                    if son_list:
                        l3_label = f"[{c_emoji}]({c_url}) :{c_color}[Select Level 3 Subcategories for {l2}]"
                        l3_selected = st.multiselect(l3_label, son_list, key=f"add_l3_{l1}_{l2}")
                        selected_classifications[(l1, l2)] = l3_selected
                    else:
                        selected_classifications[(l1, l2)] = []

    st.markdown("<br>", unsafe_allow_html=True)
    add_link = st.text_input("Approval Pack / NOC URL", placeholder="e.g., https://zap.planning.nyc.gov/...", key="add_link")
    add_remarks = st.text_area("Remarks", placeholder="Add context, waivers granted, or other notes...", key="add_remarks")
    
    if st.button("Submit For Admin Review & Approval", type="primary", use_container_width=True):
        if not add_name or not add_id or not add_l1_list or not selected_classifications:
            st.error("Please fill in all required fields (Name, ID, and at least one Category path).")
        else:
            # We split the multiple L1 and L2 selections into separate review queue entries!
            count_subm = 0
            for (l1, l2), l3s in selected_classifications.items():
                l3_vals = ["", "", "", ""]
                for idx, val in enumerate(l3s[:4]):
                    l3_vals[idx] = val
                    
                new_row = {
                    'Level1': l1,
                    'Level2': l2,
                    'Level3-1': l3_vals[0],
                    'Level3-2': l3_vals[1],
                    'Level3-3': l3_vals[2],
                    'Level3-4': l3_vals[3],
                    'Project': add_name,
                    'Project ID': add_id,
                    'Cert Year': add_year if add_year else str(date.today().year),
                    'Approval Pack/NOC': add_link,
                    'Project Desc.': add_desc,
                    'ZR Section': add_zr,
                    'Sample Categories': add_sample,
                    'Remarks': add_remarks,
                    'Status': 'Pending'
                }
                save_row('review_queue.csv', new_row)
                count_subm += 1
                
            st.success(f"Successfully submitted '{add_name}' with {count_subm} category paths for Admin Review & Approval!")
            st.rerun()


# TAB 3: EDIT / DELETE EXISTING PROJECTS
with admin_tabs[2]:
    st.markdown("### ✏️ Edit / Delete Existing Projects")
    df_live = load_csv_safe('projects.csv')
    if df_live.empty:
        st.info("No projects available to edit.")
    else:
        proj_list = []
        for p_id, gp in df_live.groupby('Project ID'):
            r1 = gp.iloc[0]
            proj_list.append({
                'id': p_id,
                'label': f"{r1['Project']} ({p_id})"
            })
        
        proj_list = sorted(proj_list, key=lambda x: x['label'].lower())
        options_labels = [p['label'] for p in proj_list]
        selected_label = st.selectbox("Select Project to Edit", ["--"] + options_labels, key=f"edit_proj_select_{st.session_state.edit_reset_key}")
        
        if selected_label != "--":
            sel_proj_id = next(p['id'] for p in proj_list if p['label'] == selected_label)
            proj_rows = df_live[df_live['Project ID'] == sel_proj_id]
            
            st.markdown(f"#### Editing: **{proj_rows.iloc[0]['Project']}**")
            
            st.markdown("##### 🌐 Global Project Info")
            edit_desc = st.text_area("Project Description (Project Desc.)", value=proj_rows.iloc[0].get('Project Desc.', ''), key="edit_desc")
            glob_col1, glob_col2 = st.columns(2)
            with glob_col1:
                edit_name = st.text_input("Project Name", value=proj_rows.iloc[0]['Project'], key="edit_name")
                edit_year = st.text_input("Cert Year", value=proj_rows.iloc[0].get('Cert Year', proj_rows.iloc[0].get('Cert Date', '')), key="edit_year")
                edit_zr = st.text_input("ZR Section", value=proj_rows.iloc[0].get('ZR Section', proj_rows.iloc[0].get('ZR Sections', '')), key="edit_zr")
            with glob_col2:
                edit_link = st.text_input("Approval Pack / NOC URL", value=proj_rows.iloc[0].get('Approval Pack/NOC', ''), key="edit_link")
                edit_sample = st.text_input("Sample Categories", value=proj_rows.iloc[0].get('Sample Categories', ''), key="edit_sample")
                
            st.markdown("##### 🌳 Classification Paths (Rows)")
            st.info("A project can have multiple classification paths. You can edit each path individually below.")
            
            updated_rows = []
            
            for idx, (real_index, row) in enumerate(proj_rows.iterrows()):
                with st.expander(f"Path #{idx + 1}: {row['Level1']} > {row['Level2']}", expanded=True):
                    path_col1, path_col2 = st.columns(2)
                    with path_col1:
                        row_l1 = st.selectbox(f"Level 1 Category", list(TREE_DATA.keys()), index=list(TREE_DATA.keys()).index(row['Level1']) if row['Level1'] in TREE_DATA else 0, key=f"row_l1_{real_index}", format_func=format_l1)
                    with path_col2:
                        daddy_list = [k for k in TREE_DATA[row_l1].keys() if k != "image_file"]
                        
                        def format_l2_edit(option):
                            has_l3 = bool(TREE_DATA.get(row_l1, {}).get(option))
                            if has_l3:
                                return make_unicode_bold(option)
                            return option
                            
                        row_l2 = st.selectbox(
                            f"Level 2 Category", 
                            daddy_list, 
                            index=daddy_list.index(row['Level2']) if row['Level2'] in daddy_list else 0, 
                            key=f"row_l2_{real_index}",
                            format_func=format_l2_edit
                        )
                    
                    son_list = TREE_DATA[row_l1][row_l2]
                    current_l3s = [str(row[c]).strip() for c in ['Level3-1', 'Level3-2', 'Level3-3', 'Level3-4'] if str(row[c]).strip() and str(row[c]).lower() not in ["", "nan", "--"]]
                    
                    if son_list:
                        selected_l3 = st.multiselect(f"Level 3 Subcategories", son_list, default=[c for c in current_l3s if c in son_list], key=f"row_l3_{real_index}")
                    else:
                        selected_l3 = []
                        st.text("No Level 3 subcategories.")
                        
                    row_remarks = st.text_area(f"Remarks", value=row.get('Remarks', ''), key=f"row_rem_{real_index}")
                    
                    if st.button("🗑️ Delete This Path", key=f"del_path_{real_index}", type="secondary"):
                        df_new_live = df_live.drop(real_index)
                        df_new_live.to_csv('projects.csv', index=False, encoding='utf-8-sig')
                        st.success("Path deleted!")
                        st.rerun()
                        
                    l3_vals = ["", "", "", ""]
                    for l_idx, val in enumerate(selected_l3[:4]):
                        l3_vals[l_idx] = val
                    
                    updated_rows.append({
                        'index': real_index,
                        'data': {
                            'Level1': row_l1,
                            'Level2': row_l2,
                            'Level3-1': l3_vals[0],
                            'Level3-2': l3_vals[1],
                            'Level3-3': l3_vals[2],
                            'Level3-4': l3_vals[3],
                            'Project': edit_name,
                            'Project ID': sel_proj_id,
                            'Cert Year': edit_year,
                            'Approval Pack/NOC': edit_link,
                            'Project Desc.': edit_desc,
                            'ZR Sections': edit_zr,
                            'Sample Categories': edit_sample,
                            'Remarks': row_remarks
                        }
                    })
            
            st.divider()
            act_col1, act_col2, act_col3 = st.columns(3)
            with act_col1:
                if st.button("💾 SAVE ALL CHANGES", type="primary", use_container_width=True):
                    for item in updated_rows:
                        idx_to_update = item['index']
                        data_to_set = item['data']
                        for col, val in data_to_set.items():
                            df_live.at[idx_to_update, col] = val
                            
                    # Clean up df_live column names to match the exact schema
                    cols_to_save = [
                        'Project', 'Project ID', 'Approval Pack/NOC', 'Project Desc.', 
                        'ZR Sections', 'Sample Categories', 'Remarks', 'Cert Year', 
                        'Level1', 'Level2', 'Level3-1', 'Level3-2', 'Level3-3', 'Level3-4'
                    ]
                    # Ensure df_live columns have these, or fill with empty
                    for col in cols_to_save:
                        if col not in df_live.columns:
                            df_live[col] = ""
                    df_live_save = df_live[cols_to_save]
                    df_live_save.to_csv('projects.csv', index=False, encoding='utf-8-sig')
                    st.success("Successfully updated project in database!")
                    st.session_state.edit_reset_key += 1
                    st.rerun()
            with act_col2:
                if st.button("➕ ADD NEW PATH TO PROJECT", use_container_width=True):
                    new_row = {
                        'Level1': list(TREE_DATA.keys())[0],
                        'Level2': '--',
                        'Level3-1': '', 'Level3-2': '', 'Level3-3': '', 'Level3-4': '',
                        'Project': edit_name,
                        'Project ID': sel_proj_id,
                        'Cert Year': edit_year,
                        'Approval Pack/NOC': edit_link,
                        'Project Desc.': edit_desc,
                        'ZR Sections': edit_zr,
                        'Sample Categories': edit_sample,
                        'Remarks': ''
                    }
                    save_row('projects.csv', new_row)
                    st.success("New classification path added! Scroll down to edit it.")
                    st.rerun()
            with act_col3:
                if st.button("🚨 DELETE ENTIRE PROJECT", type="primary", use_container_width=True):
                    df_new_live = df_live[df_live['Project ID'] != sel_proj_id]
                    df_new_live.to_csv('projects.csv', index=False)
                    st.warning(f"Deleted project {edit_name} and all its classification paths.")
                    st.session_state.edit_reset_key += 1
                    st.rerun()

# TAB 4: BACKUPS & CSV OPERATIONS
with admin_tabs[3]:
    st.markdown("### 💾 Database Backup & Import Tools")
    
    st.markdown("#### 📤 Export Database")
    st.write("Download the current database tables as CSV files for local backup or editing.")
    
    df_dl_projects = load_csv_safe('projects.csv')
    df_dl_queue = load_csv_safe('review_queue.csv')
    
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        if not df_dl_projects.empty:
            csv_proj = df_dl_projects.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Download projects.csv",
                data=csv_proj,
                file_name="projects.csv",
                mime="text/csv",
                use_container_width=True
            )
    with dl_col2:
        if not df_dl_queue.empty:
            csv_q = df_dl_queue.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Download review_queue.csv",
                data=csv_q,
                file_name="review_queue.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    st.divider()
    st.markdown("#### 📥 Import Database")
    st.write("Overwrite the current database by uploading a CSV file. WARNING: This will replace your active database!")
    
    upload_file = st.file_uploader("Upload projects.csv replacement", type=["csv"])
    if upload_file is not None:
        try:
            try:
                uploaded_df = pd.read_csv(upload_file, encoding='utf-8-sig', encoding_errors='replace', dtype=str)
            except Exception:
                try:
                    uploaded_df = pd.read_csv(upload_file, encoding='cp1252', encoding_errors='replace', dtype=str)
                except Exception:
                    try:
                        uploaded_df = pd.read_csv(upload_file, encoding='latin1', dtype=str)
                    except Exception:
                        uploaded_df = pd.DataFrame()
            
            uploaded_df.columns = [str(c).strip() for c in uploaded_df.columns]
            if not uploaded_df.empty and 'Project ID' not in uploaded_df.columns:
                if 'Project' in uploaded_df.iloc[0].values and 'Project ID' in uploaded_df.iloc[0].values:
                    uploaded_df.columns = [str(c).strip() for c in uploaded_df.iloc[0]]
                    uploaded_df = uploaded_df[1:].reset_index(drop=True)
            
            st.write("Preview of uploaded database:")
            st.dataframe(uploaded_df.head(5), use_container_width=True)
            
            if st.button("⚠️ CONFIRM & OVERWRITE LIVE DATABASE", type="primary", use_container_width=True):
                uploaded_df.to_csv('projects.csv', index=False, encoding='utf-8-sig')
                st.success("Live database successfully updated!")
                st.rerun()
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
