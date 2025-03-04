import psutil
import time
from datetime import datetime

def get_process_info():
    """
    Retrieves and prints information about all running processes,
    including memory usage and runtime.
    """
    print(f"{'PID':<10} {'Name':<30} {'Memory (MB)':<15} {'Runtime':<20}")
    print("-" * 80)

    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'create_time']):
        try:
            # Extract process details
            pid = proc.info['pid']
            name = proc.info['name'] or "Unknown"
            memory_info = proc.info['memory_info']
            create_time = proc.info['create_time']

            # Calculate memory usage in MB
            memory_mb = memory_info.rss / (1024 * 1024)  # Resident Set Size in MB

            # Calculate runtime
            runtime_seconds = time.time() - create_time
            runtime = str(datetime.utcfromtimestamp(runtime_seconds)).split('.')[0]

            # Print process details
            print(f"{pid:<10} {name:<30} {memory_mb:<15.2f} {runtime:<20}")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Handle exceptions for processes that no longer exist or cannot be accessed
            continue

if __name__ == "__main__":
    print("Monitoring Background Processes...\n")
    while True:
        get_process_info()
        print("\nRefreshing in 5 seconds...\n")
        time.sleep(5)
