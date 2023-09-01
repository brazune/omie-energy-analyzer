import argparse
import requests
from datetime import datetime, timedelta
from termcolor import colored
import os
import glob
import csv
from collections import defaultdict
import statistics
import matplotlib.pyplot as plt
import sys

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colored_timestamp = colored(timestamp, "white", attrs=["bold"])
    
    if message.startswith("INFO:"):
        colored_message = colored("INFO:", "green") + message[len("INFO:"):]
    elif message.startswith("WARN:"):
        colored_message = colored("WARN:", "yellow") + message[len("WARN:"):]
    elif message.startswith("ERROR:"):
        colored_message = colored("ERROR:", "red") + message[len("ERROR:"):]
    else:
        colored_message = message

    print(f"{colored_timestamp} {colored_message}")

def getOMIEFile(timestamp):
    try:
        datetime_obj = datetime.strptime(timestamp, "%Y-%m-%d")
        formatted_date = datetime_obj.strftime('%Y%m%d')
        generated_string = f'marginalpdbcpt_{formatted_date}.1'
        url = f'https://www.omie.es/pt/file-download?parents%5B0%5D=marginalpdbcpt&filename={generated_string}'
        log(f"INFO: retrieving {url}")
        response = requests.get(url)
        if response.status_code == 200:
            with open(generated_string, 'wb') as file:
                file.write(response.content)
                log(f'INFO: Saved {generated_string}')
        else:
            log(f'WARN: Failed to retrieve {generated_string}')
    except ValueError:
        log("ERROR: Invalid timestamp format. Please use YYYY-MM-DD.")

def initializeHistory():
    # Function to initialize history
    log("INFO: Initializing history. This might take a while...")
    current_year = datetime.now().year
    start_date = datetime(current_year, 1, 1)
    end_date = datetime.now() + timedelta(days=1)
    current_date = start_date

    while current_date <= end_date:
        formatted_date = current_date.strftime('%Y-%m-%d')
        getOMIEFile(formatted_date)
        current_date += timedelta(days=1)

def getDay(timestamp):
    try:
        date_obj = datetime.strptime(timestamp, "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        log(f"INFO: The day for {timestamp} is {day_name}.")
        getOMIEFile(timestamp)
    except ValueError:
        log("ERROR: Invalid timestamp format. Please use YYYY-MM-DD.")

def getTomorrow():
    tomorrow_date = datetime.now() + timedelta(days=1)
    formatted_date = tomorrow_date.strftime("%Y-%m-%d")
    getDay(formatted_date)

def analyze():
    # Check if any CSV files matching the criteria exist in the directory
    csv_files = glob.glob(os.path.join(args.dir, f'{args.file}'))
    if not csv_files:
        print(f"No files found matching the criteria {args.file} in path {args.dir}")
        sys.exit(1)  # Exit with an error code

    # Initialize a defaultdict to store hourly cost data
    hourly_costs = defaultdict(list)

    # Iterate through each CSV file in the directory
    for csv_file in glob.glob(os.path.join(args.dir, f'{args.file}')):
        with open(csv_file, 'r') as f:
            csv_reader = csv.reader(f, delimiter=';')
            
            for row in csv_reader:
                if len(row) == 7:  # Check if the row has the correct number of columns
                    year, month, day, hour, price, _, _ = row
                    
                    # Extract hour and price information
                    hour = int(hour)
                    price = float(price)
                    
                    # Store price in the corresponding hour slot
                    hourly_costs[hour].append(price)

    # Calculate average and standard deviation of prices for each hour
    hourly_statistics = {}
    for hour, prices in hourly_costs.items():
        avg_price = sum(prices) / len(prices)
        std_dev = statistics.stdev(prices) if len(prices) > 1 else 0
        hourly_statistics[hour] = (avg_price, std_dev)

    # Display results in text
    print("Average Costs and Standard Deviations by Hour:")
    for hour in sorted(hourly_statistics.keys()):
        avg_price, std_dev = hourly_statistics[hour]
        print(f"Hour: {hour:02d}, Average Cost: {avg_price:.2f}, Standard Deviation: {std_dev:.2f}")

    # Calculate overall average price
    all_prices = [price for hour_prices in hourly_costs.values() for price in hour_prices]
    overall_avg_price = sum(all_prices) / len(all_prices)
    print(f"\nOverall Average Price: {overall_avg_price:.2f}")

    if args.graph:
        # Sort hours based on average cost
        sorted_hours = sorted(hourly_statistics.keys(), key=lambda hour: hourly_statistics[hour][0])

        # Extract data for plotting
        avg_prices = [hourly_statistics[hour][0] for hour in sorted_hours]
        std_devs = [hourly_statistics[hour][1] for hour in sorted_hours]
        hour_labels = [f"{hour:02d}" for hour in sorted_hours]

        # Create a bar graph
        plt.figure(figsize=(10, 6))
        plt.bar(hour_labels, avg_prices, yerr=std_devs, capsize=5, color='blue', alpha=0.7)
        plt.xlabel('Hour')
        plt.ylabel('Average Cost')
        plt.title('Average Costs and Standard Deviations by Hour')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Show the graph
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="Parameterized functions example")
    parser.add_argument("--initialize-history", action="store_true", help="Retrieve OMIE price history for current year")
    parser.add_argument("--get-day", type=str, help="Retrieve the OMIE price file with a timestamp parameter (YYYY-MM-DD)")
    parser.add_argument("--get-tomorrow", action="store_true", help="Get OMIE price file for tomorrow")
    parser.add_argument('--analyze', help='Performs an analysis on the price files', action="store_true")
    parser.add_argument('--dir', default='.', help='Directory containing CSV files. Used only if --analyze is specified.')
    parser.add_argument('--file', default='*.csv', help='File extension of CSV files Used only if --analyze is specified.')
    parser.add_argument('--graph', help='Display a graph with the price analysis Used only if --analyze is specified.', action="store_true")
    global args 
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    if args.initialize_history:
        initializeHistory()
    if args.get_day:
        getDay(args.get_day)
    if args.get_tomorrow:
        getTomorrow()
    if args.analyze:
        analyze()

if __name__ == "__main__":
    main()