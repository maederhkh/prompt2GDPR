import os
import re
import json
from pathlib import Path
import sys
import difflib

# Force UTF-8 encoding for console output (fixes emoji crash on Windows)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8') # type: ignore

# ========== DEPENDENCY CHECK ==========
try:
    import pandas as pd
    import openpyxl
except ImportError as e:
    print("\n❌ CRITICAL ERROR: Missing required libraries!")
    print(f"   Error details: {e}")
    print("   Please run this command in your terminal to fix it:")
    print("   pip install pandas openpyxl")
    print("\n   The script will now exit.\n")
    sys.exit(1)

# ========== CONFIGURATION ==========
# ========== CONFIGURATION ==========
OFFICIAL_ARTICLE5 = {
    "1": "Personal data shall be processed lawfully, fairly and in a transparent manner in relation to the data subject (‘lawfulness, fairness and transparency’)",
    "2": "Personal data shall be collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible with those purposes; further processing for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes shall, in accordance with Article 89(1), not be considered to be incompatible with the initial purposes (‘purpose limitation’)",
    "3": "Personal data shall be adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed (‘data minimisation’)",
    "4": "Personal data shall be accurate and, where necessary, kept up to date; every reasonable step must be taken to ensure that personal data that are inaccurate, having regard to the purposes for which they are processed, are erased or rectified without delay (‘accuracy’)",
    "5": "Personal data shall be kept in a form which permits identification of data subjects for no longer than is necessary for the purposes for which the personal data are processed; personal data may be stored for longer periods insofar as the personal data will be processed solely for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes in accordance with Article 89(1) subject to implementation of the appropriate technical and organisational measures required by this Regulation in order to safeguard the rights and freedoms of the data subject (‘storage limitation’)",
    "6": "Personal data shall be processed in a manner that ensures appropriate security of the personal data, including protection against unauthorised or unlawful processing and against accidental loss, destruction or damage, using appropriate technical or organisational measures (‘integrity and confidentiality’)",
    "7": "The controller shall be responsible for, and be able to demonstrate compliance with, paragraph 1 (‘accountability’)"
}

# Mapping string names to internal IDs (Case Insensitive)
PRINCIPLE_NAME_TO_ID = {
    "lawfulness, fairness and transparency": "1",
    "lawfulness": "1",
    "purpose limitation": "2",
    "data minimisation": "3",
    "data minimization": "3", # handle US spelling
    "accuracy": "4",
    "storage limitation": "5",
    "integrity and confidentiality": "6",
    "integrity": "6",
    "accountability": "7"
}

REQUIRED_PRINCIPLES = [
    "Lawfulness, fairness and transparency",
    "Purpose limitation", 
    "Data minimisation",
    "Accuracy",
    "Storage limitation",
    "Integrity and confidentiality",
    "Accountability"
]

# ========== FILE PARSING FUNCTIONS ==========
def parse_filename(filepath):
    """Extract strategy, version, model, variant from filepath"""
    path = Path(filepath)
    name = path.stem.lower()
    parts = [p.lower() for p in path.parts]
    
    # Strategy
    if "zero_shot" in parts: strategy = "Zero-Shot"
    elif "few_shot" in parts: strategy = "Few-Shot"
    elif "zero" in name: strategy = "Zero-Shot"
    elif "few" in name: strategy = "Few-Shot"
    else: strategy = "Other"
    
    # Version
    version = "Unknown"
    if "1st" in name: version = "1st"
    elif "2nd" in name: version = "2nd"
    elif "3rd" in name: version = "3rd"
    
    # Model
    if "grok" in parts: model = "Grok"
    elif "gpt5.2" in parts: model = "GPT-5.2"
    elif "grok" in name: model = "Grok"
    elif "gpt5" in name or "gpt-5" in name: model = "GPT-5"
    else: model = "Unknown"

    # Variant
    variant = "Base"
    if "expert" in name: variant = "Expert"
    elif "extended_thinking" in name: variant = "Extended Thinking"
    
    return {
        "Filename": path.name,
        "Strategy": strategy,
        "Version": version, 
        "Model": model,
        "Variant": variant
    }

def normalize_text(text):
    """Normalize text for comparison"""
    text = str(text).lower()
    # Remove punctuation and extra whitespace
    text = re.sub(r'[^\w\s]', '', text)
    return " ".join(text.split())

