"""
WordNet FalkorDB Project
Main entry point
"""

from rdf_loader import load_rdf_to_falkordb
import os
import sys

def run_rdf_loader():
    """Run Task 1-3: RDF to FalkorDB loader"""
    print("\n" + "="*60)
    print("RDF TO FALKORDB LOADER")
    print("="*60)
    
    # Create data directory
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Check for RDF files
    rdf_files = [f for f in os.listdir('data') if f.endswith('.ttl')]
    
    if not rdf_files:
        print("\nNo RDF (.ttl) files found in 'data' folder.")
        print("\nTo use:")
        print("1. Download RDF from https://en-word.net/")
        print("2. Place in 'data/' folder (e.g., english-wordnet-2024.ttl)")
        print("3. Run: docker-compose up --build")
        return None
    
    print(f"\nFound RDF files: {', '.join(rdf_files)}")
    
    # Use first file
    rdf_file = f"data/{rdf_files[0]}"
    print(f"Loading: {rdf_file}")
    
    try:
        # Ask for sample or full
        print("\nOptions:")
        print("1. Test with sample (1000 triples)")
        print("2. Load full file (~1.5 hours)")
        print("3. Cancel")
        
        choice = input("\nEnter choice (1-3): ")
        
        if choice == '1':
            print("\nLoading sample...")
            stats = load_rdf_to_falkordb(rdf_file, sample_size=1000)
        elif choice == '2':
            print("\nLoading full file...")
            stats = load_rdf_to_falkordb(rdf_file)
        else:
            print("Cancelled")
            return None
        
        if stats and 'error' not in stats:
            print("\n✓ Loading complete!")
            print(f"  Triples: {stats['triples_loaded']:,}")
            print(f"  Nodes: {stats['nodes_created']:,}")
            print(f"  Relationships: {stats['relationships_created']:,}")
            print(f"  Time: {stats['elapsed_seconds']:.0f} seconds")
            return stats
        else:
            print(f"✗ Error: {stats.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return None

def run_json_comparison():
    """Run Task 4: JSON comparison"""
    print("\n" + "="*60)
    print("JSON COMPARISON")
    print("="*60)
    print("To compare JSON files:")
    print("1. Download JSON files from https://en-word.net/")
    print("2. Place in 'data/' folder:")
    print("   • english-wordnet-2025.json")
    print("   • english-wordnet-2025-plus.json")
    print("3. Run: python json_compare.py")
    print("\nFor test comparison:")
    print("  python test_json_compare.py")
    print("="*60)
    
    return None

def main():
    """Main function"""
    print("="*60)
    print("WORDNET FALKORDB PROJECT")
    print("="*60)
    print("Tasks:")
    print("1. RDF Loader (Tasks 1-3)")
    print("2. JSON Comparison (Task 4)")
    print("3. Docker Setup")
    print("="*60)
    
    print("\nSelect:")
    print("1. Run RDF loader")
    print("2. Show JSON comparison info")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ")
    
    if choice == '1':
        run_rdf_loader()
    elif choice == '2':
        run_json_comparison()
    else:
        print("Exiting...")
        return
    
    print("\n" + "="*60)
    print("DOCKER SETUP:")
    print("docker-compose up --build")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)