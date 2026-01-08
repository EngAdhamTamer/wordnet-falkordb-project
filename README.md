# FalkorDB WordNet Knowledge Graph Project

## 📋 Project Overview
Complete implementation of a knowledge graph system for Open English WordNet using FalkorDB. This project fulfills all client requirements for loading, querying, and comparing WordNet data.

## ✅ Completed Tasks

### Task 1: Download Open English Wordnet RDF 2024
- **Status**: ✅ Completed
- **Source**: https://en-word.net/
- **File**: `data/english-wordnet-2024.ttl`
- **Size**: ~200MB (3.8 million triples)
- **Format**: Turtle RDF

### Task 2: Create FalkorDB Docker Container
- **Status**: ✅ Completed
- **Image**: `falkordb/falkordb:edge`
- **Ports**: 6379 (database), 3000 (web interface)
- **Memory**: Optimized for 8GB RAM
- **Features**: Health checks, persistence, optimized configuration

### Task 3: Create Generic RDF Loader Function
- **Status**: ✅ Completed
- **File**: `generic_rdf_loader.py`
- **Features**:
  - Generic function `load_any_rdf_to_falkordb()` that works with ANY RDF file
  - Supports multiple RDF formats (.ttl, .rdf, .xml, .jsonld, .nt, .n3)
  - Auto-detects file format from extension
  - Relationship type cleaning for FalkorDB compatibility
  - Progress tracking and error handling
  - Optimized batch processing
  - Successfully tested with WordNet (creates all relationship types)

### Task 4: Compare WordNet JSON Files
- **Status**: ✅ Completed
- **File**: `compare_wordnet_years.py`
- **Features**:
  - Function `compare_wordnet_files(file1, file2, output)` compares two JSON files
  - Identifies added entries (in file2 but not in file1)
  - Identifies removed entries (in file1 but not in file2)
  - Identifies modified entries (changed between versions)
  - Generates detailed JSON difference report
  - Provides comprehensive statistics
  - Command-line interface included

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker Desktop
- 8GB RAM (for full dataset)
- 5GB free disk space

### Installation

```bash
# Clone the project
git clone <repository-url>
cd wordnet-falkordb-project

# Install Python dependencies
pip install -r requirements.txt
```

### Running the Complete System

**Step 1: Verify All Tasks Completed**
```bash
python complete_task.py
```

**Step 2: Start FalkorDB**
```bash
docker-compose up -d
```

**Step 3: Load WordNet Data**
```bash
# Option A: Load a sample (5000 triples, fast for testing)
python generic_rdf_loader.py

# Option B: Load full dataset (3.8M triples, takes 1-2 hours)
python run_full.py
```

**Step 4: Access Web Interface**

Open browser to: http://localhost:3000

## 📁 Project Structure

```
wordnet-falkordb-project/
├── data/                          # Data files
│   ├── english-wordnet-2024.ttl   # WordNet RDF dataset (3.8M triples)
│   └── *.json                     # JSON files for comparison (optional)
├── generic_rdf_loader.py          # Task 3: Generic RDF loader
├── run_full.py                    # Helper script to load full dataset
├── compare_wordnet_years.py       # Task 4: JSON comparison tool
├── complete_task.py               # Task verification script
├── docker-compose.yml             # Docker configuration
├── Dockerfile                     # Application container
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🔧 Detailed Usage

### Task 1: Download WordNet RDF

Download the RDF file from https://en-word.net/ and place it in the `data/` folder:

```bash
# Expected file location
data/english-wordnet-2024.ttl
```

### Task 2: Start FalkorDB Docker Container

**Using docker-compose (recommended):**
```bash
# Start container
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f falkordb

# Stop container
docker-compose down
```

**Using direct Docker command:**
```bash
docker run -d --name falkordb-wordnet \
  --memory=8g \
  -p 6379:6379 \
  -p 3000:3000 \
  falkordb/falkordb:edge
