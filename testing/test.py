import concurrent.futures
import subprocess

# Define the list of hosts
hosts = ["pm3d-dev.local"]

source_path = ""
destination_path = "/home/hayden"
user = "ubuntu" 

def sync_host(host):
    command = [
        "rsync", "-avz",
        source_path,
        f"{user}@{host}:{destination_path}"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully synced with {host}")
    else:
        print(f"Failed to sync with {host}: {result.stderr}")

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(sync_host, host) for host in hosts]
        for future in concurrent.futures.as_completed(futures):
            future.result() 

if __name__ == "__main__":
    main()
