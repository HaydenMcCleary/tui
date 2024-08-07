import csv 
import subprocess
from datetime import timedelta
from dateutil import parser

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def is_outofdate(deployment_sync_date,todays_date):
    date1 = parser.parse(deployment_sync_date)
    date2 = parser.parse(todays_date)
    time_difference = abs(date2 - date1)

    # Check if the time difference is over 10 days
    if time_difference >= timedelta(hours=240):
        return True
    return False


column_one = []
column_two = []
column_three = []

date = subprocess.check_output("date").decode('utf-8').strip()

print("Welcome, current deployments along with their lest succesful sync are listed below.\n")
print(f"{bcolors.FAIL}Red tag means that sync is out of date{bcolors.ENDC}, {bcolors.WARNING}yellow tag means the system logs indicate the system is unhealthy{bcolors.ENDC}\n")
column_one.append(f"{bcolors.HEADER}Deployments{bcolors.ENDC}")
column_two.append(f"{bcolors.HEADER}Last Succesful Sync{bcolors.ENDC}")
column_three.append(f"{bcolors.HEADER}Date{bcolors.ENDC}")
with open("hosts_that_need_to_be_synced.csv", mode='r') as infile:
    reader = csv.reader(infile)
    next(reader)
    for rows in reader:
        
        if is_outofdate(date, rows[1]):
            column_one.append(f"{bcolors.FAIL}{rows[0]}{bcolors.ENDC}")
            column_two.append(f"{bcolors.FAIL}{rows[1]}{bcolors.ENDC}")
        else:
            column_one.append(f"{bcolors.OKGREEN}{rows[0]}{bcolors.ENDC}")
            column_two.append(f"{bcolors.OKGREEN}{rows[1]}{bcolors.ENDC}")
        column_three.append(f"{date}")
        
for string_1, string_2, string_3 in zip(column_one, column_two, column_three):
    print(f"{string_1:<40s} {string_2:<60s} {string_3:<40s}")




