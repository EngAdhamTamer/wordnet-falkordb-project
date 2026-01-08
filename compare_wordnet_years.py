import json
import argparse
from datetime import datetime

def load_wordnet_json(file_path):
    """Load WordNet JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {file_path}: {len(data)} entries")
        return data
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return None

def compare_wordnet_files(file1_path, file2_path, output_path=None):
    """
    Compare two WordNet JSON files and find differences (file2 - file1)
    
    Args:
        file1_path: Path to older WordNet file (e.g., 2024)
        file2_path: Path to newer WordNet file (e.g., 2025)
        output_path: Path to save difference JSON (optional)
    
    Returns:
        Dictionary with added, removed, and modified entries
    """
    print(f"🔍 Comparing WordNet files:")
    print(f"  • File 1 (older): {file1_path}")
    print(f"  • File 2 (newer): {file2_path}")
    
    # Load both files
    data1 = load_wordnet_json(file1_path)
    data2 = load_wordnet_json(file2_path)
    
    if not data1 or not data2:
        return None
    
    # Convert to dictionaries with IDs as keys for easier comparison
    dict1 = {entry.get('id', idx): entry for idx, entry in enumerate(data1)}
    dict2 = {entry.get('id', idx): entry for idx, entry in enumerate(data2)}
    
    # Find differences
    ids1 = set(dict1.keys())
    ids2 = set(dict2.keys())
    
    # Added entries (in file2 but not in file1)
    added_ids = ids2 - ids1
    added_entries = [dict2[id] for id in added_ids]
    
    # Removed entries (in file1 but not in file2)
    removed_ids = ids1 - ids2
    removed_entries = [dict1[id] for id in removed_ids]
    
    # Modified entries (in both but different)
    common_ids = ids1.intersection(ids2)
    modified_entries = []
    
    for id in common_ids:
        entry1 = dict1[id]
        entry2 = dict2[id]
        
        # Convert to JSON strings for comparison (ignoring order)
        str1 = json.dumps(entry1, sort_keys=True)
        str2 = json.dumps(entry2, sort_keys=True)
        
        if str1 != str2:
            modified_entries.append({
                'id': id,
                'old': entry1,
                'new': entry2,
                'differences': find_json_differences(entry1, entry2)
            })
    
    # Create result dictionary
    result = {
        'comparison_info': {
            'file1': file1_path,
            'file2': file2_path,
            'comparison_date': datetime.now().isoformat(),
            'operation': 'file2 - file1 (newer minus older)'
        },
        'statistics': {
            'total_file1_entries': len(data1),
            'total_file2_entries': len(data2),
            'added_entries': len(added_entries),
            'removed_entries': len(removed_entries),
            'modified_entries': len(modified_entries)
        },
        'added': added_entries,
        'removed': removed_entries,
        'modified': modified_entries
    }
    
    # Save to file if output path provided
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Comparison saved to: {output_path}")
        except Exception as e:
            print(f"❌ Error saving output: {e}")
    
    # Print summary
    print(f"\n📊 COMPARISON SUMMARY:")
    print(f"  • Total entries in file 1: {len(data1)}")
    print(f"  • Total entries in file 2: {len(data2)}")
    print(f"  • Added entries: {len(added_entries)}")
    print(f"  • Removed entries: {len(removed_entries)}")
    print(f"  • Modified entries: {len(modified_entries)}")
    
    if added_entries:
        print(f"\n📥 ADDED ENTRIES (first 5):")
        for i, entry in enumerate(added_entries[:5], 1):
            print(f"  {i}. {entry.get('id', 'No ID')} - {entry.get('word', 'No word')}")
    
    if removed_entries:
        print(f"\n🗑️ REMOVED ENTRIES (first 5):")
        for i, entry in enumerate(removed_entries[:5], 1):
            print(f"  {i}. {entry.get('id', 'No ID')} - {entry.get('word', 'No word')}")
    
    if modified_entries:
        print(f"\n✏️ MODIFIED ENTRIES (first 3):")
        for i, mod in enumerate(modified_entries[:3], 1):
            print(f"  {i}. ID: {mod['id']}")
            for diff in mod['differences'][:2]:  # Show first 2 differences
                print(f"     - {diff}")
    
    return result

def find_json_differences(obj1, obj2, path=""):
    """Find differences between two JSON objects"""
    differences = []
    
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            
            if key in obj1 and key in obj2:
                differences.extend(
                    find_json_differences(obj1[key], obj2[key], new_path)
                )
            elif key in obj1:
                differences.append(f"{new_path}: removed (was: {obj1[key]})")
            else:
                differences.append(f"{new_path}: added (is: {obj2[key]})")
    
    elif isinstance(obj1, list) and isinstance(obj2, list):
        # Simple list comparison - for WordNet, usually lists of strings
        if len(obj1) != len(obj2):
            differences.append(f"{path}: list length changed from {len(obj1)} to {len(obj2)}")
        
        # Compare elements
        for i, (item1, item2) in enumerate(zip(obj1, obj2)):
            if item1 != item2:
                differences.append(f"{path}[{i}]: changed from '{item1}' to '{item2}'")
    
    elif obj1 != obj2:
        differences.append(f"{path}: changed from '{obj1}' to '{obj2}'")
    
    return differences

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Compare two WordNet JSON files')
    parser.add_argument('file1', help='Older WordNet JSON file (e.g., 2024)')
    parser.add_argument('file2', help='Newer WordNet JSON file (e.g., 2025)')
    parser.add_argument('-o', '--output', help='Output JSON file for differences')
    
    args = parser.parse_args()
    
    # Run comparison
    result = compare_wordnet_files(args.file1, args.file2, args.output)
    
    if result:
        print(f"\n✅ Comparison completed successfully!")
        if args.output:
            print(f"📁 Results saved to: {args.output}")
    else:
        print(f"\n❌ Comparison failed!")

if __name__ == "__main__":
    # Example usage
    print("🔍 WordNet Year Comparison Tool")
    print("="*50)
    
    # You would use it like:
    # python compare_wordnet_years.py wordnet-2024.json wordnet-2025.json -o differences.json
    
    # For testing without command line arguments:
    print("\n💡 To use this tool, run:")
    print("   python compare_wordnet_years.py wordnet-2024.json wordnet-2025.json -o differences.json")
    
    # Or call the function directly:
    # result = compare_wordnet_files('wordnet-2024.json', 'wordnet-2025.json', 'differences.json')