# streamlit_quote_tool_pro.py
# Professional Construction Equipment Service Quote Tool
# Multi-Manufacturer Support with Advanced Difficulty Matrix

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import io

# ============================================================================
# CONFIGURATION
# ============================================================================

# Company Settings
COMPANY_NAME = "Southeastern Equipment"
COMPANY_COLORS = {
    'primary': '#c41e3a',      # Red
    'secondary': '#0d47a1',    # Blue
    'accent': '#2e7d32',       # Green
    'background': '#f5f5f5'
}

# Default Settings
DEFAULT_LABOR_RATE = 125.00
CURRENCY_SYMBOL = "$"

# Supported Manufacturers
MANUFACTURERS = [
    "CNH (Case/New Holland)",
    "Caterpillar",
    "John Deere", 
    "Komatsu",
    "Volvo",
    "Hitachi",
    "Liebherr",
    "JCB",
    "Doosan",
    "Kubota",
    "Other"
]

# Enhanced Difficulty Matrix
DIFFICULTY_FACTORS = {
    'age': {
        "0-2 years (New)": 1.0,
        "3-5 years (Like New)": 1.05,
        "6-8 years (Good)": 1.15,
        "9-12 years (Average)": 1.25,
        "13-15 years (Older)": 1.35,
        "16-20 years (Old)": 1.50,
        "20+ years (Very Old)": 1.75
    },
    'condition': {
        "Excellent - Well maintained": 1.0,
        "Good - Normal wear": 1.10,
        "Fair - Some issues": 1.25,
        "Poor - Multiple problems": 1.40,
        "Severe - Major overhaul needed": 1.60
    },
    'location': {
        "Shop - Full facilities": 1.0,
        "On-site - Accessible": 1.15,
        "On-site - Limited access": 1.30,
        "Remote - Difficult terrain": 1.50,
        "Remote - Extreme conditions": 1.75
    },
    'manufacturer': {
        "CNH (Case/New Holland)": 1.0,  # Your specialty
        "Caterpillar": 1.05,
        "John Deere": 1.05,
        "Komatsu": 1.10,
        "Volvo": 1.10,
        "Hitachi": 1.15,
        "Liebherr": 1.15,
        "JCB": 1.08,
        "Doosan": 1.12,
        "Kubota": 1.05,
        "Other": 1.20
    },
    'urgency': {
        "Standard - Normal schedule": 1.0,
        "Priority - Within 3 days": 1.20,
        "Rush - Next day": 1.50,
        "Emergency - Same day": 2.00
    },
    'complexity': {
        "Routine - Standard service": 1.0,
        "Moderate - Some diagnosis needed": 1.15,
        "Complex - Extensive troubleshooting": 1.30,
        "Severe - Complete tear-down": 1.50
    }
}

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=f"{COMPANY_NAME} - Service Quote Tool",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown(f"""
<style>
    /* Main styling */
    .main {{
        background-color: {COMPANY_COLORS['background']};
    }}
    
    /* Header styling */
    .header {{
        background: linear-gradient(135deg, {COMPANY_COLORS['primary']} 0%, {COMPANY_COLORS['secondary']} 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    .header h1 {{
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }}
    
    .header p {{
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }}
    
    /* Card styling */
    .card {{
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }}
    
    /* Metrics styling */
    .metric-card {{
        background: linear-gradient(135deg, {COMPANY_COLORS['accent']} 0%, {COMPANY_COLORS['secondary']} 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0;
    }}
    
    /* Button styling */
    .stButton > button {{
        background-color: {COMPANY_COLORS['primary']};
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s;
    }}
    
    .stButton > button:hover {{
        background-color: {COMPANY_COLORS['secondary']};
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }}
    
    /* Operation card */
    .operation-card {{
        background: white;
        border-left: 4px solid {COMPANY_COLORS['primary']};
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    .operation-code {{
        color: {COMPANY_COLORS['secondary']};
        font-weight: bold;
        font-family: monospace;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem;
        color: #666;
        margin-top: 3rem;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATABASE
# ============================================================================

@st.cache_data
def load_database():
    """Load SRT database from JSON file"""
    try:
        db_path = Path("srt_database.json")
        if not db_path.exists():
            st.error("❌ Database file not found. Please run convert_csv.py first.")
            st.stop()
        
        with open(db_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        return database
    except Exception as e:
        st.error(f"❌ Error loading database: {e}")
        st.stop()

database = load_database()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'quote_items' not in st.session_state:
    st.session_state.quote_items = []

if 'difficulty_factors' not in st.session_state:
    st.session_state.difficulty_factors = {
        'age': 1.0,
        'condition': 1.0,
        'location': 1.0,
        'manufacturer': 1.0,
        'urgency': 1.0,
        'complexity': 1.0
    }

# ============================================================================
# HEADER
# ============================================================================

st.markdown(f"""
<div class="header">
    <h1>🔧 {COMPANY_NAME}</h1>
    <p>Professional Service Quote Tool - Construction Equipment</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - OPERATION SEARCH
# ============================================================================

with st.sidebar:
    st.markdown("### 🔍 Search Operations")
    
    # Equipment selection
    st.markdown("#### Equipment Information")
    
    manufacturer = st.selectbox(
        "Manufacturer",
        options=MANUFACTURERS,
        index=0,
        help="Select equipment manufacturer"
    )
    
    # Get available models
    available_models = ["All Models"] + sorted(database.keys())
    
    selected_model = st.selectbox(
        "Model",
        options=available_models,
        help="Select specific equipment model or 'All Models' to search across all"
    )
    
    st.markdown("---")
    
    # Search box
    search_query = st.text_input(
        "🔎 Search SRT Operations",
        placeholder="e.g., engine oil, hydraulic, transmission",
        help="Enter keywords to search operation codes and descriptions"
    )
    
    # Search results
    if search_query:
        st.markdown(f"#### Search Results for '{search_query}'")
        
        results = []
        search_lower = search_query.lower()
        
        # Search in selected model or all models
        if selected_model == "All Models":
            search_models = database.keys()
        else:
            search_models = [selected_model]
        
        for model in search_models:
            for op in database[model]:
                code_match = search_lower in op['code'].lower()
                desc_match = search_lower in op['description'].lower()
                
                if code_match or desc_match:
                    results.append({
                        'model': model,
                        'code': op['code'],
                        'description': op['description'],
                        'hours': op['hours']
                    })
        
        if results:
            st.success(f"✓ Found {len(results)} operations")
            
            # Display results
            for i, result in enumerate(results[:10]):  # Show top 10
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{result['code']}**")
                        st.caption(f"{result['description'][:80]}{'...' if len(result['description']) > 80 else ''}")
                        st.caption(f"📦 Model: {result['model']}")
                    
                    with col2:
                        st.metric("Hours", f"{result['hours']:.1f}")
                        if st.button("Add", key=f"add_{i}"):
                            st.session_state.quote_items.append(result)
                            st.success("Added!")
                            st.rerun()
                    
                    st.markdown("---")
            
            if len(results) > 10:
                st.info(f"Showing 10 of {len(results)} results. Refine search to see more.")
        else:
            st.warning(f"No results found for '{search_query}'")
    else:
        st.info("👆 Enter search terms above to find operations")
    
    # Quick stats
    st.markdown("---")
    st.markdown("### 📊 Database Stats")
    st.metric("Models Available", len(database))
    st.metric("Total Operations", sum(len(ops) for ops in database.values()))

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Create tabs
tab1, tab2, tab3 = st.tabs(["📝 Quote Builder", "⚙️ Difficulty Factors", "📄 Review & Export"])

# TAB 1: QUOTE BUILDER
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Current Quote Items")
        
        if st.session_state.quote_items:
            for i, item in enumerate(st.session_state.quote_items):
                with st.container():
                    st.markdown(f"""
                    <div class="operation-card">
                        <span class="operation-code">{item['code']}</span> | 
                        <strong>{item['description']}</strong><br>
                        <small>Model: {item['model']} | Base Hours: {item['hours']:.1f}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Remove", key=f"remove_{i}"):
                        st.session_state.quote_items.pop(i)
                        st.rerun()
        else:
            st.info("🔍 Search and add operations from the sidebar to build your quote")
    
    with col2:
        st.markdown("### Quick Summary")
        
        if st.session_state.quote_items:
            base_hours = sum(item['hours'] for item in st.session_state.quote_items)
            
            # Calculate total multiplier
            total_multiplier = 1.0
            for factor_value in st.session_state.difficulty_factors.values():
                total_multiplier *= factor_value
            
            adjusted_hours = base_hours * total_multiplier
            
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{len(st.session_state.quote_items)}</p>
                <p class="metric-label">Operations</p>
            </div>
            <div class="metric-card">
                <p class="metric-value">{base_hours:.1f}</p>
                <p class="metric-label">Base Hours</p>
            </div>
            <div class="metric-card">
                <p class="metric-value">{adjusted_hours:.1f}</p>
                <p class="metric-label">Adjusted Hours</p>
            </div>
            <div class="metric-card">
                <p class="metric-value">{total_multiplier:.2f}x</p>
                <p class="metric-label">Total Multiplier</p>
            </div>
            """, unsafe_allow_html=True)

# TAB 2: DIFFICULTY FACTORS
with tab2:
    st.markdown("### ⚙️ Adjust Difficulty Factors")
    st.markdown("Fine-tune labor estimates based on job-specific conditions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Machine & Job Conditions")
        
        # Age
        age_selection = st.selectbox(
            "Machine Age",
            options=list(DIFFICULTY_FACTORS['age'].keys()),
            help="Older machines typically require more time due to wear, rust, and part accessibility"
        )
        st.session_state.difficulty_factors['age'] = DIFFICULTY_FACTORS['age'][age_selection]
        st.caption(f"Multiplier: {DIFFICULTY_FACTORS['age'][age_selection]:.2f}x")
        
        # Condition
        condition_selection = st.selectbox(
            "Machine Condition",
            options=list(DIFFICULTY_FACTORS['condition'].keys()),
            help="Overall maintenance condition affects repair complexity"
        )
        st.session_state.difficulty_factors['condition'] = DIFFICULTY_FACTORS['condition'][condition_selection]
        st.caption(f"Multiplier: {DIFFICULTY_FACTORS['condition'][condition_selection]:.2f}x")
        
        # Location
        location_selection = st.selectbox(
            "Work Location",
            options=list(DIFFICULTY_FACTORS['location'].keys()),
            help="Job site conditions impact efficiency and tool availability"
        )
        st.session_state.difficulty_factors['location'] = DIFFICULTY_FACTORS['location'][location_selection]
        st.caption(f"Multiplier: {DIFFICULTY_FACTORS['location'][location_selection]:.2f}x")
    
    with col2:
        st.markdown("#### Service Specifications")
        
        # Manufacturer
        mfr_selection = st.selectbox(
            "Equipment Manufacturer",
            options=list(DIFFICULTY_FACTORS['manufacturer'].keys()),
            index=list(DIFFICULTY_FACTORS['manufacturer'].keys()).index(manufacturer.split(" ")[0] if " " in manufacturer else manufacturer) if manufacturer.split(" ")[0] in DIFFICULTY_FACTORS['manufacturer'] else 0,
            help="Familiarity with manufacturer affects efficiency"
        )
        st.session_state.difficulty_factors['manufacturer'] = DIFFICULTY_FACTORS['manufacturer'][mfr_selection]
        st.caption(f"Multiplier: {DIFFICULTY_FACTORS['manufacturer'][mfr_selection]:.2f}x")
        
        # Urgency
        urgency_selection = st.selectbox(
            "Service Urgency",
            options=list(DIFFICULTY_FACTORS['urgency'].keys()),
            help="Rush jobs require premium pricing for scheduling adjustments"
        )
        st.session_state.difficulty_factors['urgency'] = DIFFICULTY_FACTORS['urgency'][urgency_selection]
        st.caption(f"Multiplier: {DIFFICULTY_FACTORS['urgency'][urgency_selection]:.2f}x")
        
        # Complexity
        complexity_selection = st.selectbox(
            "Job Complexity",
            options=list(DIFFICULTY_FACTORS['complexity'].keys()),
            help="Diagnosis and troubleshooting time requirements"
        )
        st.session_state.difficulty_factors['complexity'] = DIFFICULTY_FACTORS['complexity'][complexity_selection]
        st.caption(f"Multiplier: {DIFFICULTY_FACTORS['complexity'][complexity_selection]:.2f}x")
    
    # Summary
    st.markdown("---")
    st.markdown("### 📊 Combined Impact")
    
    total_mult = 1.0
    for factor_value in st.session_state.difficulty_factors.values():
        total_mult *= factor_value
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Base Multiplier", "1.00x")
    with col2:
        st.metric("Total Multiplier", f"{total_mult:.2f}x", 
                 delta=f"+{(total_mult - 1.0) * 100:.0f}%" if total_mult > 1.0 else "Standard")
    with col3:
        if st.session_state.quote_items:
            base = sum(item['hours'] for item in st.session_state.quote_items)
            st.metric("Impact on Current Quote", 
                     f"+{(base * total_mult - base):.1f} hours",
                     delta=f"{base:.1f}h → {base * total_mult:.1f}h")

# TAB 3: REVIEW & EXPORT
with tab3:
    st.markdown("### 📄 Quote Review & Export")
    
    if not st.session_state.quote_items:
        st.warning("⚠️ No operations added yet. Add operations from the sidebar to create a quote.")
    else:
        # Customer Information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Customer Information")
            customer_name = st.text_input("Customer Name", placeholder="ABC Construction Co.")
            customer_contact = st.text_input("Contact Person", placeholder="John Smith")
            customer_phone = st.text_input("Phone", placeholder="(555) 123-4567")
        
        with col2:
            st.markdown("#### Equipment & Pricing")
            equipment_serial = st.text_input("Equipment Serial #", placeholder="ABC123456")
            labor_rate = st.number_input(
                "Labor Rate ($/hour)",
                min_value=0.0,
                value=DEFAULT_LABOR_RATE,
                step=5.0,
                format="%.2f"
            )
            quote_date = st.date_input("Quote Date", value=datetime.now())
        
        # Calculate totals
        base_hours = sum(item['hours'] for item in st.session_state.quote_items)
        total_multiplier = 1.0
        for factor_value in st.session_state.difficulty_factors.values():
            total_multiplier *= factor_value
        adjusted_hours = base_hours * total_multiplier
        total_cost = adjusted_hours * labor_rate
        
        # Quote Summary
        st.markdown("---")
        st.markdown("### 💰 Quote Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Base Hours", f"{base_hours:.1f}")
        with col2:
            st.metric("Difficulty Adj.", f"{total_multiplier:.2f}x")
        with col3:
            st.metric("Final Hours", f"{adjusted_hours:.1f}")
        with col4:
            st.metric("Total Cost", f"{CURRENCY_SYMBOL}{total_cost:,.2f}")
        
        # Detailed breakdown
        st.markdown("---")
        st.markdown("### 📋 Detailed Breakdown")
        
        # Create DataFrame
        quote_data = []
        for item in st.session_state.quote_items:
            adjusted_item_hours = item['hours'] * total_multiplier
            item_cost = adjusted_item_hours * labor_rate
            
            quote_data.append({
                'SRT Code': item['code'],
                'Description': item['description'],
                'Model': item['model'],
                'Base Hours': f"{item['hours']:.1f}",
                'Adj. Hours': f"{adjusted_item_hours:.1f}",
                'Cost': f"{CURRENCY_SYMBOL}{item_cost:,.2f}"
            })
        
        df = pd.DataFrame(quote_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # CSV Export
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"quote_{customer_name.replace(' ', '_')}_{quote_date}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel Export (basic)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Quote', index=False)
            
            st.download_button(
                label="📥 Download Excel",
                data=output.getvalue(),
                file_name=f"quote_{customer_name.replace(' ', '_')}_{quote_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            if st.button("🗑️ Clear Quote", type="secondary"):
                st.session_state.quote_items = []
                st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div class="footer">
    <p>Powered by Streamlit | © 2025 Southeastern Equipment</p>
    <p><small>Professional Service Quote Tool v2.0 | Multi-Manufacturer Support</small></p>
</div>
""", unsafe_allow_html=True)
