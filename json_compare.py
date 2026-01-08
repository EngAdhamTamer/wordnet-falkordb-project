"""
WordNet JSON Comparison Tool
Manual download required - place JSON files in data/ folder
"""

import json
import os
import sys

def check_json_files():
    """Check if required JSON files exist"""
    print("="*60)
    print("JSON FILE CHECK")
    print("="*60)
    
    files_needed = {
        '2025 Edition': 'data/english-wordnet-2025.json',
        '2025 Plus': 'data/english-wordnet-2025-plus.json'
    }
    
    all_exist = True
    
    for name, path in files_needed.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✓ {name}: {path}")
            print(f"  Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
        else:
            print(f"✗ {name}: NOT FOUND")
            print(f"  Expected: {path}")
            all_exist = False
    
    return all_exist

def show_download_instructions():
    """Show instructions for manual download"""
    print("\n" + "="*60)
    print("DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print("\n1. Download JSON files from:")
    print("   https://en-word.net/")
    print("\n2. You need these files:")
    print("   • english-wordnet-2025.json")
    print("   • english-wordnet-2025-plus.json")
    print("\n3. Place them in the 'data' folder:")
    print("   wordnet-falkordb-project/")
    print("   └── data/")
    print("       ├── english-wordnet-2025.json")
    print("       └── english-wordnet-2025-plus.json")
    print("\n4. Run this script again:")
    print("   python json_compare.py")
    print("\n" + "="*60)

def compare_wordnet_json(file1_path, file2_path, output_path='data/difference.json'):
    """
    Compare two WordNet JSON files
    file1_path: newer file (2025 Plus)
    file2_path: older file (2025 Edition)
    """
    print("\n" + "="*60)
    print("COMPARING JSON FILES")
    print("="*60)
    print(f"Newer: {os.path.basename(file1_path)}")
    print(f"Older: {os.path.basename(file2_path)}")
    
    try:
        # Load JSON files
        with open(file1_path, 'r', encoding='utf-8') as f:
            data1 = json.load(f)
        
        with open(file2_path, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        
        print("✓ Files loaded successfully")
        
    except Exception as e:
        print(f"✗ Error loading files: {e}")
        return None
    
    # Find synsets in data
    def get_synsets(data):
        if isinstance(data, dict):
            if 'synsets' in data:
                return data['synsets']
            elif 'entries' in data:
                return data['entries']
        elif isinstance(data, list):
            return data
        return []
    
    synsets1 = get_synsets(data1)
    synsets2 = get_synsets(data2)
    
    # Convert to dict with ID as key
    synsets1_dict = {}
    synsets2_dict = {}
    
    for i, synset in enumerate(synsets1):
        if isinstance(synset, dict):
            sid = synset.get('id', synset.get('synsetId', f"synset_{i}"))
            synsets1_dict[sid] = synset
    
    for i, synset in enumerate(synsets2):
        if isinstance(synset, dict):
            sid = synset.get('id', synset.get('synsetId', f"synset_{i}"))
            synsets2_dict[sid] = synset
    
    # Find differences
    differences = {
        'comparison': {
            'newer_file': os.path.basename(file1_path),
            'older_file': os.path.basename(file2_path),
            'comparison_date': os.path.getmtime(file1_path)
        },
        'added_synsets': [],
        'removed_synsets': [],
        'modified_synsets': [],
        'statistics': {}
    }
    
    # Find added synsets (in newer, not in older)
    added = []
    for sid in synsets1_dict:
        if sid not in synsets2_dict:
            added.append(synsets1_dict[sid])
    
    # Find removed synsets (in older, not in newer)
    removed = []
    for sid in synsets2_dict:
        if sid not in synsets1_dict:
            removed.append(synsets2_dict[sid])
    
    # Find modified synsets (in both but different)
    modified = []
    for sid in synsets1_dict:
        if sid in synsets2_dict:
            if json.dumps(synsets1_dict[sid], sort_keys=True) != json.dumps(synsets2_dict[sid], sort_keys=True):
                modified.append({
                    'id': sid,
                    'old': synsets2_dict[sid],
                    'new': synsets1_dict[sid]
                })
    
    differences['added_synsets'] = added
    differences['removed_synsets'] = removed
    differences['modified_synsets'] = modified
    
    # Statistics
    differences['statistics'] = {
        'total_added': len(added),
        'total_removed': len(removed),
        'total_modified': len(modified),
        'newer_total_synsets': len(synsets1_dict),
        'older_total_synsets': len(synsets2_dict),
        'newer_file_size': os.path.getsize(file1_path),
        'older_file_size': os.path.getsize(file2_path)
    }
    
    # Save to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(differences, f, indent=2, ensure_ascii=False)
        print(f"✓ Differences saved to {output_path}")
    except Exception as e:
        print(f"✗ Error saving differences: {e}")
        return differences
    
    # Print summary
    print("\n" + "="*50)
    print("COMPARISON RESULTS")
    print("="*50)
    print(f"Added synsets:     {len(added):>6}")
    print(f"Removed synsets:   {len(removed):>6}")
    print(f"Modified synsets:  {len(modified):>6}")
    print(f"Newer total:       {len(synsets1_dict):>6}")
    print(f"Older total:       {len(synsets2_dict):>6}")
    print("="*50)
    
    return differences

def main():
    """Main function"""
    print("="*70)
    print("WORDNET JSON COMPARISON")
    print("="*70)
    print("Compares: 2025 Plus vs 2025 Edition")
    print("Manual download required")
    print("="*70)
    
    # Check if files exist
    files_exist = check_json_files()
    
    if not files_exist:
        show_download_instructions()
        sys.exit(1)
    
    # Files exist, run comparison
    print("\n" + "="*70)
    print("STARTING COMPARISON")
    print("="*70)
    
    result = compare_wordnet_json(
        'data/english-wordnet-2025-plus.json',
        'data/english-wordnet-2025.json',
        'data/difference.json'
    )
    
    if result:
        print("\n" + "="*70)
        print("COMPARISON COMPLETE!")
        print("Results saved to: data/difference.json")
        print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nComparison cancelled")
        sys.exit(0)