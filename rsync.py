import subprocess
import csv
from datetime import timedelta
from dateutil import parser
import pandas as pd

# ------------------------------------- #
# CHECK HOST LAST SYNC                  #
# ------------------------------------- #

'''

    In order to prevent unnecessary backups/overloading the host we will only try and sync logs that have
    gone unsynced for over 2 hours

    To do this every time cron runs the first thing we do is grab date and compare it to the last backup date
    hosts_that_need_to_be_synced.csv. If a succesful rsync is performed than we will update the csv file with the appropriate 
    date

    ex:

    date

    Tue 30 Jul 2024 01:50:26 PM EDT

    if out of date and rsync is succesful hosts_that_need_to_be_synced.csv will be updated to something like this

    BARK, Tue 30 Jul 2024 01:50:26 PM EDT

    This update will be performed in update_csv_file

'''

def check_host_last_sync(hostname_csv, todays_date):

    outofdate_hosts = []

    # Grab hostnames and their corresponding last succesful rsync
    with open(hostname_csv, mode='r') as infile:
        reader = csv.reader(infile)
        next(reader)
        mydict = {rows[0]:rows[1] for rows in reader}

    # See if we are up to date, if not store it in outofdate_hosts
    for hostname, date in mydict.items():

        date1 = parser.parse(date)
        date2 = parser.parse(todays_date)
        time_difference = abs(date2 - date1)

        # Check if the time difference is at least over 2 hours
        if time_difference >= timedelta(hours=2):
            outofdate_hosts.append(hostname)

    return outofdate_hosts

# ------------------------------------- #
# CHECK HOST CONNECTIONS                #
# ------------------------------------- #

'''

    Ping the hosts (passed from func check_host_last_sync), if ping time is < 100 ms try to sync

    ex: 

    ping -c 4 google.com 

    64 bytes from ww-in-f138.1e100.net (142.251.167.138): icmp_seq=1 ttl=104 time=21.4 ms
    64 bytes from ww-in-f138.1e100.net (142.251.167.138): icmp_seq=2 ttl=104 time=21.5 ms
    64 bytes from ww-in-f138.1e100.net (142.251.167.138): icmp_seq=3 ttl=104 time=23.4 ms
    64 bytes from ww-in-f138.1e100.net (142.251.167.138): icmp_seq=4 ttl=104 time=19.1 ms

    --- google.com ping statistics ---
    4 packets transmitted, 4 received, 0% packet loss, time 3005ms
    rtt min/avg/max/mdev = 19.094/21.333/23.360/1.512 ms

    extract avg ==> 21.333 ms ==> store this host to perform a concurrent sync later

'''

def ping_hosts(hostnames):
    connected_hosts = []
    for host in hostnames:
        try:
            # Ping and capture outputs
            result = subprocess.run(["ping", "-c", "4", f"{host}.com"], capture_output=True, text=True, timeout=10)
            output = result.stdout
            
            # Check if the ping was successful and extract the ping time
            if result.returncode == 0:
                # Extract the average ping time from the output
                avg_ping_time = None
                for line in output.splitlines():
                    if "min/avg/max" in line:
                        avg_ping_time = float(line.split("/")[4])
                        break

                # Print the ping result and average ping time
                print(f"Host: {host}, Avg Ping Time: {avg_ping_time} ms")
                
                # Check if the average ping time is less than 100 ms, if so add it to connected hosts
                if avg_ping_time is not None and avg_ping_time < 100:
                    print(f"Adding {host} for sync")
                    connected_hosts.append(host)
                else:
                    print(f"Skipping{host} due to high ping time.")
            else:
                print(f"Failed to ping {host}.")
        except subprocess.TimeoutExpired:
            print(f"Ping to {host} timed out.")
        except Exception as e:
            print(f"An error occurred while pinging {host}: {e}")

    return connected_hosts

# ------------------------------------- #
# PERFORM RSYNC ON APPROPRIATE HOSTS    #
# ------------------------------------- #

'''

    Peform a multithread rsync with all appropriate hosts, appropriate hosts determined by ping time (from func ping_hosts)

'''

def sync_with_hosts(hostnames):
    for host in hostnames:
        print(host)

# ------------------------------------- #
# DELETE BACKUP MONGODB OFF OF HOSTS    #
# ------------------------------------- #

'''

    If the rsync is determined to be successful (by func sync_with_hosts) delete the backup database on the host machine 

'''

def delete_backup_off_host(hostname):
    pass


# ------------------------------------- #
# UPDATE OUR CSV FILE                   #
# ------------------------------------- #

'''

    This function servers to keep our CSV records up to date. If an rsync is succesfully performed the csv will be updated to reflect that
    because of this function.

'''

def update_csv_file(hostname_csv, todays_date, successful_hosts):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(hostname_csv)
    for host in successful_hosts:
        df.loc[df['host'] == host, 'date'] = todays_date
    
    df.to_csv(hostname_csv, index=False)


# ------------------------------------- #
# MAIN                                  #
# ------------------------------------- #

if __name__ == "__main__":

    date = subprocess.check_output("date").decode('utf-8').strip()
    
    # CHECK HOST LAST SYNC   
    hosts = check_host_last_sync("hosts_that_need_to_be_synced.csv", date)

    # CHECK HOST CONNECTIONS      
    connected_hosts = ping_hosts(hosts)
    
    # PERFORM RSYNC ON APPROPRIATE HOSTS 
    succesful_hosts = sync_with_hosts(connected_hosts)

    # UPDATE OUR CSV FILE
    update_csv_file("hosts_that_need_to_be_synced.csv", date, succesful_hosts)

    # DELETE BACKUP MONGODB OFF OF HOSTSS 
    delete_backup_off_host(succesful_hosts)