"""
Universal SRT database loader - works with both JSON and pickle formats
Drop this into your Streamlit app directory
"""
import json
import pickle
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

def load_srt_database() -> Tuple[pd.DataFrame, Dict]:
    """
    Load SRT database from JSON or pickle format.
    Returns: (dataframe, model_lookup_dict)
    """
    
    # Try JSON first (preferred)
    json_file = Path('srt_database_organized.json')
    if json_file.exists():
        print("Loading from JSON...")
        with open(json_file, 'r') as f:
            srt_data = json.load(f)
        
        # Convert to DataFrame
        all_codes = []
        model_lookup = {}
        
        for model_key, codes in srt_data.items():
            # Parse the model key
            parts = model_key.split('_')
            equipment_type = parts[0].replace('_', ' ').title()
            model_name = '_'.join(parts[1:]) if len(parts) > 1 else parts[0]
            
            # Add to model lookup
            model_lookup[model_key] = {
                'display_name': f"{equipment_type} {model_name}",
                'equipment_type': equipment_type,
                'model_name': model_name,
                'num_codes': len(codes)
            }
            
            # Add all codes to flat list
            for code in codes:
                all_codes.append({
                    'model_key': model_key,
                    'equipment_type': equipment_type,
                    'model_name': model_name,
                    'code': code['code'],
                    'description': code['description'],
                    'hours': float(code['hours'])
                })
        
        df = pd.DataFrame(all_codes)
        print(f"✓ Loaded {len(model_lookup)} models with {len(all_codes)} SRT codes")
        return df, model_lookup
    
    # Fall back to pickle
    pkl_file = Path('srt_database.pkl')
    if pkl_file.exists():
        print("Loading from pickle...")
        df = pd.read_pickle(pkl_file)
        
        # Try to load model lookup
        lookup_file = Path('model_lookup.pkl')
        if lookup_file.exists():
            with open(lookup_file, 'rb') as f:
                model_lookup = pickle.load(f)
        else:
            # Generate from DataFrame
            model_lookup = {}
            for model_key in df['model_key'].unique():
                model_data = df[df['model_key'] == model_key].iloc[0]
                model_lookup[model_key] = {
                    'display_name': f"{model_data['equipment_type']} {model_data['model_name']}",
                    'equipment_type': model_data['equipment_type'],
                    'model_name': model_data['model_name'],
                    'num_codes': len(df[df['model_key'] == model_key])
                }
        
        print(f"✓ Loaded {len(model_lookup)} models with {len(df)} SRT codes")
        return df, model_lookup
    
    # No database found
    raise FileNotFoundError(
        "No database found! Please add 'srt_database_organized.json' to your repo.\n"
        "Or run convert_json_to_pickle.py if you have the JSON file."
    )

def get_models_by_type(model_lookup: Dict) -> Dict[str, List[str]]:
    """Group models by equipment type"""
    by_type = {}
    for model_key, info in model_lookup.items():
        eq_type = info['equipment_type']
        if eq_type not in by_type:
            by_type[eq_type] = []
        by_type[eq_type].append(model_key)
    return by_type

def search_srt_codes(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Search SRT codes by description"""
    query_lower = query.lower()
    mask = df['description'].str.lower().str.contains(query_lower, na=False)
    return df[mask]

def get_model_codes(df: pd.DataFrame, model_key: str) -> pd.DataFrame:
    """Get all SRT codes for a specific model"""
    return df[df['model_key'] == model_key].copy()


# Example usage in Streamlit:
if __name__ == "__main__":
    # Load database
    df, models = load_srt_database()
    
    # Show summary
    print("\nEquipment types:")
    by_type = get_models_by_type(models)
    for eq_type, model_keys in sorted(by_type.items()):
        print(f"  {eq_type}: {len(model_keys)} models")
    
    # Search example
    print("\nEngine-related codes:")
    engine_codes = search_srt_codes(df, "engine")
    print(f"  Found {len(engine_codes)} codes")
    print(engine_codes[['model_name', 'code', 'description', 'hours']].head(3))
