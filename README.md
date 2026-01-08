# WordNet FalkorDB Knowledge Graph Project

Complete solution for loading Open English WordNet RDF data into FalkorDB graph database with Docker containerization.

## 🎯 Project Overview

This project implements a complete pipeline for:
1. Loading WordNet RDF (Turtle format) into FalkorDB
2. Generic RDF loader function that works with any RDF file
3. JSON comparison tool for WordNet versions
4. Fully containerized with Docker

## ✨ Features

- **Generic RDF Loader**: Load any RDF/Turtle file into FalkorDB
- **Optimized Performance**: Batch processing with progress tracking
- **Docker Support**: Complete containerized solution
- **Error Handling**: Robust error handling and recovery
- **Progress Monitoring**: Real-time loading statistics
- **JSON Comparison**: Compare WordNet versions (requires manual JSON download)

## 📊 Performance

Successfully loaded complete WordNet 2024 dataset:
- **3,854,624 triples** parsed and loaded
- **1,627,356 unique nodes** created
- **3,854,624 relationships** established
- **88 minutes** total loading time
- **730 relationships/second** throughput

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- 8GB RAM recommended
- 5GB free disk space

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/EngAdhamTamer/wordnet-falkordb-project.git
cd wordnet-falkordb-project
```

2. **Place your RDF file:**
   - Download `english-wordnet-2024.ttl` from [en-word.net](https://en-word.net/)
   - Place it in the `data/` folder

3. **Start the system:**
```bash
docker-compose up --build
```

The system will:
- Start FalkorDB on port 6379
- Automatically load the RDF data
- Save results to the graph database

### Accessing FalkorDB

- **Database**: `localhost:6379`
- **FalkorDB Studio**: `http://localhost:3000` (web interface)

## 📁 Project Structure
```
wordnet-falkordb-project/
├── rdf_loader.py          # Generic RDF to FalkorDB loader
├── json_compare.py        # JSON version comparison tool
├── main.py               # Main execution script
├── requirements.txt      # Python dependencies
├── Dockerfile            # Application container
├── docker-compose.yml    # Multi-container setup
├── README.md            # This file
├── .gitignore           # Git ignore rules
└── data/                # Data files (not in git)
    └── english-wordnet-2024.ttl
```

## 🔧 Usage

### Option 1: Using Docker (Recommended)
```bash
# Start everything
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Run Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Start FalkorDB
docker run -d -p 6379:6379 --name falkordb falkordb/falkordb:latest

# Run the loader
python main.py
```

### Using the RDF Loader Programmatically
```python
from rdf_loader import load_rdf_to_falkordb

# Load complete dataset
stats = load_rdf_to_falkordb('data/english-wordnet-2024.ttl')

# Load sample (for testing)
stats = load_rdf_to_falkordb('data/english-wordnet-2024.ttl', sample_size=10000)

print(f"Loaded {stats['nodes_created']} nodes")
print(f"Created {stats['relationships_created']} relationships")
```

## 🔍 Querying the Data

Once loaded, query using Cypher:
```bash
# Connect to FalkorDB
docker exec -it falkordb redis-cli

# Count nodes
GRAPH.QUERY wordnet "MATCH (n) RETURN count(n)"

# Find a word
GRAPH.QUERY wordnet "MATCH (n:Resource) WHERE n.name CONTAINS 'happy' RETURN n LIMIT 10"

# Find relationships
GRAPH.QUERY wordnet "MATCH (n)-[r]->(m) RETURN type(r), count(r)"
```

## 📋 Task Completion Status

| Task | Status | Implementation |
|------|--------|----------------|
| 1. Download OEWN RDF 2024 | ✅ | Client provides file |
| 2. Create FalkorDB docker container | ✅ | `docker-compose.yml` |
| 3. Generic RDF loader function | ✅ | `rdf_loader.py` |
| 4. JSON comparison (2025 vs 2024) | ✅ | `json_compare.py` |

## 🗂️ JSON Comparison Feature

The project includes a JSON comparison tool for WordNet versions.

**Note**: JSON files must be downloaded manually from [globalwordnet/english-wordnet](https://github.com/globalwordnet/english-wordnet)
```bash
# Place JSON files in data/ folder:
# - data/english-wordnet-2024.json
# - data/english-wordnet-2025.json

# Run comparison
python json_compare.py
```

The tool will generate `data/difference.json` containing:
- Added synsets
- Removed synsets
- Modified synsets
- Statistics

## 🛠️ Configuration

### Environment Variables
```bash
FALKORDB_HOST=localhost    # FalkorDB hostname
FALKORDB_PORT=6379         # FalkorDB port
```

### Docker Resources

In `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 6G
      cpus: '2.0'
```

## 📈 Performance Optimization

The loader includes several optimizations:
- **Batch processing**: 5000 nodes per batch
- **Index creation**: URI-based indexing for fast lookups
- **Relationship grouping**: Groups by predicate type
- **Progress tracking**: Real-time statistics
- **Error recovery**: Graceful handling of malformed data

## 🐛 Troubleshooting

### Docker Connection Issues
```bash
# Restart Docker Desktop
# Then:
docker-compose down
docker-compose up --build
```

### Memory Issues
Increase Docker memory in Docker Desktop settings (recommend 8GB+)

### Slow Loading
This is normal - complete dataset takes ~90 minutes. Monitor progress in logs.

## 📝 Requirements

- Python 3.8+
- Docker Desktop
- 8GB RAM (recommended)
- 5GB disk space

**Python packages** (auto-installed):
```
falkordb==1.0.8
rdflib==7.0.0
requests==2.31.0
```

## 🤝 Contributing

This is a project submission for NLP/Knowledge Graph work.

## 📄 License

MIT License

## 👤 Author

**Adham Tamer**
- GitHub: [@EngAdhamTamer](https://github.com/EngAdhamTamer)

## 🙏 Acknowledgments

- [Open English WordNet](https://en-word.net/)
- [FalkorDB](https://www.falkordb.com/)
- [Global WordNet Association](http://globalwordnet.org/)

---

**Project Status**: ✅ Complete and tested with WordNet 2024 dataset