def check_official_text(text, principle_id):
    """Check text against official snippet using fuzzy matching"""
    if not text or principle_id not in OFFICIAL_ARTICLE5:
        return "❌ Missing/Unknown"
    
    target = normalize_text(OFFICIAL_ARTICLE5[principle_id])
    source = normalize_text(text)
    
    # Calculate similarity ratio
    matcher = difflib.SequenceMatcher(None, target, source)
    ratio = matcher.ratio()
    
    # If the source is a substring of target (or vice-versa), ratio might be low if lengths differ greatly.
    # So we also check inclusion for very high overlap.
    if target in source or source in target:
         if len(source) > 20: # Ensure it's not just "The"
             return "✅ Correct (Substring)"
    
    if ratio > 0.8: # 80% similarity threshold
        return f"✅ Correct ({int(ratio*100)}%)"
    elif ratio > 0.5:
        return f"⚠️ Partial Match ({int(ratio*100)}%)"
    
    return f"❌ Low Match ({int(ratio*100)}%)"

def get_principle_id(name):
    """Fuzzy match principle name to ID"""
    name_clean = normalize_text(name).replace(".", "").replace("1 ", "").replace("2 ", "").strip()
    
    for key, pid in PRINCIPLE_NAME_TO_ID.items():
        if key in name_clean:
            return pid
    return "0"

def load_json_with_fallback(file_path):
    """Attempt to load JSON with multiple repair strategies"""
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # Strategy 1: Standard Load
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Targeted Regex Replace (Fix curly delimiters only)
    # Replaces : “ with : "  AND  ”, with ",  AND  ”} with "}
    try:
        regex_fixed = re.sub(r'":\s*“', '": "', raw_text)
        regex_fixed = re.sub(r'”\s*,', '",', regex_fixed)
        regex_fixed = re.sub(r'”\s*}', '"}', regex_fixed)
        return json.loads(regex_fixed)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Global Char Replace (Risky - might create unescaped quotes)
    try:
        global_fixed = raw_text.replace('“', '"').replace('”', '"')
        return json.loads(global_fixed)
    except json.JSONDecodeError:
        pass
        
    # Strategy 4: Robust Substring Extraction (Iterative Truncation)
    # Handles cases where valid JSON is followed by text/references (e.g. [1]: ...)
    # Logic: Find start, then try closing at every possible ']' or '}' from the end backwards
    try:
        match_start = re.search(r'[\[\{]', raw_text)
        if match_start:
            start_idx = match_start.start()
            
            # Find all closing brackets after start
            candidates = [m.start() for m in re.finditer(r'[\]\}]', raw_text) if m.start() > start_idx]
            
            # Try from the end (longest possible JSON)
            for end_idx in reversed(candidates):
                substr = raw_text[start_idx : end_idx + 1] # type: ignore
                
                # Attempt 1: Parse exactly as extracted (Best for files with valid internal curly quotes)
                try:
                    return json.loads(substr)
                except json.JSONDecodeError:
                    pass
                
                # Attempt 2: Apply quote fix (Only if needed for files using them as delimiters)
                if '“' in substr:
                    substr_fixed = substr.replace('“', '"').replace('”', '"')
                    try:
                        return json.loads(substr_fixed)
                    except json.JSONDecodeError:
                        pass
    except Exception:
        pass

    print(f"❌ Failed to parse JSON in {file_path.name} after multiple attempts.")
    return None

