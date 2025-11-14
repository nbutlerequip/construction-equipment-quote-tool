# streamlit_quote_tool_pro.py
# Professional Construction Equipment Service Quote Tool
# Multi-Manufacturer Support with Advanced Difficulty Matrix

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import io
from load_srt_database import load_srt_database, get_models_by_type

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
    """Load SRT database using the new loader"""
    try:
        df, models = load_srt_database()
        
        # Convert back to the old format for compatibility
        # (grouped by model_key with list of codes)
        database = {}
        for model_key in df['model_key'].unique():
            model_data = df[df['model_key'] == model_key]
            database[model_key] = [
                {
                    'code': row['code'],
                    'description': row['description'],
                    'hours': row['hours']
                }
                for _, row in model_data.iterrows()
            ]
        
        return database, models, df
    except FileNotFoundError as e:
        st.error(f"❌ {str(e)}")
        st.error("Please make sure 'srt_database_organized.json' and 'load_srt_database.py' are in your repository.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading database: {e}")
        st.stop()

# Load database
database, model_metadata, df_all = load_database()

# Success message
st.success(f"✅ Loaded {len(database)} models with {len(df_all):,} SRT codes")

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
    <p>Professional Construction Equipment Service Quote Tool</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - EQUIPMENT & MODEL SELECTION
# ============================================================================

with st.sidebar:
    st.markdown("## 🚜 Equipment Selection")
    
    # Manufacturer selection
    manufacturer = st.selectbox(
        "Manufacturer",
        options=MANUFACTURERS,
        help="Select equipment manufacturer"
    )
    
    # If CNH selected, show model selector with organized groups
    if manufacturer == "CNH (Case/New Holland)":
        st.markdown("### CNH Models Available")
        
        # Group models by equipment type
        models_by_type = get_models_by_type(model_metadata)
        
        # Equipment type selector
        equipment_types = sorted(models_by_type.keys())
        selected_type = st.selectbox(
            "Equipment Type",
            options=equipment_types,
            help="Filter by equipment category"
        )
        
        # Model selector (filtered by type)
        available_models = models_by_type[selected_type]
        model_display_names = [model_metadata[mk]['display_name'] for mk in available_models]
        
        selected_display = st.selectbox(
            "Model",
            options=model_display_names,
            help="Select specific equipment model"
        )
        
        # Get the actual model key
        selected_model_key = available_models[model_display_names.index(selected_display)]
        
        # Show model info
        st.info(f"📊 {len(database[selected_model_key])} operations available")
        
        # Get operations for selected model
        available_operations = database[selected_model_key]
        
        # Search/filter operations
        st.markdown("---")
        st.markdown("### 🔍 Find Operations")
        
        search_term = st.text_input(
            "Search operations",
            placeholder="e.g., engine, hydraulic, replace...",
            help="Filter by description or code"
        )
        
        # Filter operations based on search
        if search_term:
            filtered_ops = [
                op for op in available_operations
                if search_term.lower() in op['description'].lower() or 
                   search_term.lower() in op['code'].lower()
            ]
        else:
            filtered_ops = available_operations
        
        st.caption(f"Showing {len(filtered_ops)} of {len(available_operations)} operations")
        
        # Display operations and add to quote
        st.markdown("---")
        st.markdown("### ➕ Add to Quote")
        
        if filtered_ops:
            # Show operations in a scrollable container
            for op in filtered_ops[:20]:  # Limit to first 20 for performance
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="operation-card">
                            <span class="operation-code">{op['code']}</span><br/>
                            <small>{op['description'][:80]}...</small><br/>
                            <strong>{op['hours']:.1f} hours</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("Add", key=f"add_{op['code']}", use_container_width=True):
                            # Add to quote
                            quote_item = {
                                'code': op['code'],
                                'description': op['description'],
                                'hours': op['hours'],
                                'model': selected_display
                            }
                            
                            # Check if already added
                            if not any(item['code'] == op['code'] for item in st.session_state.quote_items):
                                st.session_state.quote_items.append(quote_item)
                                st.success(f"Added {op['code']}")
                                st.rerun()
                            else:
                                st.warning("Already in quote")
            
            if len(filtered_ops) > 20:
                st.info(f"Showing first 20 of {len(filtered_ops)} operations. Use search to find specific operations.")
        else:
            st.warning("No operations found. Try a different search term.")
    
    else:
        # For non-CNH manufacturers
        st.info(f"ℹ️ Manual entry mode for {manufacturer}")
        st.markdown("### ✍️ Manual Operation Entry")
        
        with st.form("manual_entry"):
            manual_code = st.text_input("Operation Code", placeholder="e.g., 10.001.AD.10")
            manual_desc = st.text_area("Description", placeholder="Describe the service operation...")
            manual_hours = st.number_input("Labor Hours", min_value=0.0, value=1.0, step=0.5)
            
            if st.form_submit_button("Add to Quote"):
                if manual_code and manual_desc:
                    quote_item = {
                        'code': manual_code,
                        'description': manual_desc,
                        'hours': manual_hours,
                        'model': f"{manufacturer} (Manual Entry)"
                    }
                    st.session_state.quote_items.append(quote_item)
                    st.success("Added to quote!")
                    st.rerun()
                else:
                    st.error("Please fill in all fields")

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

# Create tabs
tab1, tab2, tab3 = st.tabs(["📝 Quote Builder", "⚙️ Difficulty Factors", "📄 Review & Export"])

# TAB 1: QUOTE BUILDER
with tab1:
    st.markdown("### 🛠️ Current Quote")
    
    if not st.session_state.quote_items:
        st.info("👈 Select operations from the sidebar to build your quote")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display quote items
        if st.session_state.quote_items:
            for idx, item in enumerate(st.session_state.quote_items):
                with st.container():
                    col_a, col_b = st.columns([4, 1])
                    
                    with col_a:
                        st.markdown(f"""
                        **{item['code']}** - {item['hours']:.1f} hrs  
                        {item['description']}  
                        <small>Model: {item['model']}</small>
                        """, unsafe_allow_html=True)
                    
                    with col_b:
                        if st.button("🗑️", key=f"remove_{idx}", help="Remove"):
                            st.session_state.quote_items.pop(idx)
                            st.rerun()
                
                st.markdown("---")
    
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
