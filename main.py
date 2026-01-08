"""
WordNet FalkorDB Project
Main entry point - Fixed for Docker compatibility
"""

from rdf_loader import load_rdf_to_falkordb
import os
import sys

def run_rdf_loader(mode='sample'):
    """Run Task 1-3: RDF to FalkorDB loader
    
    Args:
        mode: 'sample' for 1000 triples, 'full' for complete load, 'skip' to skip
    """
    print("\n" + "="*60)
    print("RDF TO FALKORDB LOADER")
    print("="*60)
    
    # Create data directory
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Check for RDF files
    rdf_files = [f for f in os.listdir('data') if f.endswith('.ttl')]
    
    if not rdf_files:
        print("\n❌ No RDF (.ttl) files found in 'data' folder.")
        print("\nTo use:")
        print("1. Download RDF from https://en-word.net/")
        print("2. Place in 'data/' folder (e.g., english-wordnet-2024.ttl)")
        print("3. Run: docker-compose up --build")
        return None
    
    print(f"\n✅ Found RDF files: {', '.join(rdf_files)}")
    
    # Use first file
    rdf_file = f"data/{rdf_files[0]}"
    print(f"📂 Loading: {rdf_file}")
    
    try:
        if mode == 'sample':
            print("\n🔬 Loading sample (1000 triples)...")
            stats = load_rdf_to_falkordb(rdf_file, sample_size=1000)
        elif mode == 'full':
            print("\n🚀 Loading full file (~1.5 hours)...")
            stats = load_rdf_to_falkordb(rdf_file)
        else:
            print("⏭️  Skipping RDF load")
            return None
        
        if stats and 'error' not in stats:
            print("\n✅ Loading complete!")
            print(f"  Triples: {stats['triples_loaded']:,}")
            print(f"  Nodes: {stats['nodes_created']:,}")
            print(f"  Relationships: {stats['relationships_created']:,}")
            print(f"  Time: {stats['elapsed_seconds']:.0f} seconds")
            return stats
        else:
            print(f"❌ Error: {stats.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
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
    """Main function - supports both interactive and environment variable modes"""
    
    # Check for environment variable mode (for Docker)
    mode = os.getenv('WORDNET_MODE', 'interactive').lower()
    
    print("="*60)
    print("WORDNET FALKORDB PROJECT")
    print("="*60)
    
    if mode != 'interactive':
        # Non-interactive mode (Docker)
        print(f"🐳 Running in Docker mode: {mode}")
        print("="*60)
        
        if mode == 'sample':
            run_rdf_loader(mode='sample')
        elif mode == 'full':
            run_rdf_loader(mode='full')
        elif mode == 'json_compare':
            run_json_comparison()
        elif mode == 'skip':
            print("\n⏭️  Skipping automatic load")
            print("💡 To load data, use: docker-compose exec wordnet-loader python main.py")
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Valid modes: sample, full, json_compare, skip")
        
        # Keep container running if in skip mode
        if mode == 'skip':
            print("\n⏳ Container ready. Waiting...")
            print("💡 Run commands with: docker-compose exec wordnet-loader python main.py")
            # Keep alive
            try:
                import time
                while True:
                    time.sleep(3600)
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
        
        return
    
    # Interactive mode (local Python)
    print("Tasks:")
    print("1. RDF Loader (Tasks 1-3)")
    print("2. JSON Comparison (Task 4)")
    print("3. Docker Setup")
    print("="*60)
    
    print("\nSelect:")
    print("1. Run RDF loader (sample)")
    print("2. Run RDF loader (full)")
    print("3. Show JSON comparison info")
    print("4. Exit")
    
    try:
        choice = input("\nEnter choice (1-4): ")
        
        if choice == '1':
            run_rdf_loader(mode='sample')
        elif choice == '2':
            run_rdf_loader(mode='full')
        elif choice == '3':
            run_json_comparison()
        else:
            print("Exiting...")
            return
        
        print("\n" + "="*60)
        print("DOCKER SETUP:")
        print("docker-compose up --build")
        print("="*60)
        
    except EOFError:
        print("\n❌ Error: Running in non-interactive environment")
        print("💡 Use environment variable WORDNET_MODE instead")
        print("   Options: sample, full, json_compare, skip")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        sys.exit(0)