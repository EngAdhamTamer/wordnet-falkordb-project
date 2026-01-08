from rdflib import Graph
from falkordb import FalkorDB
import os
import time
import re

def clean_relationship_name(name):
    """
    Clean relationship names for FalkorDB compatibility
    """
    clean = str(name)
    # Replace spaces, hyphens, dots, colons with underscores
    clean = clean.replace(' ', '_').replace('-', '_').replace('.', '_').replace(':', '_')
    
    # If starts with digit, add prefix
    if clean and clean[0].isdigit():
        clean = 'rel_' + clean
    
    # Remove any remaining invalid characters
    clean = re.sub(r'[^a-zA-Z0-9_]', '', clean)
    
    # Ensure it's not empty
    if not clean:
        clean = 'RELATED'
    
    # Truncate if too long
    return clean[:50]

def detect_rdf_format(file_path):
    """
    Detect RDF file format from extension
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    format_map = {
        '.ttl': 'turtle',
        '.n3': 'n3',
        '.nt': 'nt',
        '.xml': 'xml',
        '.rdf': 'xml',
        '.json': 'json-ld',
        '.jsonld': 'json-ld',
        '.nq': 'nquads',
        '.trig': 'trig'
    }
    
    return format_map.get(ext, 'turtle')  # default to turtle

def load_any_rdf_to_falkordb(rdf_file_path, graph_name=None, host='localhost', port=6379, sample_size=None):
    """
    Generic function to load ANY RDF file into FalkorDB
    
    Args:
        rdf_file_path: path to any RDF file (.ttl, .rdf, .xml, .jsonld, .nt, .n3, etc.)
        graph_name: name of graph in FalkorDB (default: filename without extension)
        host: FalkorDB host
        port: FalkorDB port
        sample_size: number of triples to load (None for all)
    
    Returns:
        dict with loading statistics
    """
    total_start = time.time()
    
    # Auto-generate graph name if not provided
    if graph_name is None:
        graph_name = os.path.splitext(os.path.basename(rdf_file_path))[0]
    
    print(f"🚀 Loading RDF file: {rdf_file_path}")
    print(f"📊 Target graph: {graph_name}")
    
    # Detect file format
    file_format = detect_rdf_format(rdf_file_path)
    print(f"📄 Detected format: {file_format}")
    
    # Connect to FalkorDB
    print(f"🔗 Connecting to FalkorDB at {host}:{port}")
    try:
        db = FalkorDB(host=host, port=port)
        graph = db.select_graph(graph_name)
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ ERROR connecting to FalkorDB: {e}")
        return {'error': f'Connection failed: {e}'}
    
    # Clear existing data in this graph
    print("🧹 Clearing existing data in graph...")
    try:
        graph.query("MATCH (n) DETACH DELETE n")
        print("✅ Data cleared successfully")
    except Exception as e:
        print(f"⚠️ Warning while clearing data: {e}")
    
    # Parse RDF file
    print(f"\n📖 Parsing RDF file ({file_format})...")
    parse_start = time.time()
    
    if not os.path.exists(rdf_file_path):
        print(f"❌ ERROR: File not found: {rdf_file_path}")
        return {'error': f'File not found: {rdf_file_path}'}
    
    try:
        g = Graph()
        g.parse(rdf_file_path, format=file_format)
        parse_time = time.time() - parse_start
        total_triples = len(g)
        print(f"✅ Parsing completed in {parse_time:.2f} seconds")
        print(f"📈 Found {total_triples:,} total triples")
    except Exception as e:
        print(f"❌ ERROR parsing RDF file: {e}")
        print(f"💡 Trying alternative parsing methods...")
        
        # Try alternative formats
        alt_formats = ['xml', 'n3', 'nt', 'turtle']
        for alt_format in alt_formats:
            if alt_format != file_format:
                try:
                    print(f"   Trying {alt_format} format...")
                    g = Graph()
                    g.parse(rdf_file_path, format=alt_format)
                    parse_time = time.time() - parse_start
                    total_triples = len(g)
                    print(f"✅ Parsing successful with {alt_format} format")
                    print(f"📈 Found {total_triples:,} total triples")
                    file_format = alt_format
                    break
                except:
                    continue
        
        if 'g' not in locals():
            return {'error': f'Could not parse RDF file with any format'}
    
    # Determine how many to load
    if sample_size and sample_size < total_triples:
        triples_to_load = sample_size
        print(f"📋 Loading sample of {triples_to_load:,} triples")
    else:
        triples_to_load = total_triples
        print(f"📋 Loading all {triples_to_load:,} triples")
    
    # Collect unique nodes and relationships
    print("\n🔍 Processing triples...")
    process_start = time.time()
    
    nodes = {}
    relationships = []
    relationship_types = {}
    count = 0
    
    for subj, pred, obj in g:
        if sample_size and count >= sample_size:
            break
        
        subj_uri = str(subj)
        obj_uri = str(obj)
        
        # Create labels from URIs
        subj_label = subj_uri
        obj_label = obj_uri
        
        # Extract meaningful names from URIs
        for sep in ['#', '/']:
            if sep in subj_uri:
                subj_label = subj_uri.rsplit(sep, 1)[-1][:100]
                break
        
        for sep in ['#', '/']:
            if sep in obj_uri:
                obj_label = obj_uri.rsplit(sep, 1)[-1][:100]
                break
        
        # Get and clean predicate name
        pred_str = str(pred)
        pred_name = pred_str
        
        # Extract local name from URI
        for sep in ['#', '/']:
            if sep in pred_str:
                pred_name = pred_str.rsplit(sep, 1)[-1]
                break
        
        pred_name = clean_relationship_name(pred_name)
        
        # Track relationship types
        relationship_types[pred_name] = relationship_types.get(pred_name, 0) + 1
        
        # Store nodes
        if subj_uri not in nodes:
            nodes[subj_uri] = subj_label[:100]  # Limit label length
        if obj_uri not in nodes:
            nodes[obj_uri] = obj_label[:100]
        
        relationships.append((subj_uri, pred_name, obj_uri))
        count += 1
        
        if count % 10000 == 0:
            elapsed = time.time() - process_start
            rate = count / elapsed if elapsed > 0 else 0
            print(f"  Processed {count:,}/{triples_to_load:,} triples ({rate:.0f}/sec)")
    
    process_time = time.time() - process_start
    print(f"✅ Processing completed in {process_time:.2f} seconds")
    print(f"📊 Collected: {len(nodes):,} unique nodes, {len(relationships):,} relationships")
    print(f"📋 Found {len(relationship_types)} unique relationship types")
    
    # Show top relationship types
    if relationship_types:
        print("\n🔗 Top 10 relationship types:")
        sorted_types = sorted(relationship_types.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (rel_type, count) in enumerate(sorted_types, 1):
            print(f"  {i:2d}. {rel_type:25s} - {count:6d}")
    
    # Load nodes
    print(f"\n📥 Loading {len(nodes):,} nodes...")
    node_start = time.time()
    
    total_nodes_created = 0
    batch_size = 1000
    node_items = list(nodes.items())
    
    for i in range(0, len(node_items), batch_size):
        batch = node_items[i:i + batch_size]
        
        for uri, label in batch:
            try:
                # Escape quotes
                safe_uri = uri.replace("'", "\\'")
                safe_label = label.replace("'", "\\'") if label else ''
                
                query = f"CREATE (n:Resource {{uri: '{safe_uri}', name: '{safe_label}'}})"
                graph.query(query)
                total_nodes_created += 1
            except:
                # Fallback without escaping
                try:
                    safe_uri = uri.replace("'", "")
                    safe_label = label.replace("'", "") if label else ''
                    query = f"CREATE (n:Resource {{uri: '{safe_uri}', name: '{safe_label}'}})"
                    graph.query(query)
                    total_nodes_created += 1
                except:
                    pass
        
        if (i // batch_size) % 10 == 0 or i + batch_size >= len(node_items):
            elapsed = time.time() - node_start
            rate = total_nodes_created / elapsed if elapsed > 0 else 0
            print(f"  ✅ Loaded {total_nodes_created:,}/{len(nodes):,} nodes ({rate:.0f}/sec)")
    
    node_time = time.time() - node_start
    print(f"✅ Nodes loaded in {node_time:.2f} seconds")
    
    # Load relationships
    print(f"\n🔗 Creating {len(relationships):,} relationships...")
    rel_start = time.time()
    
    # Group by relationship type for efficiency
    rels_by_type = {}
    for source, pred, target in relationships:
        if pred not in rels_by_type:
            rels_by_type[pred] = []
        rels_by_type[pred].append((source, target))
    
    total_rels_created = 0
    failed_rels = 0
    
    for rel_idx, (rel_type, rel_list) in enumerate(rels_by_type.items()):
        if rel_idx % 10 == 0 or rel_idx == len(rels_by_type) - 1:
            print(f"  [{rel_idx+1}/{len(rels_by_type)}] Creating '{rel_type}' ({len(rel_list):,})...")
        
        type_created = 0
        
        # Process in batches
        for i in range(0, len(rel_list), 500):
            batch = rel_list[i:i + 500]
            
            for source, target in batch:
                try:
                    safe_source = source.replace("'", "\\'").replace('"', '\\"')
                    safe_target = target.replace("'", "\\'").replace('"', '\\"')
                    
                    query = f"""
                    MATCH (s:Resource {{uri: '{safe_source}'}})
                    MATCH (t:Resource {{uri: '{safe_target}'}})
                    CREATE (s)-[:{rel_type}]->(t)
                    """
                    
                    graph.query(query)
                    type_created += 1
                    total_rels_created += 1
                except:
                    failed_rels += 1
        
        if rel_idx % 10 == 0 or rel_idx == len(rels_by_type) - 1:
            print(f"    ✅ Created {type_created:,} {rel_type} relationships")
    
    rel_time = time.time() - rel_start
    total_time = time.time() - total_start
    
    # Final summary
    print(f"\n{'='*70}")
    print("🎉 GENERIC RDF LOADING COMPLETE!")
    print(f"{'='*70}")
    print(f"📊 SUMMARY:")
    print(f"  • File: {os.path.basename(rdf_file_path)}")
    print(f"  • Format: {file_format}")
    print(f"  • Graph: {graph_name}")
    print(f"  • Total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
    print(f"  • Triples loaded: {count:,}")
    print(f"  • Nodes created: {total_nodes_created:,}")
    print(f"  • Relationships created: {total_rels_created:,}")
    print(f"  • Relationship types: {len(rels_by_type)}")
    print(f"  • Failed relationships: {failed_rels:,}")
    
    # Return statistics
    return {
        'file': rdf_file_path,
        'graph_name': graph_name,
        'format': file_format,
        'triples_loaded': count,
        'nodes_created': total_nodes_created,
        'relationships_created': total_rels_created,
        'relationship_types_count': len(rels_by_type),
        'failed_relationships': failed_rels,
        'elapsed_seconds': total_time,
        'parse_time': parse_time,
        'process_time': process_time,
        'node_load_time': node_time,
        'relationship_load_time': rel_time
    }

# Example usage
if __name__ == "__main__":
    # Test with WordNet
    print("🔬 Testing generic RDF loader with WordNet...")
    result = load_any_rdf_to_falkordb(
        rdf_file_path='data/english-wordnet-2024.ttl',
        graph_name='wordnet_2024',
        sample_size=5000
    )
    
    print(f"\n📋 Test result: {result}")
    
    # You can now load any RDF file:
    # load_any_rdf_to_falkordb('path/to/your/file.rdf')
    # load_any_rdf_to_falkordb('path/to/your/file.ttl')
    # load_any_rdf_to_falkordb('path/to/your/file.jsonld')