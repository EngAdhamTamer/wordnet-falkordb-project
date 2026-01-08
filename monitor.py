# monitor.py
import time
import subprocess
import psutil

def monitor_falkordb():
    print("Monitoring FalkorDB performance...")
    print("-" * 60)
    
    while True:
        try:
            # Get Docker container stats
            result = subprocess.run(
                ['docker', 'stats', 'falkordb', '--no-stream', '--format', 
                 '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}'],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                print(f"\n{time.strftime('%H:%M:%S')} - FalkorDB Stats:")
                print(result.stdout.strip())
            
            # Get system memory
            mem = psutil.virtual_memory()
            print(f"System Memory: {mem.percent}% used")
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_falkordb()