```

**Verify it's running:**
```bash
# Test connection
docker exec falkordb-wordnet redis-cli ping
# Should return: PONG
```

### Task 3: Load RDF Data Using Generic Loader

**Option A: Load sample (recommended for testing):**
```bash
# Run the generic loader directly (loads 5000 triples by default)
python generic_rdf_loader.py
```

**Option B: Load full dataset (3.8M triples, takes 1-2 hours):**
```bash
# Use the dedicated full load script
python run_full.py
```

**Option C: Python API usage:**
```python
from generic_rdf_loader import load_any_rdf_to_falkordb

# Load sample (5000 triples for testing)
result = load_any_rdf_to_falkordb(
    rdf_file_path='data/english-wordnet-2024.ttl',
    graph_name='wordnet_test',
    sample_size=5000
)

print(f"Nodes created: {result['nodes_created']:,}")
print(f"Relationships created: {result['relationships_created']:,}")
```

**Load full dataset programmatically:**
```python
# Load complete WordNet (takes 1-2 hours)
result = load_any_rdf_to_falkordb(
    rdf_file_path='data/english-wordnet-2024.ttl',
    graph_name='wordnet_full',
    sample_size=None  # None = load all
)
```

**Generic loader works with ANY RDF file:**
```python
# Works with any RDF format
load_any_rdf_to_falkordb('your-ontology.ttl')
load_any_rdf_to_falkordb('your-data.rdf')
load_any_rdf_to_falkordb('your-file.jsonld')
load_any_rdf_to_falkordb('your-triples.nt')
```

**Features:**
- Auto-detects file format from extension
- Cleans relationship names for FalkorDB compatibility
- Shows progress during loading
- Creates indexes for fast queries
- Handles errors gracefully

### Task 4: Compare WordNet JSON Files

**Command-line usage:**
```bash
# Compare two JSON files
python compare_wordnet_years.py \
  data/wordnet-2024.json \
  data/wordnet-2025.json \
  -o data/differences.json
```

**Python usage:**
```python
from compare_wordnet_years import compare_wordnet_files

# Compare files programmatically
result = compare_wordnet_files(
    file1_path='data/wordnet-2024.json',  # Older version
    file2_path='data/wordnet-2025.json',  # Newer version
    output_path='data/differences.json'
)

# Access results
print(f"Added entries: {result['statistics']['added_entries']}")
print(f"Removed entries: {result['statistics']['removed_entries']}")
print(f"Modified entries: {result['statistics']['modified_entries']}")
```

**Output structure:**
```json
{
  "comparison_info": {
    "file1": "wordnet-2024.json",
    "file2": "wordnet-2025.json",
    "comparison_date": "2025-01-08T...",
    "operation": "file2 - file1 (newer minus older)"
  },
  "statistics": {
    "total_file1_entries": 120000,
    "total_file2_entries": 125000,
    "added_entries": 5200,
    "removed_entries": 200,
    "modified_entries": 1500
  },
  "added": [...],
  "removed": [...],
  "modified": [...]
}
```

### Verify All Tasks

Run the complete verification:
```bash
python complete_task.py
```

Expected output:
```
======================================================================
🎯 FALKORDB WORDNET KNOWLEDGE GRAPH - COMPLETE TASK
======================================================================

✅ Task 1: COMPLETED
✅ Task 2: COMPLETED
✅ Task 3: COMPLETED
✅ Task 4: COMPLETED

🎯 Completed 4/4 tasks

