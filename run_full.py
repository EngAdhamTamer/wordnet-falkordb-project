from generic_rdf_loader import load_any_rdf_to_falkordb

print("🚀 LOADING FULL WORDNET (3.8M triples)")
result = load_any_rdf_to_falkordb(
    rdf_file_path='data/english-wordnet-2024.ttl',
    graph_name='wordnet_full',
    sample_size=None  # Load EVERYTHING
)

print(f"\n📊 FULL LOAD COMPLETE: {result}")