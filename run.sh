#!/bin/bash
# run.sh - Client deployment script

echo "Setting up WordNet FalkorDB Project..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Build and start services
echo "Building and starting containers..."
docker-compose down
docker-compose up -d --build

echo "Waiting for FalkorDB to be ready..."
until docker exec falkordb redis-cli ping | grep -q "PONG"; do
    sleep 1
done

echo "FalkorDB is ready!"

# Run the loader
echo "Starting WordNet RDF loader..."
docker-compose exec -T wordnet-loader python main.py

echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo "FalkorDB is running on: localhost:6379"
echo "FalkorDB Studio (web UI): http://localhost:3000"
echo ""
echo "To query the database:"
echo "  docker exec falkordb redis-cli GRAPH.QUERY wordnet 'MATCH (n) RETURN count(n)'"
echo ""
echo "To stop: docker-compose down"
echo "To restart loader: docker-compose restart wordnet-loader"