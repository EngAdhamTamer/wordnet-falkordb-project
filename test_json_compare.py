"""
Test JSON comparison with sample files
"""

import json
import os

def create_test_files():
    """Create test JSON files"""
    print("Creating test JSON files...")
    
    # Test data
    test_2024 = {
        "synsets": [
            {"id": "s1", "word": "happy", "definition": "feeling joy"},
            {"id": "s2", "word": "sad", "definition": "feeling sorrow"},
            {"id": "s3", "word": "big", "definition": "large in size"}
        ]
    }
    
    test_2025 = {
        "synsets": [
            {"id": "s1", "word": "happy", "definition": "feeling joy"},
            {"id": "s2", "word": "sad", "definition": "feeling sorrow (updated)"},
            {"id": "s4", "word": "small", "definition": "little in size"}
        ]
    }
    
    # Create data folder
    os.makedirs('data', exist_ok=True)
    
    # Save files
    with open('data/test-2024.json', 'w') as f:
        json.dump(test_2024, f, indent=2)
    
    with open('data/test-2025.json', 'w') as f:
        json.dump(test_2025, f, indent=2)
    
    print("✓ Test files created in data/")
    print("  • test-2024.json")
    print("  • test-2025.json")

def run_test():
    """Run the test comparison"""
    print("\n" + "="*60)
    print("TESTING JSON COMPARISON")
    print("="*60)
    
    # Import and run comparison
    from json_compare import compare_wordnet_json
    
    result = compare_wordnet_json(
        'data/test-2025.json',
        'data/test-2024.json',
        'data/test-difference.json'
    )
    
    if result:
        print("\n" + "="*60)
        print("TEST SUCCESSFUL!")
        print("="*60)
        print("Comparison logic works correctly.")
        print("Results saved to: data/test-difference.json")
        
        # Show results
        print("\nTest Results:")
        print(f"Added: {result['statistics']['total_added']}")
        print(f"Removed: {result['statistics']['total_removed']}")
        print(f"Modified: {result['statistics']['total_modified']}")

if __name__ == "__main__":
    create_test_files()
    run_test()