✨ ALL TASKS COMPLETED SUCCESSFULLY!
```

## 🌐 Web Interface (FalkorDB Studio)

Access at: **http://localhost:3000**

### Connecting to Your Graph

1. Open http://localhost:3000 in your browser
2. You should auto-connect to localhost:6379
3. Select your graph from the dropdown (e.g., "wordnet_test" or "wordnet_full")
4. Use the query editor to run Cypher queries

### Sample Queries

**View all relationship types:**
```cypher
MATCH ()-[r]->() 
RETURN type(r) AS relationship_type, count(r) AS count 
ORDER BY count DESC
```

**Explore WordNet hypernyms (word hierarchies):**
```cypher
MATCH (s:Resource)-[r:hypernym]->(t:Resource) 
WHERE s.name IS NOT NULL AND t.name IS NOT NULL
RETURN s.name AS word, t.name AS broader_term 
LIMIT 20
```

**Find a specific word:**
```cypher
MATCH (n:Resource)-[r]-(m:Resource)
WHERE n.name CONTAINS 'happy'
RETURN n, type(r) AS relationship, m
LIMIT 50
```

**Count all nodes and relationships:**
```cypher
MATCH (n) RETURN count(n) AS total_nodes
```

```cypher
MATCH ()-[r]->() RETURN count(r) AS total_relationships
```

**See word definitions:**
```cypher
MATCH (s:Resource)-[r:definition]->(d:Resource)
WHERE d.name IS NOT NULL
RETURN s.name AS synset, d.name AS definition
LIMIT 20
```

**View usage examples:**
```cypher
MATCH (s:Resource)-[r:example]->(e:Resource)
WHERE e.name IS NOT NULL
RETURN s.name AS synset, e.name AS example
LIMIT 20
```

## 📊 Performance & Statistics

### Load Performance
- **Sample Load (5000 triples)**: ~30-60 seconds
- **Medium Load (100K triples)**: ~10-15 minutes
- **Full Load (3.8M triples)**: ~1-2 hours
- **Throughput**: Varies by hardware (typically 500-1000 triples/sec)

### System Requirements
- **Minimum**: 4GB RAM (for samples up to 100K triples)
- **Recommended**: 8GB RAM (for full 3.8M dataset)
- **Disk Space**: 5GB free space
- **CPU**: 2+ cores recommended

### Expected Database Statistics (Full Load)
- **Total Triples**: 3,854,624
- **Unique Nodes**: ~1.6 million
- **Total Relationships**: ~3.8 million
- **Relationship Types**: Multiple types including:
  - hypernym, hyponym (word hierarchies)
  - definition, example (word information)
  - writtenRep (written representations)
  - partOfSpeech (grammatical categories)
  - And many more...

## 🔍 Troubleshooting

### Common Issues

**1. "Connection refused" error**
```bash
# Check if Docker is running
docker ps

# Restart FalkorDB
docker-compose restart falkordb

# Check logs
docker-compose logs falkordb
```

**2. "File not found" error**
```bash
# Verify file exists
ls -la data/english-wordnet-2024.ttl

# Make sure you're in the project directory
pwd
# Should show: .../wordnet-falkordb-project
```

**3. Out of memory errors**
- Open Docker Desktop → Settings → Resources
- Increase Memory to 8GB
- Increase CPU to 2+ cores
- Click "Apply & Restart"

**4. Can't see all relationships in web interface**

This is **normal behavior**! FalkorDB Studio doesn't show all relationship types in the default visualization.

**Solution**: Use specific queries to view relationships:
```cypher
# See all relationship types
MATCH ()-[r]->() 
RETURN type(r), count(r) 
ORDER BY count(r) DESC

# View specific relationship type
MATCH (s)-[r:hypernym]->(t) 
RETURN s, r, t 
LIMIT 50
```

**5. Slow loading**
- This is normal for large datasets (3.8M triples)
- Use sample_size parameter for testing
- Monitor progress in console output
- Be patient - full load takes 1-2 hours

### Verification Commands

```bash
# Check Docker status
docker-compose ps

# Test database connection
docker exec falkordb-wordnet redis-cli ping

# View real-time logs
docker-compose logs -f

# Check loaded data (if you have check script)
# python check_data.py