def analyze_json_file(file_path):
    """Deep analysis of a single JSON file"""
    raw_data = load_json_with_fallback(file_path)
    if raw_data is None:
        return []

    metadata = parse_filename(file_path)
    rows = []
    
    # Handle different JSON structures
    data_list = []
    if isinstance(raw_data, list):
        data_list = raw_data
    elif isinstance(raw_data, dict):
        if "analysis" in raw_data and isinstance(raw_data["analysis"], list):
            data_list = raw_data["analysis"]
        else:
            # Fallback for weird structures - try to find any list
            for key, val in raw_data.items():
                if isinstance(val, list):
                    data_list = val
                    break
    
    if not data_list:
        print(f"⚠️  Skipping {file_path.name}: Could not find list of principles.")
        return []

    found_ids = set()

    for item in data_list:
        # Normalize keys just in case (e.g. "Principle" vs "principle")
        item_lower = {k.lower(): v for k, v in item.items()}
        
        p_name = item_lower.get("principle", "Unknown")
        p_id = get_principle_id(p_name)
        found_ids.add(p_id)
        
        # Extract fields with fallbacks
        rating = item_lower.get("rating", "N/A")
        justification = item_lower.get("justification", "")
        article5_text = item_lower.get("article_5_text", item_lower.get("article5_text", ""))
        recital39 = item_lower.get("recital_39_reference", item_lower.get("recital39_reference", ""))
        
        # Clause handling
        clauses = item_lower.get("relevant_clauses", item_lower.get("policy_clauses", []))
        num_sections = len(clauses) if isinstance(clauses, list) else 0
        section_names = ""
        if isinstance(clauses, list):
            names = [c.get("section", "N/A") for c in clauses if isinstance(c, dict)]
            section_names = ", ".join(names)

        # Structure Check
        required_keys = ["principle", "rating"]
        missing_keys = [k for k in required_keys if k not in item_lower]
        structure_status = "✅ OK" if not missing_keys else f"❌ Missing: {missing_keys}"

        # Build Row
        row = metadata.copy()
        row.update({
            "Principle_Name": p_name,
            "Principle_ID": p_id,
            "Rating": rating,
            "Num_Sections": num_sections,
            "Section_List": str(section_names)[:500], # Limit length for Excel # type: ignore
            "Structure_Status": structure_status,
            "Official_Text_Status": check_official_text(article5_text, p_id),
            # Justification removed per user request
        })
        rows.append(row)

    # Check for missing principles
    expected_ids = ["1", "2", "3", "4", "5", "6", "7"]
    missing_ids = [pid for pid in expected_ids if pid not in found_ids]
    
    if missing_ids:
        for mid in missing_ids:
            # Find name for ID
            nice_name = next((k for k, v in PRINCIPLE_NAME_TO_ID.items() if v == mid), f"Principle {mid}")
            row = metadata.copy()
            row.update({
                "Principle_Name": nice_name.title(),
                "Principle_ID": mid,
                "Rating": "❌ MISSING IN JSON",
                "Num_Sections": 0,
                "Structure_Status": "❌ MISSING",
                "Official_Text_Status": "N/A"
            })
            rows.append(row)

    return rows

# ========== MAIN ==========
def main():
    script_dir = Path(__file__).parent
    folder_path = (script_dir / ".." / "main_outputs").resolve()
    
    output_dir = script_dir / "outputs"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "GDPR_thesis_analysis_results.xlsx"
    
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_path}")
        return

    print(f"🚀 Scanning {folder_path}...")
    files = list(folder_path.rglob("*.json"))
    
    all_rows = []
    
    for f in files:
        print(f"   running: {f.name}")
        rows = analyze_json_file(f)
        all_rows.extend(rows)
        
    if not all_rows:
        print("\n❌ No data found! Check if JSON files are valid.")
        return

    # Create DataFrame
    df = pd.DataFrame(all_rows)
    
    # Sort for better readability
    if "Principle_ID" in df.columns:
        df = df.sort_values(by=["Filename", "Principle_ID"])

    # Split Sheets
    df_zero = df[df["Strategy"] == "Zero-Shot"]
    df_few = df[df["Strategy"] == "Few-Shot"]

    print(f"\n💾 Saving to {output_file.name}...")
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Master_Table", index=False)
            if not df_zero.empty:
                df_zero.to_excel(writer, sheet_name="Zero_Shot", index=False)
            if not df_few.empty:
                df_few.to_excel(writer, sheet_name="Few_Shot", index=False)

            # Split by Model
            if "Model" in df.columns:
                unique_models = df["Model"].dropna().unique()
                for model in unique_models:
                    model_df = df[df["Model"] == model]
                    if not model_df.empty:
                        # Clean name for Excel (max 31 chars, no invalid chars)
                        sheet_name = f"Model_{model}"[:31].replace(":", "").replace("/", "") # type: ignore
                        model_df.to_excel(writer, sheet_name=sheet_name, index=False)
        print("✅ Done! File saved successfully.")
    except Exception as e:
        print(f"\n❌ ERROR SAVING EXCEL FILE: {e}")
        print("💡 Solution: Close the Excel file if it is open!")

if __name__ == "__main__":
    main()
