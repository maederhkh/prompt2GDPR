import pandas as pd  # type: ignore
from itertools import combinations

# ========== LOAD DATA ==========
file_path = './outputs/GDPR_thesis_analysis_results.xlsx'  # Adjust path if needed
df = pd.read_excel(file_path, sheet_name='Master_Table')  # Change sheet name if different

# ========== DEFINE VARIANTS FOR EACH MODEL ==========
# GPT-5 variants (6 total)
gpt5_variants = {
    'Zero-Standard': 'zero_shot_gpt5.3rd.json',
    'Zero-Extended': 'Zero-shot.3rd.GPT5.EXTENDED.THINKING.JSON',
    'Few1': '1st few shot output.GPT5.json',
    'Few2': '2nd few shot output.GPT5.json',
    'Few3-Standard': '3rd few shot output.GPT5.json',
    'Few3-Extended': '3rd few shot output.GPT5.EXTENDED THINKING.JSON'
}

# Grok variants (6 total)
grok_variants = {
    'Zero-Standard': 'zero_shot_grok.3rd.json',
    'Zero-Expert': 'zero-shot.3rd.grok.expert.json',
    'Few1': '1st few shot output.Grok.json',
    'Few2': '2nd few shot output.Grok.json',
    'Few3-Standard': '3rd few shot output.Grok.json',
    'Few3-Expert': '3rd few shot output.Grok.Expert.json'
}

# ========== COMPUTE FLIP RATE FUNCTION ==========
def compute_flip_rate(df, var1_file, var2_file):
    """Compare ratings for 7 principles between two variants."""
    v1 = df[df['Filename'] == var1_file][['Principle_ID', 'Rating']].set_index('Principle_ID')
    v2 = df[df['Filename'] == var2_file][['Principle_ID', 'Rating']].set_index('Principle_ID')
    
    if len(v1) == 0 or len(v2) == 0:
        return None, None  # Missing data
    
    merged = v1.join(v2, lsuffix='_v1', rsuffix='_v2', how='inner')
    flips = merged['Rating_v1'].ne(merged['Rating_v2']).sum()
    total = len(merged)
    flip_rate = (flips / total * 100) if total > 0 else 0
    
    return flip_rate, flips

# ========== COMPUTE ALL PAIRWISE FLIPS ==========
def compute_all_flips(df, variants_dict, model_name):
    """Compute flip rate for all pairs of variants."""
    results = []
    variant_names = list(variants_dict.keys())
    
    for v1, v2 in combinations(variant_names, 2):
        file1 = variants_dict[v1]
        file2 = variants_dict[v2]
        flip_rate, flips = compute_flip_rate(df, file1, file2)
        
        if flip_rate is not None:
            results.append({
                'Model': model_name,
                'Variant1': v1,
                'Variant2': v2,
                'Flip_Rate_%': round(flip_rate, 1),
                'Flips_Count': flips
            })
    
    return pd.DataFrame(results)

# ========== RUN ANALYSIS ==========
print("Computing GPT-5 flip rates...")
gpt5_results = compute_all_flips(df, gpt5_variants, 'GPT-5')

print("\nComputing Grok flip rates...")
grok_results = compute_all_flips(df, grok_variants, 'Grok')

# Combine results
all_results = pd.concat([gpt5_results, grok_results], ignore_index=True)

# ========== SUMMARY STATISTICS ==========
print("\n" + "="*60)
print("FLIP RATE ANALYSIS - ALL PAIRWISE COMPARISONS")
print("="*60)
print(all_results.to_string(index=False))

print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)
for model in ['GPT-5', 'Grok']:
    model_data = all_results[all_results['Model'] == model]
    mean_flip = model_data['Flip_Rate_%'].mean()
    median_flip = model_data['Flip_Rate_%'].median()
    max_flip = model_data['Flip_Rate_%'].max()
    
    print(f"\n{model}:")
    print(f"  Mean Flip Rate:   {mean_flip:.1f}%")
    print(f"  Median Flip Rate: {median_flip:.1f}%")
    print(f"  Max Flip Rate:    {max_flip:.1f}%")

# ========== SAVE TO CSV ==========
output_file = './outputs/flip_rate_analysis_v2.csv'
all_results.to_csv(output_file, index=False)
print(f"\n[OK] Results saved to: {output_file}")