# Monitor resource usage
docker stats falkordb-wordnet
```

## 📝 Technical Details

### Generic RDF Loader (Task 3)

**Key features:**
- **Function signature**: `load_any_rdf_to_falkordb(rdf_file_path, graph_name=None, host='localhost', port=6379, sample_size=None)`
- **Auto-format detection**: Automatically detects format from file extension
- **Relationship cleaning**: Converts URI predicates to valid FalkorDB relationship names
- **Batch processing**: Loads nodes and relationships in batches for efficiency
- **Progress tracking**: Real-time progress updates every 10,000 triples
- **Error handling**: Graceful fallbacks for parsing and loading errors
- **Statistics**: Returns detailed loading statistics

**Supported formats:**
- Turtle (.ttl)
- RDF/XML (.rdf, .xml)
- JSON-LD (.json, .jsonld)
- N-Triples (.nt)
- N3 (.n3)
- N-Quads (.nq)
- TriG (.trig)

### JSON Comparison Tool (Task 4)

**Key features:**
- **Function signature**: `compare_wordnet_files(file1_path, file2_path, output_path=None)`
- **Flexible input**: Works with different JSON structures (arrays, objects with synsets/entries)
- **ID-based matching**: Uses entry IDs for accurate comparison
- **Three-way diff**: Finds added, removed, and modified entries
- **Detailed changes**: Identifies specific field differences in modified entries
- **Statistics**: Comprehensive statistics about changes
- **JSON output**: Saves complete difference report

### Docker Configuration

**FalkorDB container settings:**
- Base image: `falkordb/falkordb:edge`
- Memory limit: 8GB
- CPU limit: 4 cores
- Ports: 6379 (database), 3000 (web UI)
- Health checks: Automatic monitoring
- Persistent storage: Volume for data persistence

## 💡 Best Practices

1. **Always test with samples first**: Use `sample_size=5000` before loading full dataset
2. **Monitor resources**: Keep an eye on Docker memory usage
3. **Use docker-compose**: Easier than manual Docker commands
4. **Save your queries**: Create a queries.txt file with useful queries
5. **Check logs**: If something fails, check Docker logs first
6. **Verify tasks**: Run `complete_task.py` before delivery

## 🎯 Project Delivery Checklist

- ✅ Task 1: WordNet RDF downloaded and in `data/` folder
- ✅ Task 2: FalkorDB Docker container configured in `docker-compose.yml`
- ✅ Task 3: Generic RDF loader implemented in `generic_rdf_loader.py`
- ✅ Task 4: JSON comparison tool implemented in `compare_wordnet_years.py`
- ✅ Task verification script (`complete_task.py`)
- ✅ Complete documentation (this README)
- ✅ All dependencies listed in `requirements.txt`
- ✅ Git ignore configured for data files

## 📞 Support

For issues:
1. Check this README's Troubleshooting section
2. Verify Docker is running: `docker ps`
3. Check logs: `docker-compose logs`
4. Run verification: `python complete_task.py`

## 📄 Files Included

### Core Task Files
- `generic_rdf_loader.py` - Task 3: Generic RDF loader function
- `run_full.py` - Helper script to load full WordNet dataset (3.8M triples)
- `compare_wordnet_years.py` - Task 4: JSON comparison function
- `complete_task.py` - Verifies all 4 tasks are completed

### Configuration Files
- `docker-compose.yml` - Docker services configuration
- `Dockerfile` - Application container (if needed)
- `requirements.txt` - Python dependencies
- `.gitignore` - Excludes data files from git

### Documentation
- `README.md` - This file

### Data Files (User-provided, not in git)
- `data/english-wordnet-2024.ttl` - WordNet RDF dataset
- `data/*.json` - JSON files for comparison (optional)

## 🎉 Project Status

**Status**: ✅ **All 4 tasks completed and verified**

**Completed Tasks:**
1. ✅ Downloaded Open English WordNet RDF 2024
2. ✅ Created FalkorDB Docker container configuration
3. ✅ Implemented generic RDF loader function
4. ✅ Implemented JSON comparison function

**Tested With:**
- WordNet 2024 RDF (3.8M triples)
- Sample loads (1K-100K triples)
- Full dataset load (verified working)

**Client Requirements**: ✅ Fully met

**Delivery Ready**: ✅ Yes

---

**Technologies Used:**
- FalkorDB (Graph Database)
- Python 3.11
- Docker & Docker Compose
- RDFLib (RDF parsing)
- Open English WordNet

**Project Date**: January 2026