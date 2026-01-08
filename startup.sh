#!/bin/bash

# Start FalkorDB with optimized configuration
echo "Starting FalkorDB with optimized configuration..."
docker-compose down
docker-compose up -d

# Wait for FalkorDB to be ready
echo "Waiting for FalkorDB to start..."
until docker exec falkordb redis-cli ping | grep -q "PONG"; do
    sleep 1
done

echo "FalkorDB is ready!"

# Optional: Disable persistence for faster import
echo "Configuring FalkorDB for fast import..."
docker exec falkordb redis-cli CONFIG SET SAVE ""
docker exec falkordb redis-cli CONFIG SET APPENDONLY no

# Run the RDF loader
echo "Starting RDF loader..."
python main.py

# Re-enable persistence after import
echo "Re-enabling persistence..."
docker exec falkordb redis-cli CONFIG SET SAVE "900 1 300 10 60 10000"
docker exec falkordb redis-cli CONFIG SET APPENDONLY yes
docker exec falkordb redis-cli BGSAVE

echo "Import complete!"