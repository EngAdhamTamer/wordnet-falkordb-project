@echo off
echo Starting FalkorDB with optimized configuration...
docker-compose down
docker-compose up -d

echo Waiting for FalkorDB to start...
:wait
docker exec falkordb redis-cli ping | findstr "PONG"
if errorlevel 1 (
    timeout /t 1 /nobreak > nul
    goto wait
)

echo FalkorDB is ready!
echo Configuring FalkorDB for fast import...
docker exec falkordb redis-cli CONFIG SET SAVE ""
docker exec falkordb redis-cli CONFIG SET APPENDONLY no

echo Starting RDF loader...
python main.py

echo Re-enabling persistence...
docker exec falkordb redis-cli CONFIG SET SAVE "900 1 300 10 60 10000"
docker exec falkordb redis-cli CONFIG SET APPENDONLY yes
docker exec falkordb redis-cli BGSAVE

echo Import complete!