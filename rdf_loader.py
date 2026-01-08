from rdflib import Graph
from falkordb import FalkorDB
import os
import time
import rdflib
import re

def load_rdf_to_falkordb_optimized(rdf_file_path, graph_name='wordnet', host=None, port=None, sample_size=None):
    """
    Load RDF file into FalkorDB - Optimized version with better error handling
    
    Args:
        rdf_file_path: path to .ttl or .rdf file
        graph_name: name of graph in FalkorDB
        host: FalkorDB host
        port: FalkorDB port
        sample_size: number of triples to load (None for all)
    
    Returns:
        dict with loading statistics
    """
    if host is None:
        host = os.getenv('FALKORDB_HOST', 'localhost')
    if port is None:
        port = int(os.getenv('FALKORDB_PORT', 6379))
    
    total_start = time.time()
    print(f"🚀 Loading RDF file: {rdf_file_path}")
    print(f"📊 Estimated size: 200MB WordNet file")
    
    # Connect to FalkorDB
    print(f"🔗 Connecting to FalkorDB at {host}:{port}")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph(graph_name)
    
    # Clear existing data
    print("🧹 Clearing existing data...")
    try:
        graph.query("MATCH (n) DETACH DELETE n")
        print("✅ Data cleared successfully")
    except Exception as e:
        print(f"⚠️ Warning while clearing data: {e}")
    
    # Create index (handle if it already exists)
    print("📊 Creating index on :Resource(uri)...")
    try:
        graph.query("CREATE INDEX ON :Resource(uri)")
        print("✅ Index created successfully")
    except Exception as e:
        if "already indexed" in str(e):
            print("ℹ️ Index already exists, continuing...")
        else:
            print(f"⚠️ Warning while creating index: {e}")
            # Try to drop and recreate
            try:
                graph.query("DROP INDEX ON :Resource(uri)")
                graph.query("CREATE INDEX ON :Resource(uri)")
                print("✅ Index recreated successfully")
            except:
                print("⚠️ Could not create index, continuing without it")
    
    # Parse RDF file
    print("\n📖 Parsing RDF file (this may take a few minutes for 200MB)...")
    parse_start = time.time()
    
    # Check if file exists
    if not os.path.exists(rdf_file_path):
        print(f"❌ ERROR: File not found: {rdf_file_path}")
        print(f"💡 Please make sure the file exists in the data folder")
        return {
            'error': f'File not found: {rdf_file_path}',
            'elapsed_seconds': time.time() - total_start
        }
    
    # Parse with error handling
    try:
        g = Graph()
        g.parse(rdf_file_path, format='turtle')
        parse_time = time.time() - parse_start
        total_triples = len(g)
        print(f"✅ Parsing completed in {parse_time:.2f} seconds")
        print(f"📈 Found {total_triples:,} total triples")
    except Exception as e:
        print(f"❌ ERROR parsing RDF file: {e}")
        print("💡 Make sure the file is a valid Turtle (.ttl) format")
        return {
            'error': f'Parse error: {e}',
            'elapsed_seconds': time.time() - total_start
        }
    
    # Determine how many to load
    if sample_size and sample_size < total_triples:
        triples_to_load = sample_size
        print(f"📋 Loading sample of {triples_to_load:,} triples")
    else:
        triples_to_load = total_triples
        print(f"📋 Loading all {triples_to_load:,} triples")
    
    # PHASE 1: Collect unique nodes and relationships
    print("\n🔍 Collecting unique nodes and relationships...")
    process_start = time.time()
    
    nodes = {}
    relationships = []
    count = 0
    
    # Pre-compiled regex for faster processing
    pred_cleaner = re.compile(r'[^a-zA-Z0-9_]')
    
    for subj, pred, obj in g:
        if sample_size and count >= sample_size:
            break
        
        subj_uri = str(subj)
        obj_uri = str(obj)
        
        # Get node labels efficiently
        subj_label = subj_uri[:100]  # Default to first 100 chars
        obj_label = obj_uri[:100]
        
        if isinstance(subj, rdflib.URIRef):
            for sep in ['#', '/']:
                if sep in subj_uri:
                    subj_label = subj_uri.rsplit(sep, 1)[-1][:100]
                    break
        
        if isinstance(obj, rdflib.URIRef):
            for sep in ['#', '/']:
                if sep in obj_uri:
                    obj_label = obj_uri.rsplit(sep, 1)[-1][:100]
                    break
        
        # Clean predicate name efficiently
        pred_str = str(pred)
        pred_name = pred_str
        for sep in ['#', '/']:
            if sep in pred_str:
                pred_name = pred_str.rsplit(sep, 1)[-1]
                break
        
        # Clean predicate name
        pred_name = pred_cleaner.sub('_', pred_name)[:50]
        if not pred_name:
            pred_name = 'RELATED'
        
        # Store nodes
        if subj_uri not in nodes:
            nodes[subj_uri] = subj_label
        if obj_uri not in nodes:
            nodes[obj_uri] = obj_label
        
        relationships.append((subj_uri, pred_name, obj_uri))
        count += 1
        
        # Show progress
        if count % 50000 == 0:
            elapsed = time.time() - process_start
            rate = count / elapsed
            print(f"  Processed {count:,}/{triples_to_load:,} triples "
                  f"({rate:.0f} triples/sec, {len(nodes):,} nodes)")
    
    process_time = time.time() - process_start
    print(f"✅ Processing completed in {process_time:.2f} seconds")
    print(f"📊 Collected: {len(nodes):,} unique nodes, {len(relationships):,} relationships")
    
    # PHASE 2: Load nodes
    print(f"\n📥 Loading {len(nodes):,} nodes into FalkorDB...")
    node_start = time.time()
    
    # Prepare nodes for batch loading
    node_batches = []
    batch_size = 5000  # Smaller batch for stability
    
    node_items = list(nodes.items())
    for i in range(0, len(node_items), batch_size):
        batch = node_items[i:i + batch_size]
        node_batches.append(batch)
    
    total_nodes_created = 0
    failed_nodes = 0
    
    for batch_idx, batch in enumerate(node_batches):
        batch_start = time.time()
        
        # Create nodes one by one in this batch
        for uri, name in batch:
            try:
                # First try with proper escaping
                safe_uri = uri.replace("'", "\\'")
                safe_name = name.replace("'", "\\'")
                graph.query(f"CREATE (n:Resource {{uri: '{safe_uri}', name: '{safe_name}'}})")
                total_nodes_created += 1
            except Exception as e:
                # If that fails, try removing quotes
                try:
                    safe_uri = uri.replace("'", "")
                    safe_name = name.replace("'", "")
                    graph.query(f"CREATE (n:Resource {{uri: '{safe_uri}', name: '{safe_name}'}})")
                    total_nodes_created += 1
                except:
                    failed_nodes += 1
                    pass
        
        # Show progress every 10 batches
        if (batch_idx + 1) % 10 == 0 or batch_idx == len(node_batches) - 1:
            elapsed = time.time() - node_start
            rate = total_nodes_created / elapsed if elapsed > 0 else 0
            print(f"  ✅ Batch {batch_idx + 1}/{len(node_batches)}: "
                  f"{total_nodes_created:,} nodes ({rate:.0f} nodes/sec)")
    
    node_time = time.time() - node_start
    print(f"✅ Nodes loaded in {node_time:.2f} seconds "
          f"({total_nodes_created / node_time:.0f} nodes/sec)")
    if failed_nodes > 0:
        print(f"⚠️ Failed to create {failed_nodes} nodes")
    
    # PHASE 3: Load relationships - Optimized batch approach
    print(f"\n🔗 Creating {len(relationships):,} relationships...")
    rel_start = time.time()
    
    # Group relationships by type for more efficient creation
    rels_by_type = {}
    for source, pred, target in relationships:
        if pred not in rels_by_type:
            rels_by_type[pred] = []
        rels_by_type[pred].append((source, target))
    
    total_rels_created = 0
    failed_rels = 0
    
    # Process each relationship type separately
    for pred_idx, (pred_name, pred_rels) in enumerate(rels_by_type.items()):
        print(f"  Processing '{pred_name}' ({len(pred_rels):,} relationships)...")
        
        # Create relationships in smaller batches
        batch_size = 500
        
        for i in range(0, len(pred_rels), batch_size):
            batch = pred_rels[i:i + batch_size]
            
            # Build a single query for this batch
            query_parts = []
            for idx, (source, target) in enumerate(batch):
                safe_source = source.replace("'", "\\'")
                safe_target = target.replace("'", "\\'")
                query_parts.append(
                    f"MATCH (s{idx}:Resource {{uri: '{safe_source}'}}) "
                    f"MATCH (o{idx}:Resource {{uri: '{safe_target}'}}) "
                    f"CREATE (s{idx})-[:`{pred_name}`]->(o{idx})"
                )
            
            query = " ".join(query_parts)
            
            try:
                graph.query(query)
                total_rels_created += len(batch)
            except:
                # Fallback to individual creation for this batch
                for source, target in batch:
                    try:
                        safe_source = source.replace("'", "\\'")
                        safe_target = target.replace("'", "\\'")
                        graph.query(f"""
                        MATCH (s:Resource {{uri: '{safe_source}'}})
                        MATCH (o:Resource {{uri: '{safe_target}'}})
                        CREATE (s)-[:`{pred_name}`]->(o)
                        """)
                        total_rels_created += 1
                    except:
                        failed_rels += 1
                        pass
            
            # Show progress every 50,000 relationships
            if total_rels_created % 50000 == 0:
                elapsed = time.time() - rel_start
                rate = total_rels_created / elapsed if elapsed > 0 else 0
                print(f"    Created {total_rels_created:,}/{len(relationships):,} "
                      f"({rate:.0f} rels/sec)")
    
    rel_time = time.time() - rel_start
    
    total_time = time.time() - total_start
    
    # Final statistics
    stats = {
        'total_triples_in_file': total_triples,
        'triples_loaded': count,
        'nodes_created': total_nodes_created,
        'relationships_created': total_rels_created,
        'nodes_failed': failed_nodes,
        'relationships_failed': failed_rels,
        'file': rdf_file_path,
        'graph_name': graph_name,
        'elapsed_seconds': total_time,
        'nodes_per_second': total_nodes_created / total_time if total_time > 0 else 0,
        'relationships_per_second': total_rels_created / total_time if total_time > 0 else 0,
        'parse_time': parse_time,
        'process_time': process_time,
        'node_load_time': node_time,
        'relationship_load_time': rel_time
    }
    
    # Print summary
    print(f"\n{'='*70}")
    print("🎉 LOADING COMPLETE!")
    print(f"{'='*70}")
    print(f"⏱️  Total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
    print(f"📄 File: {os.path.basename(rdf_file_path)}")
    print(f"📊 Triples parsed: {total_triples:,}")
    print(f"📥 Triples loaded: {count:,}")
    print(f"🔵 Nodes created: {total_nodes_created:,}")
    print(f"🔗 Relationships created: {total_rels_created:,}")
    if failed_nodes > 0 or failed_rels > 0:
        print(f"⚠️  Failed: {failed_nodes} nodes, {failed_rels} relationships")
    print(f"📈 Performance:")
    print(f"   • Nodes/sec: {stats['nodes_per_second']:.1f}")
    print(f"   • Relationships/sec: {stats['relationships_per_second']:.1f}")
    print(f"   • Parse time: {parse_time:.1f}s")
    print(f"   • Node load time: {node_time:.1f}s")
    print(f"   • Relationship load time: {rel_time:.1f}s")
    print(f"{'='*70}")
    
    return stats

def load_rdf_to_falkordb(rdf_file_path, graph_name='wordnet', host=None, port=None, sample_size=None):
    """Compatibility wrapper"""
    return load_rdf_to_falkordb_optimized(rdf_file_path, graph_name, host, port, sample_size)

if __name__ == "__main__":
    # Test with a small sample first to verify everything works
    print("🔍 Testing with small sample...")
    result = load_rdf_to_falkordb('data/english-wordnet-2024.ttl', sample_size=1000)
    print(f"\n📋 Test result: {result}")
    
    if 'error' not in result:
        print("\n✅ Test successful! Ready to load full dataset.")
        response = input("Load full dataset? (y/n): ")
        if response.lower() == 'y':
            print("\n🚀 Starting full dataset load...")
            full_result = load_rdf_to_falkordb('data/english-wordnet-2024.ttl')
            print(f"\n📋 Full load result: {full_result}")