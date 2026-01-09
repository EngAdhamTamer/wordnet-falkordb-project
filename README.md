# FalkorDB WordNet Knowledge Graph Project

Complete implementation of a knowledge graph system for Open English WordNet using FalkorDB.

## ✅ Completed Tasks

### Task 1: Download Open English Wordnet RDF 2024
- **File**: `data/english-wordnet-2024.ttl`
- **Source**: https://en-word.net/
- **Size**: ~200MB (3.8 million triples)

### Task 2: FalkorDB Docker Container
- **Image**: `falkordb/falkordb:edge`
- **Ports**: 6379 (database), 3000 (web UI)
- **Configuration**: `docker-compose.yml`

### Task 3: Generic RDF Loader
- **File**: `generic_rdf_loader.py`
- **Function**: `load_any_rdf_to_falkordb()` - works with ANY RDF file
- **Formats**: .ttl, .rdf, .xml, .jsonld, .nt, .n3
- **Features**: Auto-format detection, progress tracking, batch processing

### Task 4: JSON Comparison Tool
- **File**: `compare_wordnet_years.py`
- **Function**: `compare_wordnet_files()` - compares two JSON files
- **Output**: Added, removed, and modified entries with statistics

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/EngAdhamTamer/wordnet-falkordb-project.git
cd wordnet-falkordb-project
pip install -r requirements.txt

# Download WordNet RDF from https://en-word.net/
# Place it in: data/english-wordnet-2024.ttl

# Verify tasks
python complete_task.py

# Start FalkorDB
docker-compose up -d

# Load WordNet
python run_full.py       # Full dataset (1-2 hours)
# OR
python generic_rdf_loader.py  # Sample (5000 triples)

# Access web interface
# Open: http://localhost:3000
```

## 📁 Project Structure

```
wordnet-falkordb-project/
├── data/
│   └── english-wordnet-2024.ttl (download from en-word.net)
├── generic_rdf_loader.py    # Task 3: RDF loader
├── run_full.py              # Full dataset loader
├── compare_wordnet_years.py # Task 4: JSON comparison
├── complete_task.py         # Task verification
├── docker-compose.yml       # Docker configuration
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🔧 Usage

### Load RDF Data

**Load full WordNet:**
```bash
python run_full.py
```

**Load sample for testing:**
```bash
python generic_rdf_loader.py
```

**Use in Python:**
```python
from generic_rdf_loader import load_any_rdf_to_falkordb

# Load any RDF file
result = load_any_rdf_to_falkordb(
    rdf_file_path='data/english-wordnet-2024.ttl',
    graph_name='wordnet',
    sample_size=None  # None = load all
)
```

### Compare JSON Files

```bash
python compare_wordnet_years.py \
  data/wordnet-2024.json \
  data/wordnet-2025.json \
  -o data/differences.json
```

### Query the Database

Open http://localhost:3000 and run:

```cypher
# View all relationship types
MATCH ()-[r]->() 
RETURN type(r), count(r) 
ORDER BY count(r) DESC

# Explore hypernyms
MATCH (s:Resource)-[r:hypernym]->(t:Resource) 
RETURN s, r, t 
LIMIT 20

# Find a word
MATCH (n:Resource)-[r]-(m:Resource)
WHERE n.uri CONTAINS 'happy'
RETURN n, r, m
LIMIT 50
```

## 📊 Performance

- **Sample Load (5K triples)**: ~30-60 seconds
- **Full Load (3.8M triples)**: ~1-2 hours
- **System**: 8GB RAM recommended
- **Relationship Types**: 8 types (hypernym, hyponym, definition, example, etc.)

## 🔍 Troubleshooting

**Docker not starting:**
```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

**Connection refused:**
```bash
# Test connection
docker exec falkordb-wordnet redis-cli ping
```

**File not found:**
```bash
# Make sure you're in the project directory
ls data/english-wordnet-2024.ttl
```

**Out of memory:**
- Open Docker Desktop → Settings → Resources
- Set Memory to 8GB, CPU to 2+ cores
- Restart Docker

## 💡 Features

- **Generic RDF Loader**: Works with any RDF file format
- **Auto-format Detection**: Automatically detects file format
- **Progress Tracking**: Real-time progress during loading
- **Batch Processing**: Optimized for large datasets
- **Error Handling**: Graceful fallbacks for failed operations
- **Web Interface**: FalkorDB Studio for visualization
- **JSON Comparison**: Detailed diff analysis between versions

## 📝 Requirements

- Python 3.8+
- Docker Desktop
- 8GB RAM (for full dataset)
- 5GB disk space

## 🎯 All Tasks Completed

✅ Task 1: WordNet RDF download instructions  
✅ Task 2: FalkorDB Docker container  
✅ Task 3: Generic RDF loader function  
✅ Task 4: JSON comparison tool  

## 📞 Support

Run `python complete_task.py` to verify all tasks are complete.

For Docker issues, check logs: `docker-compose logs`

## 📄 License

MIT License

---

**Technologies**: FalkorDB, Python 3.11, Docker, RDFLib  
**Repository**: https://github.com/EngAdhamTamer/wordnet-falkordb-project  
**Date**: January 2026